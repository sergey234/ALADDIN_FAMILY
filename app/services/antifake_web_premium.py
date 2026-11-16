"""Web Antifake Premium — activation code → users.subscription_level."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple  # Any used by trial snapshot

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.antifake_premium import (
    PREMIUM_LEVELS,
    effective_level_from_parts,
    level_grants_antifake,
    user_has_antifake_access,
)


def subscription_level_from_db(db: Session, user_id: int) -> Optional[str]:
    row = db.execute(
        text("SELECT subscription_level FROM users WHERE id = :uid LIMIT 1"),
        {"uid": user_id},
    ).fetchone()
    if not row or not row[0]:
        return None
    return str(row[0]).lower().strip()


def subscription_trial_snapshot_from_db(
    db: Session, user_id: int
) -> Tuple[Optional[str], Optional[str], Any]:
    """
    user_level, sub_level, trial_end — same sources as family roster effective tier.
    """
    row = db.execute(
        text(
            """
            SELECT
                NULLIF(lower(trim(u.subscription_level)), ''),
                NULLIF(lower(trim(COALESCE(s.level, sd.level))), ''),
                COALESCE(s.trial_end_date, sd.trial_end_date)
            FROM users u
            LEFT JOIN LATERAL (
                SELECT level, trial_end_date
                FROM subscriptions
                WHERE user_id = :uid_text
                ORDER BY updated_at DESC NULLS LAST
                LIMIT 1
            ) s ON true
            LEFT JOIN LATERAL (
                SELECT level, trial_end_date
                FROM subscriptions
                WHERE device_id IS NOT NULL
                  AND device_id = NULLIF(trim(u.device_id), '')
                ORDER BY updated_at DESC NULLS LAST
                LIMIT 1
            ) sd ON true
            WHERE u.id = :uid
            LIMIT 1
            """
        ),
        {"uid": user_id, "uid_text": str(user_id)},
    ).fetchone()
    if not row:
        return None, None, None
    return row[0], row[1], row[2]


def user_has_antifake_access_resolved(
    user: Dict[str, Any],
    db: Optional[Session] = None,
    *,
    smoke_secret: str | None = None,
    client: str | None = None,
) -> bool:
    if user_has_antifake_access(user, smoke_secret=smoke_secret, client=client):
        return True
    if db is None:
        return False
    try:
        uid = int(user.get("id") or user.get("user_id") or 0)
    except (TypeError, ValueError):
        return False
    if uid <= 0:
        return False

    user_level, sub_level, trial_end = subscription_trial_snapshot_from_db(db, uid)
    eff = effective_level_from_parts(user_level, sub_level, trial_end)
    if level_grants_antifake(eff):
        return True

    from app.services.antifake_web_trial import web_trial_grants_access

    return web_trial_grants_access(user, db, client=client)


def _normalize_tariff(tariff_id: str) -> str:
    t = (tariff_id or "free").lower().strip()
    if t in PREMIUM_LEVELS:
        return t
    if t in ("family", "premium", "personal"):
        return t
    return t


def apply_web_activation_code(db: Session, user_id: int, code: str) -> Dict[str, Any]:
    normalized = (code or "").strip().upper()
    if not normalized:
        raise HTTPException(status_code=400, detail="code_required")

    row = db.execute(
        text(
            """
            SELECT tariff_id, expires_at, status
            FROM activation_codes
            WHERE UPPER(activation_code) = :code
            ORDER BY created_at DESC NULLS LAST
            LIMIT 1
            """
        ),
        {"code": normalized},
    ).fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="activation_code_not_found")

    tariff_id, expires_at, status = row[0], row[1], row[2]
    if status and str(status).lower() not in ("active", "issued", ""):
        raise HTTPException(status_code=400, detail="activation_code_inactive")

    if expires_at:
        exp = expires_at
        if exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if exp < datetime.now(timezone.utc):
            raise HTTPException(status_code=410, detail="activation_code_expired")

    level = _normalize_tariff(str(tariff_id or "premium"))
    if level not in PREMIUM_LEVELS:
        raise HTTPException(status_code=400, detail="tariff_not_eligible_for_antifake")

    db.execute(
        text(
            """
            UPDATE users
            SET subscription_level = :level, updated_at = CURRENT_TIMESTAMP
            WHERE id = :uid
            """
        ),
        {"level": level, "uid": user_id},
    )
    db.commit()

    return {
        "success": True,
        "subscription_level": level,
        "tariff_id": tariff_id,
        "expires_at": expires_at.isoformat() if expires_at else None,
    }
