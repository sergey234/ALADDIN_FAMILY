"""Family location history on the server (l360 stage 4).

Points come from POST /api/parental-control/location/report (table `location_history`).
How long a person's points are kept depends on the plan: own plan or the family owner's plan,
whichever is longer. Free / Personal 24 h, Trial / Family 7 days, Premium 30 days.
Nothing is kept longer than 30 days. Account delete removes all points (app/routers/user.py).
iOS mirror: TariffEntitlements.locationHistoryHours. Privacy text: privacy_location_history_*.
"""
from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional

from sqlalchemy import text

from app.services.antifake_premium import effective_level_from_parts

logger = logging.getLogger(__name__)

FREE_HOURS = 24
FAMILY_HOURS = 7 * 24
PREMIUM_HOURS = 30 * 24
MAX_HOURS = PREMIUM_HOURS
MAX_POINTS_RETURNED = 500

_LEVEL_HOURS = {
    "free": FREE_HOURS,
    "personal": FREE_HOURS,
    "trial": FAMILY_HOURS,
    "family": FAMILY_HOURS,
    "trial_premium": PREMIUM_HOURS,
    "premium": PREMIUM_HOURS,
    "premium_3m": PREMIUM_HOURS,
    "premium_6m": PREMIUM_HOURS,
}

# Personal is "for yourself": it does not extend history for the rest of the family.
_OWNER_SHARED_LEVELS = frozenset({"trial", "family", "trial_premium", "premium", "premium_3m", "premium_6m"})

CHILD_ROLES = frozenset({"child", "teenager"})

_GLOBAL_PURGE_EVERY_SEC = 3600
_last_global_purge = 0.0
_index_ready = False


def retention_hours_for_level(level: Optional[str]) -> int:
    return _LEVEL_HOURS.get((level or "").strip().lower(), FREE_HOURS)


def _level_of(db: Any, user_id: int) -> str:
    from app.services.antifake_web_premium import subscription_trial_snapshot_from_db

    user_level, sub_level, trial_end = subscription_trial_snapshot_from_db(db, user_id)
    return effective_level_from_parts(user_level, sub_level, trial_end)


def _owner_ids_for_member(db: Any, user_id: int) -> List[int]:
    rows: Iterable = db.execute(
        text(
            """
            SELECT DISTINCT f.owner_user_id
            FROM family_members fm
            JOIN families f ON f.id = fm.family_id
            WHERE fm.user_id = :uid AND f.owner_user_id IS NOT NULL
            LIMIT 3
            """
        ),
        {"uid": user_id},
    ).fetchall()
    out: List[int] = []
    for row in rows:
        try:
            out.append(int(row[0]))
        except (TypeError, ValueError, IndexError):
            continue
    return out


def retention_hours_for_user(db: Any, user_id: int) -> int:
    """Longest of: own plan, family owner's plan (if that plan is shared with the family)."""
    hours = retention_hours_for_level(_level_of(db, user_id))
    for owner_id in _owner_ids_for_member(db, user_id):
        if owner_id == user_id:
            continue
        level = _level_of(db, owner_id)
        if level.strip().lower() in _OWNER_SHARED_LEVELS:
            hours = max(hours, retention_hours_for_level(level))
    return min(hours, MAX_HOURS)


def ensure_index(db: Any) -> None:
    global _index_ready
    if _index_ready:
        return
    db.execute(
        text(
            "CREATE INDEX IF NOT EXISTS ix_location_history_user_ts "
            "ON location_history (user_id, timestamp)"
        )
    )
    db.commit()
    _index_ready = True


def purge_user(db: Any, user_id: int, hours: int, now: Optional[datetime] = None) -> int:
    cutoff = (now or datetime.now(timezone.utc)) - timedelta(hours=hours)
    result = db.execute(
        text("DELETE FROM location_history WHERE user_id = :uid AND timestamp < :cutoff"),
        {"uid": user_id, "cutoff": cutoff},
    )
    return int(getattr(result, "rowcount", 0) or 0)


def purge_all(db: Any, now: Optional[datetime] = None) -> Dict[str, int]:
    """Apply each person's retention to every stored point. Safe to run any time."""
    now = now or datetime.now(timezone.utc)
    deleted_over_max = db.execute(
        text("DELETE FROM location_history WHERE timestamp < :cutoff"),
        {"cutoff": now - timedelta(hours=MAX_HOURS)},
    )
    over_max = int(getattr(deleted_over_max, "rowcount", 0) or 0)
    rows = db.execute(
        text("SELECT DISTINCT user_id FROM location_history WHERE timestamp < :cutoff"),
        {"cutoff": now - timedelta(hours=FREE_HOURS)},
    ).fetchall()
    by_plan = 0
    for row in rows:
        try:
            uid = int(row[0])
        except (TypeError, ValueError, IndexError):
            continue
        by_plan += purge_user(db, uid, retention_hours_for_user(db, uid), now=now)
    db.commit()
    return {"over_max": over_max, "by_plan": by_plan, "users_checked": len(rows)}


def enforce_after_write(db: Any, user_id: int) -> None:
    """Called after a point is stored. Failures never block the location report."""
    global _last_global_purge
    try:
        ensure_index(db)
        purge_user(db, user_id, retention_hours_for_user(db, user_id))
        db.commit()
        if time.monotonic() - _last_global_purge >= _GLOBAL_PURGE_EVERY_SEC:
            _last_global_purge = time.monotonic()
            stats = purge_all(db)
            logger.info("location_history purge %s", stats)
    except Exception as exc:
        db.rollback()
        logger.warning("location_history retention skipped: %s", exc)


def viewer_may_see(
    viewer_role: Optional[str],
    viewer_member_id: str,
    target_member_id: str,
    parent_member_ids: Iterable[str],
) -> bool:
    """Same rule as Where-phone: a child or teenager sees self and parents; others see the family."""
    if (viewer_role or "").strip().lower() not in CHILD_ROLES:
        return True
    allowed = {str(m).strip() for m in parent_member_ids if str(m).strip()}
    if viewer_member_id:
        allowed.add(viewer_member_id)
    return target_member_id in allowed


def thin(points: List[Dict[str, Any]], limit: int = MAX_POINTS_RETURNED) -> List[Dict[str, Any]]:
    """Keep first, last and evenly spaced points so a month of data stays small."""
    if len(points) <= limit:
        return points
    if limit < 2:
        return points[-limit:] if limit > 0 else []
    step = (len(points) - 1) / (limit - 1)
    return [points[round(i * step)] for i in range(limit)]


def history_for_member(db: Any, viewer_user_id: int, member_id: str, now: Optional[datetime] = None) -> Dict[str, Any]:
    """Points of one family member within that member's retention window."""
    from app.services.antifake_family_store import get_member_role, resolve_primary_family_id

    family_id = resolve_primary_family_id(int(viewer_user_id))
    if not family_id:
        return {"ok": False, "error": "no_family"}
    target = db.execute(
        text(
            """
            SELECT id, user_id FROM family_members
            WHERE family_id = :fid AND CAST(id AS TEXT) = :mid
            LIMIT 1
            """
        ),
        {"fid": family_id, "mid": str(member_id).strip()},
    ).fetchone()
    if not target:
        return {"ok": False, "error": "member_not_found"}
    viewer_row = db.execute(
        text("SELECT id FROM family_members WHERE family_id = :fid AND user_id = :uid ORDER BY id DESC LIMIT 1"),
        {"fid": family_id, "uid": int(viewer_user_id)},
    ).fetchone()
    parent_rows = db.execute(
        text("SELECT id FROM family_members WHERE family_id = :fid AND lower(trim(role)) = 'parent'"),
        {"fid": family_id},
    ).fetchall()
    viewer_member_id = str(viewer_row[0]) if viewer_row else ""
    if not viewer_may_see(
        get_member_role(int(viewer_user_id), family_id),
        viewer_member_id,
        str(target[0]),
        [str(r[0]) for r in parent_rows],
    ):
        return {"ok": False, "error": "member_not_found"}

    target_user_id = target[1]
    if target_user_id is None:
        return {"ok": True, "member_id": str(target[0]), "retention_hours": FREE_HOURS, "points": []}
    hours = retention_hours_for_user(db, int(target_user_id))
    since = (now or datetime.now(timezone.utc)) - timedelta(hours=hours)
    rows = db.execute(
        text(
            """
            SELECT lat, lon, speed, timestamp
            FROM location_history
            WHERE user_id = :uid AND timestamp >= :since
            ORDER BY timestamp ASC
            """
        ),
        {"uid": int(target_user_id), "since": since},
    ).fetchall()
    points = [
        {
            "lat": float(r[0]),
            "lon": float(r[1]),
            "speed": float(r[2]) if r[2] is not None else None,
            "at": r[3].isoformat() if hasattr(r[3], "isoformat") else str(r[3]),
        }
        for r in rows
    ]
    return {
        "ok": True,
        "member_id": str(target[0]),
        "retention_hours": hours,
        "points": thin(points),
    }
