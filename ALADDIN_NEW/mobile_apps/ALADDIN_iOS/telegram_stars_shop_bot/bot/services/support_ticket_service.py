"""Обращения в поддержку внутри бота → assistant_tickets + DM только админам."""

from __future__ import annotations

import logging
from typing import Any

import aiosqlite
from aiogram import Bot

from bot.assistant import repo as as_repo
from bot.assistant.redact import redact_for_log
from bot.config import Settings
from bot.support_links import support_url_is_shop_bot_loop

_log = logging.getLogger(__name__)


def _admin_notify_chat_ids(settings: Settings) -> set[int]:
    out: set[int] = set(settings.parsed_admin_ids())
    raw = (settings.assistant_admin_chat_id or "").strip()
    if raw:
        try:
            out.add(int(raw))
        except ValueError:
            pass
    return out


async def notify_admins_only(bot: Bot, settings: Settings, text: str) -> int:
    """Шлёт текст только в чаты админов / ASSISTANT_ADMIN_CHAT_ID. Обычные юзеры не видят."""
    sent = 0
    body = (text or "")[:3500]
    if not body:
        return 0
    for chat_id in sorted(_admin_notify_chat_ids(settings)):
        try:
            await bot.send_message(chat_id, body)
            sent += 1
        except Exception as e:
            _log.warning("support_admin_notify_failed chat=%s: %s", chat_id, e)
    return sent


async def open_inbot_support_ticket(
    conn: aiosqlite.Connection,
    settings: Settings,
    *,
    bot: Bot,
    telegram_user_id: int,
    username: str | None,
    text: str,
    reason: str = "esc.support_menu",
) -> dict[str, Any]:
    """
    Создаёт тикет в shop.db (assistant_tickets) и уведомляет только админов.
    Не пишет в общий канал и не открывает URL на сам shop-бот.
    """
    clean = redact_for_log((text or "").strip(), max_len=1500)
    if not clean:
        return {"ok": False, "error": "empty"}

    limit = int(getattr(settings, "assistant_ticket_daily_limit", 5) or 5)
    used = await as_repo.count_tickets_today(conn, telegram_user_id)
    if used >= limit:
        return {
            "ok": False,
            "error": "ticket_daily_limit",
            "used_today": used,
            "limit": limit,
        }

    session_id = await as_repo.get_or_create_session(
        conn,
        int(telegram_user_id),
        ttl_min=int(settings.assistant_session_ttl_min or 30),
        max_turns=int(settings.assistant_session_max_turns or 20),
    )
    tid = await as_repo.create_ticket(
        conn,
        user_id=int(telegram_user_id),
        session_id=session_id,
        reason_code=reason,
        summary=clean,
        urgency="normal",
        meta={"username": username or "", "via": "support_menu"},
    )

    uname = f" @{username}" if username else ""
    admin_msg = (
        f"🛟 Обращение из «Поддержка» #{tid}\n"
        f"user={telegram_user_id}{uname}\n"
        f"{clean[:800]}"
    )
    n = await notify_admins_only(bot, settings, admin_msg)
    _log.info(
        "inbot_support_ticket id=%s user=%s admins_notified=%s loop_url=%s",
        tid,
        telegram_user_id,
        n,
        support_url_is_shop_bot_loop(settings),
    )
    return {"ok": True, "ticket_id": tid, "admins_notified": n}
