from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject

from bot.config import Settings
from bot.services.channel_gate import channel_gate_enabled, user_is_channel_member


def _callback_requires_channel(data: str | None) -> bool:
    if not data:
        return False
    if data == "order:submit":
        return True
    prefixes = ("buy:", "prem:", "pay:", "nav:buy_stars", "nav:premium", "nav:gifts")
    return any(data.startswith(p) for p in prefixes)


class ChannelGateMiddleware(BaseMiddleware):
    """Блокирует оформление покупки, пока пользователь не в канале (если задан REQUIRED_CHANNEL_ID)."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, CallbackQuery) or not event.from_user:
            return await handler(event, data)
        settings: Settings | None = data.get("settings")
        if settings is None or not channel_gate_enabled(settings):
            return await handler(event, data)
        if not _callback_requires_channel(event.data):
            return await handler(event, data)
        bot = data.get("bot") or event.bot
        ok = await user_is_channel_member(bot, settings, event.from_user.id)
        if ok:
            return await handler(event, data)
        await event.answer(
            "Чтобы покупать Stars / Premium / подарки, подпишитесь на канал магазина (кнопка на первом экране).",
            show_alert=True,
        )
        return None
