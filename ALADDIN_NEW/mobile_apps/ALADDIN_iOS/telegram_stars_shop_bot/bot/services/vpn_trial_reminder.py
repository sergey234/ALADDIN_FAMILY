"""
Напоминания пробного периода AiMonkeyVPN:
  trial_d1      — за ~1 день до конца
  trial_h6      — за ~6 часов (legacy trial_h3/h4 — не дублируем)
  trial_expired — после vpn_expired
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
from bot.services.vpn_subscription_notify_ux import (
    KIND_TRIAL_D1,
    KIND_TRIAL_EXPIRED,
    KIND_TRIAL_H3,
    KIND_TRIAL_H4,
    KIND_TRIAL_H6,
    hours_until_expiry,
    message_for_trial_kind,
    subscription_notify_kb,
    trial_kind_for_hours_left,
)

_log = logging.getLogger(__name__)

# re-exports for tests
__all__ = [
    "KIND_TRIAL_D1",
    "KIND_TRIAL_H3",
    "KIND_TRIAL_H4",
    "KIND_TRIAL_H6",
    "KIND_TRIAL_EXPIRED",
    "hours_until_expiry",
    "trial_kind_for_hours_left",
    "message_for_trial_kind",
    "run_vpn_trial_reminder_batch",
    "vpn_trial_reminder_loop",
]


async def _fetch_trial_accounts(vpath) -> list[dict]:
    conn = await aiosqlite.connect(vpath)
    conn.row_factory = aiosqlite.Row
    try:
        cur = await conn.execute(
            """
            SELECT telegram_user_id, status, paid_until, trial_used_at, account_kind
            FROM vpn_accounts
            WHERE trial_used_at IS NOT NULL AND TRIM(trial_used_at) != ''
            """
        )
        rows = await cur.fetchall()
        return [dict(r) for r in rows]
    finally:
        await conn.close()


async def _should_attempt(shop, *, tid: int, kind: str, now: datetime) -> bool:
    if await vpn_expiry_notify_repo.notice_already_sent(shop, telegram_user_id=tid, kind=kind):
        return False
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
            return False
    except TelegramForbiddenError as e:
        await vpn_expiry_notify_repo.mark_notice_failed(
            shop, telegram_user_id=tid, kind=kind, error=str(e), blocked=True
        )
        return False
    except Exception as e:
        await vpn_expiry_notify_repo.mark_notice_failed(
            shop, telegram_user_id=tid, kind=kind, error=str(e)
        )
        _log.exception("vpn_trial_reminder: send failed tid=%s kind=%s", tid, kind)
        return False


async def run_vpn_trial_reminder_batch(bot: Bot, settings: Settings) -> int:
    if not settings.vpn_trial_enabled:
        return 0
    vpath = settings.resolved_vpn_db_path()
    if vpath is None:
        return 0

    shop = await connect(settings.database_path)
    await vpn_expiry_notify_repo.ensure_vpn_expiry_notices_table(shop)
    sent_n = 0
    now = datetime.now(timezone.utc).replace(microsecond=0)
    kb = subscription_notify_kb()

    try:
        try:
            from bot.services.vpn_trial_repo import sync_trial_request_statuses_from_vpn

            sync_stats = await sync_trial_request_statuses_from_vpn(shop, vpath)
            if any(sync_stats.values()):
                _log.info("vpn_trial_requests sync: %s", sync_stats)
        except Exception:
            _log.exception("vpn_trial_requests sync failed")

        for acc in await _fetch_trial_accounts(vpath):
            tid = int(acc["telegram_user_id"])
            if is_friend_seed_tid(tid):
                continue
            status = str(acc.get("status") or "").strip()
            paid = str(acc.get("paid_until") or "")
            kind: str | None = None
            hours_left: float | None = None

            if status == "vpn_active" and str(acc.get("account_kind") or "").strip().lower() == "trial":
                hours_left = hours_until_expiry(paid, now=now)
                kind = trial_kind_for_hours_left(hours_left)
            elif status == "vpn_expired":
                kind = KIND_TRIAL_EXPIRED

            if not kind:
                continue
            # Не дублировать ~6ч, если уже ушло legacy h3/h4.
            if kind == KIND_TRIAL_H6:
                for legacy in (KIND_TRIAL_H3, KIND_TRIAL_H4):
                    if await vpn_expiry_notify_repo.notice_already_sent(
                        shop, telegram_user_id=tid, kind=legacy
                    ):
                        kind = None
                        break
            if not kind:
                continue
            if not await _should_attempt(shop, tid=tid, kind=kind, now=now):
                continue

            text = message_for_trial_kind(
                kind=kind, paid_until=paid, hours_left=hours_left, settings=settings
            )
            if not text:
                continue
            kb = subscription_notify_kb(ended=(kind == KIND_TRIAL_EXPIRED))
            if await _send_one(bot, shop, tid=tid, kind=kind, text=text, kb=kb):
                sent_n += 1
                if kind == KIND_TRIAL_EXPIRED:
                    try:
                        from bot.services.vpn_trial_repo import mark_trial_expired

                        await mark_trial_expired(shop, telegram_user_id=tid)
                    except Exception:
                        _log.exception("mark_trial_expired tid=%s", tid)
    finally:
        await shop.close()

    # Allowlist 3+7: после trial expire начислить +N и пуш (только очередь).
    try:
        from bot.services.vpn_trial_plus7_reward import process_pending_rewards

        granted = await process_pending_rewards(bot, settings)
        if granted:
            _log.info("vpn_trial_plus7: granted %s reward(s)", granted)
    except Exception:
        _log.exception("vpn_trial_plus7 process_pending_rewards")

    if sent_n:
        _log.info("vpn_trial_reminder: sent %s message(s)", sent_n)
    return sent_n


async def vpn_trial_reminder_loop(bot: Bot, settings: Settings) -> None:
    interval = max(60, int(settings.vpn_trial_reminder_interval_seconds))
    _log.info(
        "vpn_trial_reminder_loop: interval=%ss enabled=%s",
        interval,
        settings.vpn_trial_enabled,
    )
    while True:
        try:
            await run_vpn_trial_reminder_batch(bot, settings)
        except Exception:
            _log.exception("vpn_trial_reminder_loop")
        await asyncio.sleep(interval)
