"""Отложенное вознаграждение +N дней после trial — только allowlist TID.

Фаза 1: обычный trial (уведомления trial_*).
Фаза 2: после vpn_expired — add-subscription-days(+reward_days), пуш «в подарок»,
далее платные напоминания (d3/d1/h6/expired) до финального отключения.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from aiogram import Bot

from bot.config import Settings
from bot.services import vpn_api_client, vpn_expiry_notify_repo
from bot.services.vpn_referral_notify import message_paid_friend
from bot.services.buyer_order_notify import schedule_buyer_html

_log = logging.getLogger(__name__)

DEFAULT_QUEUE_PATH = Path("/opt/aladdin-shop-vpn-api/var/vpn_trial_plus7_queue.json")
STATUS_PENDING = "pending_reward"
STATUS_GRANTED = "reward_granted"
STATUS_DONE = "done"


def _queue_path(settings: Settings) -> Path:
    raw = (getattr(settings, "vpn_trial_plus7_queue_path", None) or "").strip()
    return Path(raw) if raw else DEFAULT_QUEUE_PATH


def load_queue(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"items": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        _log.exception("vpn_trial_plus7: bad queue file %s", path)
        return {"items": []}
    if not isinstance(data, dict):
        return {"items": []}
    items = data.get("items")
    if not isinstance(items, list):
        data["items"] = []
    return data


def save_queue(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def enroll(
    path: Path,
    *,
    telegram_user_id: int,
    reward_days: int = 7,
    note: str = "",
) -> dict[str, Any]:
    data = load_queue(path)
    tid = int(telegram_user_id)
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    items: list[dict[str, Any]] = list(data.get("items") or [])
    for it in items:
        if int(it.get("telegram_user_id") or 0) == tid and str(it.get("status") or "") == STATUS_PENDING:
            it["reward_days"] = int(reward_days)
            it["enrolled_at_utc"] = now
            if note:
                it["note"] = note
            save_queue(path, data)
            return it
    item = {
        "telegram_user_id": tid,
        "reward_days": int(reward_days),
        "status": STATUS_PENDING,
        "enrolled_at_utc": now,
        "note": note or "ops 3+7 test",
    }
    items.append(item)
    data["items"] = items
    save_queue(path, data)
    return item


async def process_pending_rewards(bot: Bot, settings: Settings) -> int:
    """После trial expire: +reward_days и пуш. Возвращает число выдач."""
    path = _queue_path(settings)
    data = load_queue(path)
    items: list[dict[str, Any]] = list(data.get("items") or [])
    if not items:
        return 0

    vpath = settings.resolved_vpn_db_path()
    if vpath is None:
        return 0

    import aiosqlite

    granted_n = 0
    changed = False
    now = datetime.now(timezone.utc).replace(microsecond=0)

    async with aiosqlite.connect(vpath) as vdb:
        vdb.row_factory = aiosqlite.Row
        for it in items:
            if str(it.get("status") or "") != STATUS_PENDING:
                continue
            tid = int(it.get("telegram_user_id") or 0)
            days = int(it.get("reward_days") or 7)
            if tid <= 0 or days <= 0:
                continue
            cur = await vdb.execute(
                """
                SELECT status, account_kind, paid_until, trial_used_at
                FROM vpn_accounts WHERE telegram_user_id = ?
                """,
                (tid,),
            )
            row = await cur.fetchone()
            if row is None:
                continue
            status = str(row["status"] or "").strip()
            kind = str(row["account_kind"] or "").strip().lower()
            # Ждём штатного expire trial (worker → vpn_expired).
            if status != "vpn_expired" or kind != "trial":
                continue

            order_id = 9_200_000_000 + tid
            ok, msg = await vpn_api_client.post_add_subscription_days(
                settings,
                telegram_user_id=tid,
                order_id=order_id,
                days=days,
                reason="vpn_trial_plus7_reward",
                idempotency_key=f"shop-vpn-trial-plus7:{tid}:{it.get('enrolled_at_utc')}",
            )
            if not ok:
                _log.warning("vpn_trial_plus7: extend failed tid=%s: %s", tid, msg)
                it["last_error"] = str(msg)[:300]
                changed = True
                continue

            # Сброс paid-reminders, чтобы d3/d1/h6/expired прошли по новому сроку.
            from bot.db.database import connect as shop_connect

            shop = await shop_connect(settings.database_path)
            try:
                await vpn_expiry_notify_repo.ensure_vpn_expiry_notices_table(shop)
                await vpn_expiry_notify_repo.clear_notices_for_user(shop, telegram_user_id=tid)
            finally:
                await shop.close()

            reward_html = message_paid_friend(days)
            try:
                await bot.send_message(tid, reward_html)
            except Exception as e:
                _log.exception("vpn_trial_plus7: reward push failed tid=%s", tid)
                schedule_buyer_html(settings, tid, reward_html)
                it["push_error"] = str(e)[:200]

            it["status"] = STATUS_GRANTED
            it["granted_at_utc"] = now.isoformat()
            it["last_error"] = None
            granted_n += 1
            changed = True
            _log.info("vpn_trial_plus7: granted +%sd tid=%s", days, tid)

    if changed:
        save_queue(path, data)
    return granted_n
