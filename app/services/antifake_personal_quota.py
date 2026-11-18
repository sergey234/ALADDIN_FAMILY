"""Personal plan: monthly cap on heavy (AI) Antifake checks (l360 1Б.3).

Heavy = audio, video, document, call. Text/URL stay unlimited (anti-spam rate limits only).
Applies only when the user's own effective level is `personal` and no family owner shares
Family/Premium/Trial with them. Month = calendar month, Moscow time (UTC+3).
`ANTIFAKE_PERSONAL_MONTHLY_HEAVY_LIMIT=0` disables the cap without a code deploy.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi import HTTPException
from sqlalchemy import text

from app.services.antifake_premium import effective_level_from_parts

HEAVY_JOB_TYPES = frozenset({"audio", "video", "document", "call"})
DEFAULT_PERSONAL_MONTHLY_LIMIT = 30
_MSK = timezone(timedelta(hours=3))

_table_ready = False


def personal_monthly_limit() -> int:
    raw = os.environ.get("ANTIFAKE_PERSONAL_MONTHLY_HEAVY_LIMIT", str(DEFAULT_PERSONAL_MONTHLY_LIMIT))
    try:
        return max(0, int(raw))
    except (TypeError, ValueError):
        return DEFAULT_PERSONAL_MONTHLY_LIMIT


def month_key(now: Optional[datetime] = None) -> str:
    moment = now or datetime.now(timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return moment.astimezone(_MSK).strftime("%Y-%m")


def resets_at(now: Optional[datetime] = None) -> str:
    year, month = (int(p) for p in month_key(now).split("-"))
    if month == 12:
        year, month = year + 1, 1
    else:
        month += 1
    return f"{year:04d}-{month:02d}-01"


def _ensure_table(db: Any) -> None:
    global _table_ready
    if _table_ready:
        return
    db.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS antifake_monthly_usage (
                user_id BIGINT NOT NULL,
                month VARCHAR(7) NOT NULL,
                heavy_count INTEGER NOT NULL DEFAULT 0,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, month)
            )
            """
        )
    )
    db.commit()
    _table_ready = True


def _user_id(user: Dict[str, Any]) -> int:
    try:
        return int(user.get("id") or user.get("user_id") or 0)
    except (TypeError, ValueError):
        return 0


def is_quota_limited(user: Dict[str, Any], db: Any) -> bool:
    """Own effective level is Personal and no family owner shares a bigger plan."""
    uid = _user_id(user)
    if db is None or uid <= 0 or personal_monthly_limit() <= 0:
        return False
    from app.services.antifake_family_entitlement import family_owner_grants_antifake
    from app.services.antifake_web_premium import subscription_trial_snapshot_from_db

    user_level, sub_level, trial_end = subscription_trial_snapshot_from_db(db, uid)
    jwt_level = str(user.get("subscription_level") or "").strip().lower() or None
    level = effective_level_from_parts(user_level or jwt_level, sub_level, trial_end)
    if level != "personal":
        return False
    return not family_owner_grants_antifake(db, uid)


def used_this_month(db: Any, user_id: int, now: Optional[datetime] = None) -> int:
    _ensure_table(db)
    row = db.execute(
        text("SELECT heavy_count FROM antifake_monthly_usage WHERE user_id = :uid AND month = :m"),
        {"uid": user_id, "m": month_key(now)},
    ).fetchone()
    return int(row[0]) if row and row[0] is not None else 0


def consume_heavy_check(user: Dict[str, Any], db: Any, job_type: str, now: Optional[datetime] = None) -> bool:
    """Atomically count one heavy check; HTTP 429 `monthly_quota_exceeded` when the cap is reached.

    Returns True when a check was counted (caller refunds it if analysis fails on our side).
    """
    if job_type not in HEAVY_JOB_TYPES or not is_quota_limited(user, db):
        return False
    uid = _user_id(user)
    limit = personal_monthly_limit()
    _ensure_table(db)
    row = db.execute(
        text(
            """
            INSERT INTO antifake_monthly_usage (user_id, month, heavy_count, updated_at)
            VALUES (:uid, :m, 1, CURRENT_TIMESTAMP)
            ON CONFLICT (user_id, month) DO UPDATE
                SET heavy_count = antifake_monthly_usage.heavy_count + 1,
                    updated_at = CURRENT_TIMESTAMP
                WHERE antifake_monthly_usage.heavy_count < :lim
            RETURNING heavy_count
            """
        ),
        {"uid": uid, "m": month_key(now), "lim": limit},
    ).fetchone()
    db.commit()
    if row is None:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "monthly_quota_exceeded",
                "limit": limit,
                "used": limit,
                "resets_at": resets_at(now),
            },
        )
    return True


def refund_heavy_check(user: Dict[str, Any], db: Any, now: Optional[datetime] = None) -> None:
    uid = _user_id(user)
    if db is None or uid <= 0:
        return
    try:
        db.execute(
            text(
                """
                UPDATE antifake_monthly_usage
                SET heavy_count = GREATEST(heavy_count - 1, 0), updated_at = CURRENT_TIMESTAMP
                WHERE user_id = :uid AND month = :m
                """
            ),
            {"uid": uid, "m": month_key(now)},
        )
        db.commit()
    except Exception:
        db.rollback()


def quota_status(user: Dict[str, Any], db: Any, now: Optional[datetime] = None) -> Dict[str, Any]:
    limit = personal_monthly_limit()
    if not is_quota_limited(user, db):
        return {
            "limited": False,
            "limit": None,
            "used": 0,
            "resets_at": None,
            "personal_monthly_limit": limit,
        }
    return {
        "limited": True,
        "limit": limit,
        "used": min(limit, used_this_month(db, _user_id(user), now)),
        "resets_at": resets_at(now),
        "personal_monthly_limit": limit,
    }
