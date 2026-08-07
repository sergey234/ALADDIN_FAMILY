from __future__ import annotations

import asyncio
import contextlib
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, ErrorEvent

from bot.config import Settings, load_settings
from bot.sentry_util import init_sentry_bot
from bot.db.database import connect
from bot.services.cardlink_api import cardlink_checkout_configured
from bot.services.fiat_checkout import fiat_bc_universal_url_active
from bot.services.ckassa_api import ckassa_checkout_configured
from bot.services.lava_api import lava_checkout_configured
from bot.support_links import telegram_support_base
from bot.handlers import admin as admin_handlers
from bot.handlers import assistant as assistant_handlers
from bot.handlers import broadcast as broadcast_handlers
from bot.handlers import common as common_handlers
from bot.handlers import hub as hub_handlers
from bot.handlers import promo as promo_handlers
from bot.handlers import shop as shop_handlers
from bot.handlers import vpn as vpn_handlers
from bot.middlewares.channel_gate import ChannelGateMiddleware
from bot.middlewares.inject import InjectMiddleware
from bot.middlewares.throttling import ThrottleMiddleware
from bot.logutil import slog
from bot.services.auto_fulfill_startup import log_auto_fulfill_startup_warnings
from bot.services.catalog import load_products
from bot.services.break_glass_monitor import break_glass_report_loop
from bot.services.data_quality_checks import data_quality_checks_loop
from bot.services.exec_report import exec_report_loop
from bot.services.feedback_survey import feedback_survey_loop
from bot.services.vpn_ops_health import vpn_ops_health_loop, vpn_path_digest_loop
from bot.services.istar_order_poller import istar_order_poll_loop
from bot.services.lava_payment_reconcile import lava_payment_reconcile_loop
from bot.services.pending_payment_ttl import pending_payment_ttl_loop
from bot.services.stuck_orders_monitor import stuck_paid_orders_loop
from bot.services.vpn_expiry_notify import vpn_expiry_notify_loop
from bot.services.vpn_device_first_notify import vpn_device_first_notify_loop
from bot.services.vpn_trial_reminder import vpn_trial_reminder_loop
from bot.services.vpn_referral_retry_loop import vpn_referral_api_retry_loop
from bot.util_telegram import is_message_not_modified_error

logger = logging.getLogger(__name__)


def _user_bot_commands(settings: Settings) -> list[BotCommand]:
    commands = [
        BotCommand(command="start", description="Запуск и приветствие"),
        BotCommand(command="menu", description="Главное меню"),
        BotCommand(command="my", description="Личный кабинет"),
        BotCommand(command="orders", description="Мои заказы"),
        BotCommand(command="help_ai", description="AI Помощник AiMonkey"),
    ]
    if settings.ui_show_vpn:
        commands.insert(4, BotCommand(command="vpn", description="AiMonkeyVPN — оплата и настройка"))
        commands.insert(5, BotCommand(command="vpnlink", description="Моя VPN-ссылка /sub/"))
    return commands


def _admin_bot_commands(settings: Settings) -> list[BotCommand]:
    commands = _user_bot_commands(settings)
    commands.extend(
        [
            BotCommand(command="admin", description="Админ-панель"),
            BotCommand(command="admin_help", description="Админ: все команды с расшифровкой"),
            BotCommand(command="vpn_health", description="Админ: VPN health / путь"),
            BotCommand(command="vpn_zombies", description="Админ: живые + зомби RU-bridge"),
            BotCommand(command="admin_vpn_health", description="Админ: VPN health (полный снимок)"),
            BotCommand(command="admin_vpn_zombies", description="Админ: зомби bridge (детали)"),
            BotCommand(command="admqueue", description="Админ: очередь внимания по заказам"),
            BotCommand(command="admdeliveries", description="Админ: последние выдачи"),
            BotCommand(command="admin_recalc_profit", description="Админ: пересчёт прибыли"),
            BotCommand(command="admin_cogs", description="Админ: себестоимость заказа"),
            BotCommand(command="admin_broadcast", description="Админ: рассылка акций"),
            BotCommand(command="contest", description="Админ: конкурсы партнёров"),
        ]
    )
    return commands


def _bot_commands_list(settings: Settings) -> list[BotCommand]:
    """Полный список (для тестов / админ-scope)."""
    return _admin_bot_commands(settings)


async def _setup_bot_commands(bot: Bot, settings: Settings) -> bool:
    """
    Меню ☰: юзерам — без админ-команд; каждому ADMIN_IDS — полный список.
    При деградации Telegram API не валит весь run()/polling.
    """
    from aiogram.types import BotCommandScopeChat, BotCommandScopeDefault

    user_cmds = _user_bot_commands(settings)
    admin_cmds = _admin_bot_commands(settings)
    try:
        await bot.set_my_commands(user_cmds, scope=BotCommandScopeDefault())
        for aid in sorted(settings.parsed_admin_ids()):
            try:
                await bot.set_my_commands(
                    admin_cmds,
                    scope=BotCommandScopeChat(chat_id=int(aid)),
                )
            except Exception as e:
                logger.warning(
                    "set_my_commands admin scope failed chat_id=%s: %s: %s",
                    aid,
                    type(e).__name__,
                    e,
                )
        return True
    except Exception as e:
        logger.warning(
            "set_my_commands failed (continue polling): %s: %s",
            type(e).__name__,
            e,
        )
        return False


async def _retry_bot_commands_later(
    bot: Bot,
    settings: Settings,
    *,
    delay_seconds: float = 120.0,
) -> None:
    """Фоновый retry меню-команд, когда канал к Telegram уже мог ожить."""
    try:
        await asyncio.sleep(max(1.0, float(delay_seconds)))
        ok = await _setup_bot_commands(bot, settings)
        if ok:
            logger.info("set_my_commands retry succeeded after %.0fs", delay_seconds)
        else:
            logger.warning("set_my_commands retry still failed after %.0fs", delay_seconds)
    except asyncio.CancelledError:
        raise
    except Exception as e:
        logger.warning("set_my_commands retry crashed: %s: %s", type(e).__name__, e)


async def run() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = load_settings()
    init_sentry_bot(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment or None,
        traces_sample_rate=settings.sentry_traces_sample_rate,
    )
    if not telegram_support_base(settings):
        logger.warning(
            "SUPPORT_URL and SUPPORT_USERNAME are empty: Telegram support links and prefills are disabled."
        )
    if bool(getattr(settings, "ckassa_enabled", False)) and bool(getattr(settings, "ckassa_test_mode", False)):
        logger.warning(
            "CKASSA_TEST_MODE=true: демо-шлюз и демо-ключи, не для реального приёма. "
            "Прод: CKASSA_TEST_MODE=false, ShopToken/SecKey из ЛК Ckassa, CKASSA_CALLBACK_PUBLIC_URL публичный HTTPS."
        )
    univers = fiat_bc_universal_url_active(settings)
    if (
        not univers
        and not cardlink_checkout_configured(settings)
        and not ckassa_checkout_configured(settings)
        and not lava_checkout_configured(settings)
    ):
        logger.warning(
            "Fiat: не настроены LAVA / Cardlink / Ckassa Shop API / Ckassa BC - "
            "покупатели при «Карта / СБП» увидят текст без кнопки оплаты. Добавьте переменные в shared/.env "
            "(см. telegram_stars_shop_bot/env.example, docs/ML_SYSTEM_HANDOFF_FINAL.md §4)."
        )
    elif lava_checkout_configured(settings):
        logger.info("Fiat: LAVA настроена — основной поток оплаты картой / СБП.")
    elif univers:
        logger.info("Fiat: Ckassa BC URL задан — оплата по универсальной ссылке bc.")
    log_auto_fulfill_startup_warnings(settings)
    conn = await connect(settings.database_path)
    slog(logger, "bot_start", database=str(settings.database_path))
    try:
        from bot.assistant.kb import build_kb

        rebuilt = await build_kb(conn, settings)
        if rebuilt:
            logger.info("assistant KB rebuilt: %s chunks", rebuilt)
    except Exception as e:
        logger.warning("assistant KB build skipped: %s: %s", type(e).__name__, e)
    products = load_products(settings.products_path)
    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    commands_ok = await _setup_bot_commands(bot, settings)
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(InjectMiddleware(settings, conn, products))
    dp.message.middleware(ThrottleMiddleware(settings))
    dp.include_router(common_handlers.router)
    dp.include_router(hub_handlers.router)
    dp.include_router(promo_handlers.router)
    dp.include_router(vpn_handlers.router)
    shop_handlers.router.callback_query.middleware(ChannelGateMiddleware())
    # Shop checkout FSM handlers before assistant text (R16 / as-4-router-order).
    dp.include_router(shop_handlers.router)
    dp.include_router(assistant_handlers.router)
    dp.include_router(broadcast_handlers.router)
    dp.include_router(admin_handlers.router)

    @dp.errors()
    async def _swallow_benign_telegram_errors(event: ErrorEvent) -> bool:
        if is_message_not_modified_error(event.exception):
            return True
        if isinstance(event.exception, TelegramBadRequest):
            logger.debug("telegram_bad_request: %s", event.exception)
        return False

    commands_retry_task: asyncio.Task | None = None
    if not commands_ok:
        commands_retry_task = asyncio.create_task(
            _retry_bot_commands_later(bot, settings, delay_seconds=120.0)
        )
    ttl_task = asyncio.create_task(pending_payment_ttl_loop(bot, settings))
    lava_reconcile_task: asyncio.Task | None = None
    if int(settings.lava_reconcile_interval_seconds) > 0:
        lava_reconcile_task = asyncio.create_task(lava_payment_reconcile_loop(settings))
    vpn_ref_retry_task: asyncio.Task | None = None
    if int(settings.vpn_referral_api_retry_interval_seconds) > 0:
        vpn_ref_retry_task = asyncio.create_task(vpn_referral_api_retry_loop(bot, settings))
    stuck_task: asyncio.Task | None = None
    break_glass_task: asyncio.Task | None = None
    vpn_ops_health_task: asyncio.Task | None = None
    vpn_path_digest_task: asyncio.Task | None = None
    vpn_expiry_notify_task: asyncio.Task | None = None
    vpn_device_first_notify_task: asyncio.Task | None = None
    vpn_trial_reminder_task: asyncio.Task | None = None
    exec_report_task: asyncio.Task | None = None
    feedback_survey_task: asyncio.Task | None = None
    data_quality_task: asyncio.Task | None = None
    istar_poll_task: asyncio.Task | None = None
    if (
        int(settings.stuck_paid_alert_hours) > 0
        or int(settings.stuck_processing_alert_minutes) > 0
        or int(settings.stuck_paid_fast_alert_minutes) > 0
    ):
        stuck_task = asyncio.create_task(stuck_paid_orders_loop(bot, settings))
    if int(settings.break_glass_report_interval_seconds) > 0:
        break_glass_task = asyncio.create_task(break_glass_report_loop(bot, settings))
    if int(settings.vpn_ops_health_interval_seconds) > 0 and (settings.vpn_api_base_url or "").strip():
        vpn_ops_health_task = asyncio.create_task(vpn_ops_health_loop(bot, settings))
    if (
        bool(getattr(settings, "vpn_path_digest_enabled", True))
        and int(getattr(settings, "vpn_path_digest_interval_seconds", 18000) or 0) > 0
        and (settings.vpn_api_base_url or "").strip()
    ):
        vpn_path_digest_task = asyncio.create_task(vpn_path_digest_loop(bot, settings))
    if (
        settings.vpn_expiry_notify_enabled
        and int(settings.vpn_expiry_notify_interval_seconds) > 0
        and settings.resolved_vpn_db_path() is not None
    ):
        vpn_expiry_notify_task = asyncio.create_task(vpn_expiry_notify_loop(bot, settings))
    if (
        settings.vpn_device_first_notify_enabled
        and int(settings.vpn_device_first_notify_interval_seconds) > 0
        and settings.resolved_vpn_db_path() is not None
    ):
        vpn_device_first_notify_task = asyncio.create_task(
            vpn_device_first_notify_loop(bot, settings)
        )
    if (
        settings.vpn_trial_enabled
        and int(settings.vpn_trial_reminder_interval_seconds) > 0
        and settings.resolved_vpn_db_path() is not None
    ):
        vpn_trial_reminder_task = asyncio.create_task(vpn_trial_reminder_loop(bot, settings))
    if settings.exec_report_enabled:
        exec_report_task = asyncio.create_task(exec_report_loop(bot, settings))
    if settings.feedback_survey_enabled and int(settings.feedback_survey_interval_seconds) > 0:
        feedback_survey_task = asyncio.create_task(feedback_survey_loop(bot, settings))
    if settings.data_quality_checks_enabled and int(settings.data_quality_checks_interval_seconds) > 0:
        data_quality_task = asyncio.create_task(data_quality_checks_loop(settings))
    if int(settings.istar_order_poll_interval_seconds) > 0:
        istar_poll_task = asyncio.create_task(istar_order_poll_loop(bot, settings))
    try:
        await dp.start_polling(bot)
    finally:
        if commands_retry_task is not None:
            commands_retry_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await commands_retry_task
        ttl_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await ttl_task
        if lava_reconcile_task is not None:
            lava_reconcile_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await lava_reconcile_task
        if vpn_ref_retry_task is not None:
            vpn_ref_retry_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await vpn_ref_retry_task
        if stuck_task is not None:
            stuck_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await stuck_task
        if break_glass_task is not None:
            break_glass_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await break_glass_task
        if vpn_ops_health_task is not None:
            vpn_ops_health_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await vpn_ops_health_task
        if vpn_path_digest_task is not None:
            vpn_path_digest_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await vpn_path_digest_task
        if vpn_expiry_notify_task is not None:
            vpn_expiry_notify_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await vpn_expiry_notify_task
        if vpn_device_first_notify_task is not None:
            vpn_device_first_notify_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await vpn_device_first_notify_task
        if vpn_trial_reminder_task is not None:
            vpn_trial_reminder_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await vpn_trial_reminder_task
        if exec_report_task is not None:
            exec_report_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await exec_report_task
        if feedback_survey_task is not None:
            feedback_survey_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await feedback_survey_task
        if data_quality_task is not None:
            data_quality_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await data_quality_task
        if istar_poll_task is not None:
            istar_poll_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await istar_poll_task
        await conn.close()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
