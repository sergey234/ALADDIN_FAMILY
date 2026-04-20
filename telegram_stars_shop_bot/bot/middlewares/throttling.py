from __future__ import annotations

import time
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from bot.config import Settings


class ThrottleMiddleware(BaseMiddleware):
    """Простой антифлуд: не чаще N сообщений в секунду на пользователя."""

    def __init__(self, settings: Settings, *, per_user_seconds: float = 0.6) -> None:
        self._admins = settings.parsed_admin_ids()
        self._interval = per_user_seconds
        self._last: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            uid = event.from_user.id
            if uid not in self._admins:
                now = time.monotonic()
                prev = self._last.get(uid, 0.0)
                if now - prev < self._interval:
                    return None
                self._last[uid] = now
        return await handler(event, data)
