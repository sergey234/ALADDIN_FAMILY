"""Отправка маркетинговой рассылки с throttle. Не трогает VPN trial/expiry."""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import Settings
from bot.services import broadcast_repo

_log = logging.getLogger(__name__)

THROTTLE_SEC = 0.05


def broadcast_message_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🔕 Отписаться от акций", callback_data="bc:unsub"))
    return b.as_markup()


def broadcast_mode_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="🧪 Тест себе (dry)", callback_data="bc:run:dry"))
    b.row(InlineKeyboardButton(text="👮 Только админам", callback_data="bc:run:admins"))
    b.row(InlineKeyboardButton(text="👥 Когорта 100", callback_data="bc:run:cohort:100"))
    b.row(InlineKeyboardButton(text="📣 Всем с подпиской на акции", callback_data="bc:run:all"))
    b.row(InlineKeyboardButton(text="❌ Отмена", callback_data="bc:cancel"))
    return b.as_markup()


async def run_broadcast(
    bot: Bot,
    settings: Settings,
    conn,
    *,
    admin_user_id: int,
    mode: str,
    body_html: str,
) -> dict[str, int]:
    await broadcast_repo.ensure_broadcast_schema(conn)
    recipients = await broadcast_repo.list_recipient_ids(
        conn,
        mode=mode,
        admin_ids=settings.parsed_admin_ids(),
        actor_id=admin_user_id,
    )
    bid = await broadcast_repo.create_broadcast(
        conn, admin_user_id=admin_user_id, mode=mode, body_html=body_html
    )
    sent = fail = skip = 0
    kb = broadcast_message_kb()
    text = body_html[:3900]
    for uid in recipients:
        # dry/admins — без фильтра opt-in; cohort/all уже отфильтрованы
        if mode in ("all",) or mode.startswith("cohort:"):
            if not await broadcast_repo.is_marketing_opt_in(conn, uid):
                skip += 1
                await broadcast_repo.log_delivery(
                    conn, broadcast_id=bid, user_id=uid, status="skip"
                )
                continue
        try:
            await bot.send_message(uid, text, reply_markup=kb, disable_web_page_preview=True)
            sent += 1
            await broadcast_repo.log_delivery(
                conn, broadcast_id=bid, user_id=uid, status="sent"
            )
        except TelegramRetryAfter as e:
            await asyncio.sleep(float(e.retry_after) + 0.5)
            try:
                await bot.send_message(uid, text, reply_markup=kb, disable_web_page_preview=True)
                sent += 1
                await broadcast_repo.log_delivery(
                    conn, broadcast_id=bid, user_id=uid, status="sent"
                )
            except Exception as e2:
                fail += 1
                await broadcast_repo.log_delivery(
                    conn, broadcast_id=bid, user_id=uid, status="fail", error=str(e2)[:200]
                )
                _log.warning("broadcast fail after retry uid=%s: %s", uid, e2)
        except Exception as e:
            fail += 1
            await broadcast_repo.log_delivery(
                conn, broadcast_id=bid, user_id=uid, status="fail", error=str(e)[:200]
            )
            _log.warning("broadcast fail uid=%s: %s", uid, e)
        await asyncio.sleep(THROTTLE_SEC)
    await broadcast_repo.finish_broadcast(conn, bid, sent=sent, fail=fail, skip=skip)
    unsub = await broadcast_repo.count_unsubscribed(conn)
    return {
        "broadcast_id": bid,
        "recipients": len(recipients),
        "sent": sent,
        "fail": fail,
        "skip": skip,
        "unsubscribed_total": unsub,
    }
