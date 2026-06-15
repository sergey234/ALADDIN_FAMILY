from __future__ import annotations

import asyncio
import contextlib
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.config import Settings, load_settings
from bot.sentry_util import init_sentry_bot
from bot.db.database import connect
from bot.services.cardlink_api import cardlink_checkout_configured
from bot.services.ckassa_api import ckassa_checkout_configured
from bot.services.lava_api import lava_checkout_configured
from bot.support_links import telegram_support_base
from bot.handlers import admin as admin_handlers
from bot.handlers import common as common_handlers
from bot.handlers import hub as hub_handlers
from bot.handlers import shop as shop_handlers
from bot.handlers import vpn as vpn_handlers
from bot.middlewares.channel_gate import ChannelGateMiddleware
from bot.middlewares.inject import InjectMiddleware
from bot.middlewares.throttling import ThrottleMiddleware
from bot.logutil import slog
from bot.services.catalog import load_products
from bot.services.break_glass_monitor import break_glass_report_loop
from bot.services.data_quality_checks import data_quality_checks_loop
from bot.services.exec_report import exec_report_loop
from bot.services.feedback_survey import feedback_survey_loop
from bot.services.vpn_ops_health import vpn_ops_health_loop
from bot.services.pending_payment_ttl import pending_payment_ttl_loop
from bot.services.stuck_orders_monitor import stuck_paid_orders_loop
from bot.services.vpn_expiry_notify import vpn_expiry_notify_loop
from bot.services.vpn_referral_retry_loop import vpn_referral_api_retry_loop

logger = logging.getLogger(__name__)


async def _setup_bot_commands(bot: Bot, settings: Settings) -> None:
    """
    Показывает кнопку Menu внизу чата и список команд в стиле популярных ботов.
    /menu ведёт к тому же экрану с 10 карточками, что и кнопка «Далее».
    """
    commands = [
        BotCommand(command="start", description="Запуск и приветствие"),
        BotCommand(command="menu", description="Главное меню (после подписки на канал)"),
        BotCommand(command="my", description="Мой профиль"),
        BotCommand(command="orders", description="Мои заказы"),
        BotCommand(command="admin", description="Админ-панель"),
        BotCommand(command="admqueue", description="Админ: очередь внимания по заказам"),
        BotCommand(command="contest", description="Админ: конкурсы партнёров"),
    ]
    if settings.ui_show_vpn:
        commands.insert(4, BotCommand(command="vpn", description="AiMonkeyVPN — оплата и настройка"))
    await bot.set_my_commands(commands)


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
    univers = (getattr(settings, "ckassa_bc_universal_payment_url", "") or "").strip()
    if (
        not univers
        and not cardlink_checkout_configured(settings)
        and not ckassa_checkout_configured(settings)
        and not lava_checkout_configured(settings)
    ):
        logger.warning(
            "Fiat: не задана CKASSA_BC_UNIVERSAL_PAYMENT_URL и не настроены Cardlink / Ckassa Shop API / LAVA - "
            "покупатели при «Карта / СБП» увидят текст без кнопки оплаты. Добавьте переменные в shared/.env "
            "(см. telegram_stars_shop_bot/env.example, docs/ML_SYSTEM_HANDOFF_FINAL.md §4)."
        )
    elif univers:
        logger.info("Fiat: CKASSA_BC_UNIVERSAL_PAYMENT_URL задан - кнопка оплаты по ссылке bc доступна при оформлении.")
    conn = await connect(settings.database_path)
    slog(logger, "bot_start", database=str(settings.database_path))
    products = load_products(settings.products_path)
    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await _setup_bot_commands(bot, settings)
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(InjectMiddleware(settings, conn, products))
    dp.message.middleware(ThrottleMiddleware(settings))
    dp.include_router(common_handlers.router)
    dp.include_router(hub_handlers.router)
    dp.include_router(vpn_handlers.router)
    shop_handlers.router.callback_query.middleware(ChannelGateMiddleware())
    dp.include_router(shop_handlers.router)
    dp.include_router(admin_handlers.router)
    ttl_task = asyncio.create_task(pending_payment_ttl_loop(bot, settings))
    vpn_ref_retry_task: asyncio.Task | None = None
    if int(settings.vpn_referral_api_retry_interval_seconds) > 0:
        vpn_ref_retry_task = asyncio.create_task(vpn_referral_api_retry_loop(bot, settings))
    stuck_task: asyncio.Task | None = None
    break_glass_task: asyncio.Task | None = None
    vpn_ops_health_task: asyncio.Task | None = None
    vpn_expiry_notify_task: asyncio.Task | None = None
    exec_report_task: asyncio.Task | None = None
    feedback_survey_task: asyncio.Task | None = None
    data_quality_task: asyncio.Task | None = None
    if int(settings.stuck_paid_alert_hours) > 0 or int(settings.stuck_processing_alert_minutes) > 0:
        stuck_task = asyncio.create_task(stuck_paid_orders_loop(bot, settings))
    if int(settings.break_glass_report_interval_seconds) > 0:
        break_glass_task = asyncio.create_task(break_glass_report_loop(bot, settings))
    if int(settings.vpn_ops_health_interval_seconds) > 0 and (settings.vpn_api_base_url or "").strip():
        vpn_ops_health_task = asyncio.create_task(vpn_ops_health_loop(bot, settings))
    if (
        settings.vpn_expiry_notify_enabled
        and int(settings.vpn_expiry_notify_interval_seconds) > 0
        and settings.resolved_vpn_db_path() is not None
    ):
        vpn_expiry_notify_task = asyncio.create_task(vpn_expiry_notify_loop(bot, settings))
    if settings.exec_report_enabled and int(settings.exec_report_interval_seconds) > 0:
        exec_report_task = asyncio.create_task(exec_report_loop(bot, settings))
    if settings.feedback_survey_enabled and int(settings.feedback_survey_interval_seconds) > 0:
        feedback_survey_task = asyncio.create_task(feedback_survey_loop(bot, settings))
    if settings.data_quality_checks_enabled and int(settings.data_quality_checks_interval_seconds) > 0:
        data_quality_task = asyncio.create_task(data_quality_checks_loop(settings))
    try:
        await dp.start_polling(bot)
    finally:
        ttl_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await ttl_task
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
        if vpn_expiry_notify_task is not None:
            vpn_expiry_notify_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await vpn_expiry_notify_task
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
        await conn.close()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
