"""
Ежедневные напоминания об окончании VPN-подписки (1 прогон в сутки из main).

Окна: за 7 / 3 / 1 день, в день окончания, после vpn_expired.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

import aiosqlite
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.brand_constants import VPN_PRODUCT_NAME
from bot.config import Settings
from bot.db.database import connect
from bot.services import vpn_expiry_notify_repo
from bot.services.vpn_connect_copy import vpn_payment_button_label
from bot.services.vpn_subscription_dates import days_until_expiry, parse_paid_until_utc
from bot.util_html import esc

_log = logging.getLogger(__name__)

_KINDS_ACTIVE = ("d7", "d3", "d1", "d0")
_KIND_EXPIRED = "expired"


def _notify_kb() -> InlineKeyboardMarkup:
    pay = vpn_payment_button_label()
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=pay, callback_data="nav:vpn")],
            [InlineKeyboardButton(text=f"🌐 {VPN_PRODUCT_NAME}", callback_data="nav:vpn")],
            [
                InlineKeyboardButton(
                    text="🧪 Проверить VPN",
                    callback_data="vpn:check",
                )
            ],
        ]
    )


def _format_until_short(paid_until: str) -> str:
    dt = parse_paid_until_utc(paid_until)
    if dt is None:
        return "—"
    return dt.strftime("%d.%m.%Y")


def message_for_kind(*, kind: str, paid_until: str) -> str:
    p = esc(VPN_PRODUCT_NAME)
    until = esc(_format_until_short(paid_until))
    pay = esc(vpn_payment_button_label())

    if kind == "d7":
        return (
            f"<b>⏳ {p}</b>\n\n"
            f"Подписка активна до <b>{until}</b> (осталось около 7 дней).\n"
            "После этой даты VPN отключится; запасная ссылка в <b>Happ</b> перестанет обновляться.\n\n"
            f"Продлить: {pay} → выберите срок (30 / 90 / … дней)."
        )
    if kind == "d3":
        return (
            f"<b>⏳ {p}</b>\n\n"
            f"До конца подписки около <b>3 дней</b> (до {until}).\n"
            f"Продлить заранее: {pay}."
        )
    if kind == "d1":
        return (
            f"<b>⏳ {p}</b>\n\n"
            f"Завтра заканчивается срок (до {until}).\n"
            "После даты VPN отключится. Если не продлите — удалите старый профиль в "
            "<b>Happ</b> (запасной способ) и при необходимости туннель в <b>WireGuard</b>.\n\n"
            f"Продлить: {pay}."
        )
    if kind == "d0":
        return (
            f"<b>⏳ {p}</b>\n\n"
            f"<b>Сегодня последний день</b> подписки (до {until}).\n"
            f"Продлите, чтобы VPN не отключился: {pay}."
        )
    if kind == _KIND_EXPIRED:
        return (
            f"<b>{p}</b>\n\n"
            "Срок подписки <b>истёк</b> — VPN отключён.\n"
            "Удалите старый профиль в <b>Happ</b>; в <b>WireGuard</b> — старый туннель "
            "(после продления запросите новый 📥 или 📷 в боте).\n\n"
            f"Продлить: {pay}."
        )
    return ""


def kind_for_days_left(days_left: int | None) -> str | None:
    if days_left is None:
        return None
    if days_left == 7:
        return "d7"
    if days_left == 3:
        return "d3"
    if days_left == 1:
        return "d1"
    if days_left == 0:
        return "d0"
    return None


async def _fetch_vpn_accounts(vpath) -> list[dict]:
    conn = await aiosqlite.connect(vpath)
    conn.row_factory = aiosqlite.Row
    try:
        cur = await conn.execute(
            """
            SELECT telegram_user_id, status, paid_until
            FROM vpn_accounts
            WHERE status IN ('vpn_active', 'vpn_expired')
            """
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        await conn.close()


async def run_vpn_expiry_notify_batch(bot: Bot, settings: Settings) -> int:
    """Один проход. Возвращает число отправленных сообщений."""
    if not settings.vpn_expiry_notify_enabled:
        return 0
    vpath = settings.resolved_vpn_db_path()
    if vpath is None:
        return 0

    shop = await connect(settings.database_path)
    await vpn_expiry_notify_repo.ensure_vpn_expiry_notices_table(shop)
    sent_n = 0
    now = datetime.now(timezone.utc).replace(microsecond=0)

    try:
        accounts = await _fetch_vpn_accounts(vpath)
        kb = _notify_kb()
        for acc in accounts:
            tid = int(acc["telegram_user_id"])
            status = str(acc.get("status") or "").strip()
            paid = str(acc.get("paid_until") or "")

            if status == "vpn_expired":
                kind = _KIND_EXPIRED
            elif status == "vpn_active":
                kind = kind_for_days_left(days_until_expiry(paid, now=now))
            else:
                continue

            if not kind:
                continue
            if await vpn_expiry_notify_repo.notice_already_sent(shop, telegram_user_id=tid, kind=kind):
                continue

            text = message_for_kind(kind=kind, paid_until=paid)
            if not text:
                continue
            try:
                await bot.send_message(tid, text, reply_markup=kb)
                await vpn_expiry_notify_repo.mark_notice_sent(shop, telegram_user_id=tid, kind=kind)
                sent_n += 1
            except Exception:
                _log.exception("vpn_expiry_notify: send failed tid=%s kind=%s", tid, kind)
    finally:
        await shop.close()

    if sent_n:
        _log.info("vpn_expiry_notify: sent %s message(s)", sent_n)
    return sent_n


async def vpn_expiry_notify_loop(bot: Bot, settings: Settings) -> None:
    interval = max(3600, int(settings.vpn_expiry_notify_interval_seconds))
    _log.info("vpn_expiry_notify_loop: interval=%ss enabled=%s", interval, settings.vpn_expiry_notify_enabled)
    while True:
        try:
            await run_vpn_expiry_notify_batch(bot, settings)
        except Exception:
            _log.exception("vpn_expiry_notify_loop")
        await asyncio.sleep(interval)
