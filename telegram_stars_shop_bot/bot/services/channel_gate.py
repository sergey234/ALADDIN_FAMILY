from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    ChatMemberAdministrator,
    ChatMemberMember,
    ChatMemberOwner,
    ChatMemberRestricted,
)

from bot.config import Settings

_log = logging.getLogger(__name__)


def channel_gate_enabled(settings: Settings) -> bool:
    return bool((settings.required_channel_id or "").strip())


def normalized_channel_id(settings: Settings) -> str | None:
    raw = (settings.required_channel_id or "").strip()
    return raw or None


async def user_is_channel_member(bot: Bot, settings: Settings, user_id: int) -> bool:
    if not channel_gate_enabled(settings):
        return True
    chat_id = normalized_channel_id(settings)
    if not chat_id:
        return True
    try:
        member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
    except TelegramBadRequest as e:
        _log.warning("get_chat_member failed chat=%s user=%s: %s", chat_id, user_id, e)
        return False
    except Exception:
        _log.exception("get_chat_member unexpected chat=%s user=%s", chat_id, user_id)
        return False

    if isinstance(member, (ChatMemberMember, ChatMemberAdministrator, ChatMemberOwner)):
        return True
    if isinstance(member, ChatMemberRestricted):
        return bool(member.is_member)
    return False
