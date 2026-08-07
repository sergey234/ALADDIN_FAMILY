from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.config import Settings
from bot.services.catalog import Product


class InjectMiddleware(BaseMiddleware):
    def __init__(self, settings: Settings, conn, products: list[Product]) -> None:
        self.settings = settings
        self.conn = conn
        self.products = products

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        data["settings"] = self.settings
        data["conn"] = self.conn
        data["products"] = self.products
        return await handler(event, data)
