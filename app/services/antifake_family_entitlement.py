"""Antifake for invited family members via the family owner's plan (l360 1Б.6).

Family / Premium / Trial owners share Antifake with every member of their family.
Personal is "for yourself" and does not share. iOS mirror: TariffEntitlements.familySharingOwnerTiers.
"""
from __future__ import annotations

from typing import Any, Iterable, List, Optional

from sqlalchemy import text

from app.services.antifake_premium import effective_level_from_parts

FAMILY_SHARING_LEVELS = frozenset(
    {"family", "premium", "trial", "trial_premium", "premium_3m", "premium_6m"}
)

_MAX_FAMILIES_CHECKED = 3


def level_shares_with_family(level: Optional[str]) -> bool:
    return (level or "").strip().lower() in FAMILY_SHARING_LEVELS


def _family_ids_for_member(db: Any, user_id: int) -> List[str]:
    rows: Iterable = db.execute(
        text(
            """
            SELECT family_id
            FROM family_members
            WHERE user_id = :uid AND family_id IS NOT NULL
            ORDER BY updated_at DESC NULLS LAST, id DESC
            LIMIT :lim
            """
        ),
        {"uid": user_id, "lim": _MAX_FAMILIES_CHECKED},
    ).fetchall()
    return [str(r[0]).strip() for r in rows if r and r[0] is not None]


def _owner_user_id(db: Any, family_id: str) -> Optional[int]:
    row = db.execute(
        text("SELECT owner_user_id FROM families WHERE id = :fid LIMIT 1"),
        {"fid": family_id},
    ).fetchone()
    if not row or row[0] is None:
        return None
    try:
        return int(row[0])
    except (TypeError, ValueError):
        return None


def family_owner_grants_antifake(db: Any, user_id: int) -> bool:
    """True when the user belongs to a family whose owner (not the user) has a sharing plan."""
    if db is None or user_id <= 0:
        return False
    from app.services.antifake_web_premium import subscription_trial_snapshot_from_db

    try:
        family_ids = _family_ids_for_member(db, user_id)
    except Exception:
        # Failed SELECT leaves the Postgres transaction aborted for the rest of the request.
        db.rollback()
        return False
    for fid in family_ids:
        owner_id = _owner_user_id(db, fid)
        if owner_id is None or owner_id == user_id:
            continue
        user_level, sub_level, trial_end = subscription_trial_snapshot_from_db(db, owner_id)
        if level_shares_with_family(effective_level_from_parts(user_level, sub_level, trial_end)):
            return True
    return False
