"""Family Invite Pro — ledger + apply helpers (SQLAlchemy text).

Канон: docs/REFERRAL_FAMILY_A_PRODUCT_LOCK.md
Таблица: family_referral_ledger (см. docs/server/FAMILY_REFERRAL_A_LEDGER.sql)
"""

from __future__ import annotations

import hashlib
import logging
from typing import Any, Optional, TYPE_CHECKING

from app.services.family_referral_a import QualifyInput, evaluate_qualify, tier_for_qualified_count

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

_ENSURED = False


def _sa_text():
    from sqlalchemy import text

    return text


def ensure_ledger_table(db: "Session") -> None:
    """Idempotent DDL for environments where migration SQL not yet applied."""
    global _ENSURED
    if _ENSURED:
        return
    try:
        db.execute(
            _sa_text()(
                """
                CREATE TABLE IF NOT EXISTS family_referral_ledger (
                    id SERIAL PRIMARY KEY,
                    referrer_user_id INTEGER NOT NULL,
                    friend_user_id INTEGER NOT NULL,
                    referrer_family_id VARCHAR(64) NOT NULL,
                    friend_family_id VARCHAR(64) NOT NULL,
                    referral_code VARCHAR(32),
                    status VARCHAR(24) NOT NULL DEFAULT 'granted',
                    reason VARCHAR(64) NOT NULL,
                    friend_discount_percent INTEGER NOT NULL DEFAULT 20,
                    referrer_protection_days INTEGER NOT NULL DEFAULT 0,
                    tier VARCHAR(24),
                    device_soft_hash VARCHAR(64),
                    created_at TIMESTAMP DEFAULT NOW(),
                    CONSTRAINT family_referral_ledger_pair UNIQUE (referrer_family_id, friend_family_id)
                )
                """
            )
        )
        db.commit()
        _ENSURED = True
    except Exception as e:
        db.rollback()
        logger.warning("ensure_ledger_table: %s", e)


def soft_device_hash(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    return hashlib.sha256(raw.strip().encode("utf-8")).hexdigest()[:32]


def pair_already_rewarded(db: "Session", referrer_family_id: str, friend_family_id: str) -> bool:
    ensure_ledger_table(db)
    try:
        row = db.execute(
            _sa_text()(
                """
                SELECT 1 FROM family_referral_ledger
                WHERE referrer_family_id = :a AND friend_family_id = :b
                  AND status = 'granted'
                LIMIT 1
                """
            ),
            {"a": referrer_family_id, "b": friend_family_id},
        ).fetchone()
        return row is not None
    except Exception as e:
        logger.warning("pair_already_rewarded: %s", e)
        return False


def count_granted_for_referrer_family(db: "Session", referrer_family_id: str) -> int:
    ensure_ledger_table(db)
    try:
        n = db.execute(
            _sa_text()(
                """
                SELECT COUNT(*) FROM family_referral_ledger
                WHERE referrer_family_id = :fid AND status = 'granted'
                """
            ),
            {"fid": referrer_family_id},
        ).scalar()
        return int(n or 0)
    except Exception as e:
        logger.warning("count_granted_for_referrer_family: %s", e)
        return 0


def list_ledger_for_user(db: "Session", user_id: int, *, limit: int = 50) -> list[dict[str, Any]]:
    ensure_ledger_table(db)
    try:
        rows = db.execute(
            _sa_text()(
                """
                SELECT id, referrer_user_id, friend_user_id, referrer_family_id, friend_family_id,
                       referral_code, status, reason, friend_discount_percent,
                       referrer_protection_days, tier, created_at
                FROM family_referral_ledger
                WHERE referrer_user_id = :uid OR friend_user_id = :uid
                ORDER BY created_at DESC
                LIMIT :lim
                """
            ),
            {"uid": int(user_id), "lim": int(limit)},
        ).fetchall()
        out: list[dict[str, Any]] = []
        for r in rows:
            out.append(
                {
                    "id": str(r[0]),
                    "referrer_user_id": int(r[1]),
                    "friend_user_id": int(r[2]),
                    "referrer_family_id": r[3],
                    "friend_family_id": r[4],
                    "referral_code": r[5],
                    "status": r[6],
                    "reason": r[7],
                    "friend_discount_percent": int(r[8] or 0),
                    "referrer_protection_days": int(r[9] or 0),
                    "tier": r[10],
                    "created_at": r[11].isoformat() if r[11] else None,
                }
            )
        return out
    except Exception as e:
        logger.warning("list_ledger_for_user: %s", e)
        return []


def apply_family_referral_a(
    db: "Session",
    *,
    referrer_user_id: int,
    friend_user_id: int,
    referrer_family_id: str,
    friend_family_id: str,
    referral_code: Optional[str],
    referrer_has_active_tariff: bool,
    friend_has_paid: bool,
    friend_active_protection_days: int,
    device_raw: Optional[str] = None,
) -> dict[str, Any]:
    """Evaluate + insert ledger row. Idempotent on pair unique constraint."""
    ensure_ledger_table(db)
    already = pair_already_rewarded(db, referrer_family_id, friend_family_id)
    before = count_granted_for_referrer_family(db, referrer_family_id)
    result = evaluate_qualify(
        QualifyInput(
            referrer_family_id=referrer_family_id,
            friend_family_id=friend_family_id,
            referrer_has_active_tariff=referrer_has_active_tariff,
            friend_has_paid=friend_has_paid,
            friend_active_protection_days=friend_active_protection_days,
            already_rewarded_pair=already,
            is_same_family=referrer_family_id == friend_family_id,
        ),
        referrer_qualified_count_before=before,
    )
    if not result.ok:
        return {"ok": False, "reason": result.reason}

    dh = soft_device_hash(device_raw)
    try:
        db.execute(
            _sa_text()(
                """
                INSERT INTO family_referral_ledger (
                    referrer_user_id, friend_user_id, referrer_family_id, friend_family_id,
                    referral_code, status, reason, friend_discount_percent,
                    referrer_protection_days, tier, device_soft_hash
                ) VALUES (
                    :ru, :fu, :rf, :ff, :code, 'granted', :reason, :disc, :days, :tier, :dh
                )
                """
            ),
            {
                "ru": int(referrer_user_id),
                "fu": int(friend_user_id),
                "rf": referrer_family_id,
                "ff": friend_family_id,
                "code": (referral_code or "")[:32] or None,
                "reason": "qualify_paid" if friend_has_paid else "qualify_active_days",
                "disc": int(result.friend_discount_percent),
                "days": int(result.referrer_days),
                "tier": result.tier,
                "dh": dh,
            },
        )
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("apply_family_referral_a insert: %s", e)
        return {"ok": False, "reason": "insert_failed"}

    return {
        "ok": True,
        "reason": "ok",
        "friend_discount_percent": result.friend_discount_percent,
        "referrer_protection_days": result.referrer_days,
        "tier": result.tier,
        "qualified_count": before + 1,
        "tier_progress": _progress(before + 1),
    }


def overview_for_referrer(db: "Session", *, user_id: int, family_id: str) -> dict[str, Any]:
    n = count_granted_for_referrer_family(db, family_id) if family_id else 0
    tier = tier_for_qualified_count(n)
    return {
        "qualified_families": n,
        "tier": tier.tier.value if n > 0 else "none",
        "referrer_protection_days_current_tier": tier.referrer_protection_days if n > 0 else 0,
        "progress": _progress(n),
        "friend_discount_percent": 20,
        "ledger": list_ledger_for_user(db, user_id, limit=20),
    }


def progress_for_qualified(qualified: int) -> dict[str, Any]:
    return _progress(qualified)


def _progress(qualified: int) -> dict[str, Any]:
    q = max(0, int(qualified))
    thresholds = [1, 3, 5, 10]
    nxt = next((t for t in thresholds if t > q), None)
    return {"current": q, "next_tier_at": nxt, "remaining": (nxt - q) if nxt else 0}
