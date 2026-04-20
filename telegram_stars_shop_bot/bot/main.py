from __future__ import annotations

import asyncio
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
from bot.middlewares.inject import InjectMiddleware
from bot.middlewares.throttling import ThrottleMiddleware
from bot.logutil import slog
from bot.services.catalog import load_products

logger = logging.getLogger(__name__)


async def _setup_bot_commands(bot: Bot) -> None:
    """
    Показывает кнопку Menu внизу чата и список команд в стиле популярных ботов.
    /menu ведёт к тому же экрану с 10 карточками, что и кнопка «Далее».
    """
    commands = [
        BotCommand(command="start", description="Запуск и приветствие"),
        BotCommand(command="menu", description="Главное меню (10 карточек)"),
        BotCommand(command="my", description="Мой профиль"),
        BotCommand(command="orders", description="Мои заказы"),
        BotCommand(command="admin", description="Админ-панель"),
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
    dp.include_router(shop_handlers.router)
    dp.include_router(admin_handlers.router)
    try:
        await dp.start_polling(bot)
    finally:
        await conn.close()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
