"""
Напоминания об окончании платной VPN-подписки.

Окна: d7 / d3 / d1 / h6 / expired (h6 вместо d0).
Loop не реже 15 мин — чтобы ловить часовые окна; day-kinds идемпотентны.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

import aiosqlite
from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter

from bot.config import Settings
from bot.db.database import connect
from bot.services import vpn_expiry_notify_repo
from bot.services.admin_stats_repo import is_friend_seed_tid
from bot.services.vpn_subscription_dates import days_until_expiry
from bot.services.vpn_subscription_notify_ux import (
    KIND_EXPIRED,
    KIND_H6,
    hours_until_expiry,
    message_for_paid_kind,
    paid_kind_for_timing,
    subscription_notify_kb,
)

_log = logging.getLogger(__name__)


def kind_for_days_left(days_left: int | None) -> str | None:
    """Совместимость с тестами: только day-окна (без h6)."""
    return paid_kind_for_timing(days_left=days_left, hours_left=None)


def message_for_kind(*, kind: str, paid_until: str, settings: Settings | None = None) -> str:
    return message_for_paid_kind(kind=kind, paid_until=paid_until, settings=settings)


async def _fetch_vpn_accounts(vpath) -> list[dict]:
    conn = await aiosqlite.connect(vpath)
    conn.row_factory = aiosqlite.Row
    try:
        cur = await conn.execute(
            """
            SELECT telegram_user_id, status, paid_until, trial_used_at, account_kind
            FROM vpn_accounts
            WHERE status IN ('vpn_active', 'vpn_expired')
            """
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        await conn.close()


async def _should_attempt(shop, *, tid: int, kind: str, now: datetime) -> bool:
    if await vpn_expiry_notify_repo.notice_already_sent(shop, telegram_user_id=tid, kind=kind):
        return False
    # pending/failed с attempts < max: шлём только когда next_retry наступил
    cur = await shop.execute(
        "SELECT status FROM vpn_expiry_notices WHERE telegram_user_id = ? AND kind = ?",
        (tid, kind),
    )
    row = await cur.fetchone()
    if row is None:
        return True
    status = str(row[0] or "").strip().lower()
    if status in (
        vpn_expiry_notify_repo.STATUS_PENDING,
        vpn_expiry_notify_repo.STATUS_FAILED,
    ):
        return await vpn_expiry_notify_repo.notice_ready_for_retry(
            shop, telegram_user_id=tid, kind=kind, now=now
        )
    return True


async def _send_one(bot: Bot, shop, *, tid: int, kind: str, text: str, kb) -> bool:
    try:
        await bot.send_message(tid, text, reply_markup=kb)
        await vpn_expiry_notify_repo.mark_notice_sent(shop, telegram_user_id=tid, kind=kind)
        return True
    except TelegramRetryAfter as e:
        await asyncio.sleep(float(e.retry_after) + 0.5)
        try:
            await bot.send_message(tid, text, reply_markup=kb)
            await vpn_expiry_notify_repo.mark_notice_sent(shop, telegram_user_id=tid, kind=kind)
            return True
        except Exception as e2:
            await vpn_expiry_notify_repo.mark_notice_failed(
                shop, telegram_user_id=tid, kind=kind, error=str(e2)
            )
            _log.exception("vpn_expiry_notify: retry failed tid=%s kind=%s", tid, kind)
            return False
    except TelegramForbiddenError as e:
        await vpn_expiry_notify_repo.mark_notice_failed(
            shop, telegram_user_id=tid, kind=kind, error=str(e), blocked=True
        )
        _log.info("vpn_expiry_notify: blocked tid=%s kind=%s", tid, kind)
        return False
    except Exception as e:
        await vpn_expiry_notify_repo.mark_notice_failed(
            shop, telegram_user_id=tid, kind=kind, error=str(e)
        )
        _log.exception("vpn_expiry_notify: send failed tid=%s kind=%s", tid, kind)
        return False


async def run_vpn_expiry_notify_batch(bot: Bot, settings: Settings) -> int:
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
        for acc in await _fetch_vpn_accounts(vpath):
            tid = int(acc["telegram_user_id"])
            if is_friend_seed_tid(tid):
                continue
            status = str(acc.get("status") or "").strip()
            paid = str(acc.get("paid_until") or "")
            kind_acc = str(acc.get("account_kind") or "").strip().lower()

            if status == "vpn_expired":
                if str(acc.get("trial_used_at") or "").strip():
                    continue
                kind = KIND_EXPIRED
            elif status == "vpn_active":
                if kind_acc == "trial":
                    continue
                days = days_until_expiry(paid, now=now)
                hours = hours_until_expiry(paid, now=now)
                kind = paid_kind_for_timing(days_left=days, hours_left=hours)
            else:
                continue

            if not kind:
                continue
            if kind == KIND_H6 and await vpn_expiry_notify_repo.notice_already_sent(
                shop, telegram_user_id=tid, kind="d0"
            ):
                continue
            if not await _should_attempt(shop, tid=tid, kind=kind, now=now):
                continue

            text = message_for_paid_kind(kind=kind, paid_until=paid, settings=settings)
            if not text:
                continue
            kb = subscription_notify_kb(ended=(kind == KIND_EXPIRED))
            if await _send_one(bot, shop, tid=tid, kind=kind, text=text, kb=kb):
                sent_n += 1
    finally:
        await shop.close()

    if sent_n:
        _log.info("vpn_expiry_notify: sent %s message(s)", sent_n)
    return sent_n


def _loop_interval_seconds(settings: Settings) -> int:
    raw = int(settings.vpn_expiry_notify_interval_seconds or 0)
    if raw <= 0:
        return 0
    # h6 нужен ≥15 мин; суточный env (86400) принудительно 900.
    if raw >= 3600:
        return 900
    return max(900, raw)


async def vpn_expiry_notify_loop(bot: Bot, settings: Settings) -> None:
    interval = _loop_interval_seconds(settings)
    if interval <= 0:
        return
    _log.info(
        "vpn_expiry_notify_loop: interval=%ss enabled=%s",
        interval,
        settings.vpn_expiry_notify_enabled,
    )
    while True:
        try:
            await run_vpn_expiry_notify_batch(bot, settings)
        except Exception:
            _log.exception("vpn_expiry_notify_loop")
        await asyncio.sleep(interval)
