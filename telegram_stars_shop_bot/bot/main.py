from __future__ import annotations

import asyncio
import contextlib
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.config import load_settings
from bot.sentry_util import init_sentry_bot
from bot.db.database import connect
from bot.support_links import telegram_support_base
from bot.handlers import admin as admin_handlers
from bot.handlers import common as common_handlers
from bot.handlers import hub as hub_handlers
from bot.handlers import shop as shop_handlers
from bot.middlewares.channel_gate import ChannelGateMiddleware
from bot.middlewares.inject import InjectMiddleware
from bot.middlewares.throttling import ThrottleMiddleware
from bot.logutil import slog
from bot.services.catalog import load_products
from bot.services.break_glass_monitor import break_glass_report_loop
from bot.services.pending_payment_ttl import pending_payment_ttl_loop
from bot.services.stuck_orders_monitor import stuck_paid_orders_loop

logger = logging.getLogger(__name__)


async def _setup_bot_commands(bot: Bot) -> None:
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
    conn = await connect(settings.database_path)
    slog(logger, "bot_start", database=str(settings.database_path))
    products = load_products(settings.products_path)
    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await _setup_bot_commands(bot)
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(InjectMiddleware(settings, conn, products))
    dp.message.middleware(ThrottleMiddleware(settings))
    dp.include_router(common_handlers.router)
    dp.include_router(hub_handlers.router)
    shop_handlers.router.callback_query.middleware(ChannelGateMiddleware())
    dp.include_router(shop_handlers.router)
    dp.include_router(admin_handlers.router)
    ttl_task = asyncio.create_task(pending_payment_ttl_loop(bot, settings))
    stuck_task: asyncio.Task | None = None
    break_glass_task: asyncio.Task | None = None
    if int(settings.stuck_paid_alert_hours) > 0 or int(settings.stuck_processing_alert_minutes) > 0:
        stuck_task = asyncio.create_task(stuck_paid_orders_loop(bot, settings))
    if int(settings.break_glass_report_interval_seconds) > 0:
        break_glass_task = asyncio.create_task(break_glass_report_loop(bot, settings))
    try:
        await dp.start_polling(bot)
    finally:
        ttl_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await ttl_task
        if stuck_task is not None:
            stuck_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await stuck_task
        if break_glass_task is not None:
            break_glass_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await break_glass_task
        await conn.close()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
