"""
d10: пуш пользователю при первом успешном /sub устройства.

Опрос vpn.db (как expiry-notify): слоты с first_connected_at, дедуп в shop.db.
Только свежие подключения (окно lookback), чтобы не спамить историю при первом деплое.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

import aiosqlite
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.config import Settings
from bot.db.database import connect
from bot.services import vpn_device_first_notify_repo
from bot.services.admin_stats_repo import is_friend_seed_tid
from bot.util_html import esc

_log = logging.getLogger(__name__)


def device_first_connect_html(*, display_name: str) -> str:
    name = esc((display_name or "").strip() or "Устройство")
    return (
        f"🔔 <b>Новое устройство подключилось:</b> {name}\n\n"
        "Управлять ссылкой и именем можно в разделе «Мои устройства»."
    )


def device_first_connect_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📱 Мои устройства", callback_data="vpn:devices")],
            [InlineKeyboardButton(text="🌐 VPN", callback_data="nav:vpn")],
        ]
    )


def _parse_iso(raw: str | None) -> datetime | None:
    s = (raw or "").strip()
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


async def _list_recent_first_connected_slots(
    vpn_db: Path, *, lookback: timedelta
) -> list[dict]:
    cutoff = datetime.now(timezone.utc) - lookback
    async with aiosqlite.connect(vpn_db) as db:
        db.row_factory = aiosqlite.Row
        cur = await db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='vpn_device_slots'"
        )
        if await cur.fetchone() is None:
            return []
        cur = await db.execute(
            """
            SELECT id, telegram_user_id, display_name, device_kind, first_connected_at
            FROM vpn_device_slots
            WHERE revoked_at IS NULL
              AND first_connected_at IS NOT NULL
            ORDER BY first_connected_at DESC
            LIMIT 200
            """
        )
        rows = await cur.fetchall()
        out: list[dict] = []
        for r in rows:
            connected = _parse_iso(str(r["first_connected_at"] or ""))
            if connected is None:
                continue
            if connected.tzinfo is None:
                connected = connected.replace(tzinfo=timezone.utc)
            if connected < cutoff:
                continue
            kind = str(r["device_kind"] or "unknown")
            name = (r["display_name"] or "").strip()
            if not name:
                name = {
                    "iphone": "iPhone",
                    "android": "Android",
                    "tablet": "Планшет",
                    "laptop": "Ноутбук",
                    "desktop": "Компьютер",
                }.get(kind, "Устройство")
            out.append(
                {
                    "slot_id": int(r["id"]),
                    "telegram_user_id": int(r["telegram_user_id"] or 0),
                    "display_name": name,
                }
            )
        return out


async def run_device_first_notify_batch(bot: Bot, settings: Settings) -> int:
    if not settings.vpn_device_first_notify_enabled:
        return 0
    vpath = settings.resolved_vpn_db_path()
    if vpath is None or not vpath.is_file():
        return 0
    # Lookback ≥ 2 poll intervals so a slow cycle still catches the event.
    interval = max(30, int(settings.vpn_device_first_notify_interval_seconds or 60))
    lookback = timedelta(seconds=max(300, interval * 3))
    shop = await connect(settings.database_path)
    sent_n = 0
    try:
        await vpn_device_first_notify_repo.ensure_device_first_notices_table(shop)
        slots = await _list_recent_first_connected_slots(vpath, lookback=lookback)
        for s in slots:
            tid = int(s["telegram_user_id"])
            slot_id = int(s["slot_id"])
            if tid <= 0 or is_friend_seed_tid(tid):
                continue
            if await vpn_device_first_notify_repo.notice_already_sent(shop, slot_id=slot_id):
                continue
            html = device_first_connect_html(display_name=str(s["display_name"]))
            try:
                await bot.send_message(
                    tid,
                    html,
                    reply_markup=device_first_connect_kb(),
                    disable_web_page_preview=True,
                )
                await vpn_device_first_notify_repo.mark_notice_sent(
                    shop, slot_id=slot_id, telegram_user_id=tid
                )
                sent_n += 1
            except Exception:
                _log.exception(
                    "vpn_device_first_notify: send failed tid=%s slot=%s", tid, slot_id
                )
        if sent_n:
            _log.info("vpn_device_first_notify: sent %s message(s)", sent_n)
        return sent_n
    finally:
        await shop.close()


async def vpn_device_first_notify_loop(bot: Bot, settings: Settings) -> None:
    interval = max(30, int(settings.vpn_device_first_notify_interval_seconds))
    _log.info(
        "vpn_device_first_notify_loop: interval=%ss enabled=%s",
        interval,
        settings.vpn_device_first_notify_enabled,
    )
    while True:
        try:
            await run_device_first_notify_batch(bot, settings)
        except Exception:
            _log.exception("vpn_device_first_notify_loop")
        await asyncio.sleep(interval)
