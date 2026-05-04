"""
Server-side invariant for family roster (GET /api/family/members).

If the tariff allows more than one family slot but the DB has exactly one
member row with role `child` and the JWT actor owns the family, promote that
row to `parent`. This repairs broken creator rows (child + NULL user_id) without
touching real multi-member households.
"""

from __future__ import annotations

from typing import Any, Optional

_DEFAULT_LEVEL_MAX: dict[str, int] = {
    "trial": 3,
    "free": 1,
    "personal": 2,
    "family": 6,
    "premium": 10,
}


def max_family_slots_for_subscription_level(level: Optional[str]) -> int:
    if not level or not str(level).strip():
        return _DEFAULT_LEVEL_MAX["free"]
    key = str(level).strip().lower()
    return _DEFAULT_LEVEL_MAX.get(key, _DEFAULT_LEVEL_MAX["free"])


def _sql(stmt: str) -> Any:
    """sqlalchemy.text on server; plain str in minimal test environments without sqlalchemy."""
    try:
        from sqlalchemy import text as sa_text  # type: ignore

        return sa_text(stmt)
    except ImportError:
        return stmt


def reconcile_sole_child_roster_for_owner(
    db: Any,
    *,
    family_id: str,
    actor_user_id: int,
    log: Any,
) -> bool:
    """
    Returns True if an UPDATE was applied and committed.
    `db` is a synchronous SQLAlchemy session (same as family router).
    """
    fid = str(family_id or "").strip()
    if not fid:
        return False

    sub = db.execute(
        _sql("SELECT COALESCE(subscription_level, 'free') FROM users WHERE id = :uid LIMIT 1"),
        {"uid": int(actor_user_id)},
    ).fetchone()
    level = str(sub[0]) if sub and sub[0] is not None else "free"
    max_slots = max_family_slots_for_subscription_level(level)

    own = db.execute(
        _sql("SELECT owner_user_id FROM families WHERE id = :fid LIMIT 1"),
        {"fid": fid},
    ).fetchone()
    if not own or own[0] is None or int(own[0]) != int(actor_user_id):
        return False

    rows = db.execute(
        _sql(
            "SELECT id, role, user_id FROM family_members WHERE family_id = :fid ORDER BY id ASC"
        ),
        {"fid": fid},
    ).fetchall() or []
    if len(rows) != 1:
        return False

    member_id, role_raw, uid = rows[0][0], rows[0][1], rows[0][2]
    role = str(role_raw or "").strip().lower()
    if role != "child":
        return False
    if uid is not None and int(uid) != int(actor_user_id):
        return False
    # On free (max_slots<=1), still repair a *placeholder* child row (user_id IS NULL) so the owner
    # is not locked out of roster management. Skip auto-promote when a real user_id is attached.
    if max_slots <= 1 and uid is not None:
        return False

    upd = db.execute(
        _sql(
            """
            UPDATE family_members
            SET role = 'parent', updated_at = CURRENT_TIMESTAMP
            WHERE family_id = :fid AND id = :mid AND lower(trim(role)) = 'child'
            """
        ),
        {"fid": fid, "mid": str(member_id)},
    )
    if not getattr(upd, "rowcount", None):
        db.rollback()
        return False
    db.commit()
    log.info(
        "family_roster_reconcile_sole_child_to_parent",
        family_id=fid,
        member_id=str(member_id),
        actor_user_id=int(actor_user_id),
        subscription_level=level,
        max_family_slots=max_slots,
    )
    return True
