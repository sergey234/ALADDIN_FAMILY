"""fws-01: per-family safe-word hash storage (PostgreSQL)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy import text

from app.database.database import engine
from app.services.antifake_family_store import (
    get_member_role,
    is_family_member,
    resolve_primary_family_id,
)
from app.services.family_safe_word_crypto import (
    hash_phrase,
    validate_phrase,
    verify_phrase,
)

_PARENT_ROLES = frozenset({"parent", "elderly"})

_CREATE = """
CREATE TABLE IF NOT EXISTS family_safe_word_hashes (
    family_id VARCHAR(64) PRIMARY KEY,
    salt_hex VARCHAR(64) NOT NULL,
    hash_hex VARCHAR(128) NOT NULL,
    updated_by_user_id BIGINT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_family_safe_word_updated ON family_safe_word_hashes (updated_at DESC);
CREATE TABLE IF NOT EXISTS family_safe_word_mismatch_log (
    id BIGSERIAL PRIMARY KEY,
    family_id VARCHAR(64) NOT NULL,
    member_user_id BIGINT NOT NULL,
    context VARCHAR(32) NOT NULL DEFAULT 'antifake',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_family_safe_word_mismatch_family
    ON family_safe_word_mismatch_log (family_id, created_at DESC);
"""


def ensure_tables() -> None:
    with engine.begin() as conn:
        for stmt in _CREATE.strip().split(";"):
            line = stmt.strip()
            if line:
                conn.execute(text(line))


def _row_to_status(row) -> Dict[str, Any]:
    return {
        "configured": True,
        "updated_at": row[1].isoformat() if row[1] else None,
        "updated_by_user_id": int(row[0]) if row[0] is not None else None,
    }


def get_status_for_user(user_id: int) -> Dict[str, Any]:
    ensure_tables()
    family_id = resolve_primary_family_id(user_id)
    if not family_id or not is_family_member(user_id, family_id):
        return {"family_id": None, "configured": False}
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT updated_by_user_id, updated_at
                FROM family_safe_word_hashes
                WHERE family_id = :fid
                LIMIT 1
                """
            ),
            {"fid": family_id},
        ).first()
    if not row:
        return {"family_id": family_id, "configured": False}
    payload = _row_to_status(row)
    payload["family_id"] = family_id
    return payload


def set_safe_word(*, user_id: int, phrase: str) -> Dict[str, Any]:
    ensure_tables()
    err = validate_phrase(phrase)
    if err:
        raise ValueError(err)

    family_id = resolve_primary_family_id(user_id)
    if not family_id or not is_family_member(user_id, family_id):
        raise PermissionError("no_family")

    role = (get_member_role(user_id, family_id) or "").lower()
    if role not in _PARENT_ROLES:
        raise PermissionError("parent_only")

    salt_hex, hash_hex = hash_phrase(phrase)
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO family_safe_word_hashes
                    (family_id, salt_hex, hash_hex, updated_by_user_id, updated_at)
                VALUES (:fid, :salt, :hash, :uid, :now)
                ON CONFLICT (family_id) DO UPDATE SET
                    salt_hex = EXCLUDED.salt_hex,
                    hash_hex = EXCLUDED.hash_hex,
                    updated_by_user_id = EXCLUDED.updated_by_user_id,
                    updated_at = EXCLUDED.updated_at
                """
            ),
            {
                "fid": family_id,
                "salt": salt_hex,
                "hash": hash_hex,
                "uid": int(user_id),
                "now": now,
            },
        )
    return {"family_id": family_id, "configured": True, "updated_at": now.isoformat()}


def verify_for_user(*, user_id: int, phrase: str, context: str = "antifake") -> Dict[str, Any]:
    ensure_tables()
    family_id = resolve_primary_family_id(user_id)
    if not family_id or not is_family_member(user_id, family_id):
        return {"family_id": None, "configured": False, "match": False}

    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT salt_hex, hash_hex
                FROM family_safe_word_hashes
                WHERE family_id = :fid
                LIMIT 1
                """
            ),
            {"fid": family_id},
        ).first()

    if not row:
        return {"family_id": family_id, "configured": False, "match": False}

    match = verify_phrase(phrase, str(row[0]), str(row[1]))
    result: Dict[str, Any] = {
        "family_id": family_id,
        "configured": True,
        "match": match,
    }

    if not match:
        now = datetime.now(timezone.utc)
        with engine.begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO family_safe_word_mismatch_log
                        (family_id, member_user_id, context, created_at)
                    VALUES (:fid, :uid, :ctx, :now)
                    """
                ),
                {
                    "fid": family_id,
                    "uid": int(user_id),
                    "ctx": (context or "antifake")[:32],
                    "now": now,
                },
            )
        from app.services.family_safe_word_notify import maybe_notify_parents_safe_word_mismatch

        result["parents_notified"] = maybe_notify_parents_safe_word_mismatch(
            member_user_id=user_id,
            family_id=family_id,
            context=context,
        )
    return result
