"""L-batch: family moat — parents, shared reports, CD status."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.database.database import engine

_PARENT_ROLES = frozenset({"parent"})
_MEMBER_ROLES = frozenset({"child", "teenager", "elderly"})

_CREATE = """
CREATE TABLE IF NOT EXISTS antifake_user_push_tokens (
    user_id BIGINT NOT NULL,
    token_hex VARCHAR(128) NOT NULL,
    platform VARCHAR(16) NOT NULL DEFAULT 'ios',
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (user_id, token_hex)
);
CREATE TABLE IF NOT EXISTS antifake_family_cd_status (
    user_id BIGINT PRIMARY KEY,
    family_id VARCHAR(64) NOT NULL,
    extension_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    synced_count INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_antifake_family_cd_family ON antifake_family_cd_status (family_id, updated_at DESC);
"""


def ensure_tables() -> None:
    with engine.begin() as conn:
        for stmt in _CREATE.strip().split(";"):
            line = stmt.strip()
            if line:
                conn.execute(text(line))
        conn.execute(
            text("ALTER TABLE antifake_reports ADD COLUMN IF NOT EXISTS family_id VARCHAR(64)")
        )
        conn.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_antifake_reports_family
                ON antifake_reports (family_id, created_at DESC)
                """
            )
        )


def register_push_token(user_id: int, token_hex: str, platform: str = "ios") -> None:
    ensure_tables()
    token = (token_hex or "").strip().lower()
    if not token:
        return
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO antifake_user_push_tokens (user_id, token_hex, platform, updated_at)
                VALUES (:uid, :token, :platform, :now)
                ON CONFLICT (user_id, token_hex) DO UPDATE SET
                    platform = EXCLUDED.platform,
                    updated_at = EXCLUDED.updated_at
                """
            ),
            {"uid": int(user_id), "token": token, "platform": platform, "now": now},
        )


def get_push_tokens(user_id: int) -> List[str]:
    ensure_tables()
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT token_hex FROM antifake_user_push_tokens
                WHERE user_id = :uid ORDER BY updated_at DESC
                """
            ),
            {"uid": int(user_id)},
        ).scalars().all()
    return [str(r) for r in rows]


def resolve_primary_family_id(user_id: int) -> Optional[str]:
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT fm.family_id
                FROM family_members fm
                WHERE fm.user_id = :uid
                ORDER BY fm.updated_at DESC NULLS LAST, fm.id DESC
                LIMIT 1
                """
            ),
            {"uid": int(user_id)},
        ).first()
        if row and row[0]:
            return str(row[0]).strip()
        owner = conn.execute(
            text(
                """
                SELECT id FROM families
                WHERE owner_user_id = :uid
                ORDER BY created_at DESC LIMIT 1
                """
            ),
            {"uid": int(user_id)},
        ).first()
        if owner and owner[0]:
            return str(owner[0]).strip()
    return None


def get_member_role(user_id: int, family_id: str) -> Optional[str]:
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT lower(trim(role)) FROM family_members
                WHERE user_id = :uid AND family_id = :fid LIMIT 1
                """
            ),
            {"uid": int(user_id), "fid": family_id},
        ).first()
    return str(row[0]) if row and row[0] else None


def get_parent_user_ids(member_user_id: int) -> List[int]:
    """L-01: parents in the same family as member_user_id."""
    family_id = resolve_primary_family_id(member_user_id)
    if not family_id:
        return []
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT DISTINCT fm.user_id
                FROM family_members fm
                WHERE fm.family_id = :fid AND lower(trim(fm.role)) = 'parent'
                """
            ),
            {"fid": family_id},
        ).scalars().all()
        owner = conn.execute(
            text(
                """
                SELECT owner_user_id FROM families WHERE id = :fid LIMIT 1
                """
            ),
            {"fid": family_id},
        ).first()
    parent_ids = {int(r) for r in rows if r is not None}
    if owner and owner[0] is not None:
        parent_ids.add(int(owner[0]))
    parent_ids.discard(int(member_user_id))
    return sorted(parent_ids)


def is_family_member(user_id: int, family_id: str) -> bool:
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT 1 FROM family_members
                WHERE family_id = :fid AND user_id = :uid
                UNION
                SELECT 1 FROM families WHERE id = :fid AND owner_user_id = :uid
                LIMIT 1
                """
            ),
            {"fid": family_id, "uid": int(user_id)},
        ).first()
    return row is not None


def upsert_cd_status(
    *,
    user_id: int,
    family_id: str,
    extension_enabled: bool,
    synced_count: int,
) -> None:
    ensure_tables()
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO antifake_family_cd_status
                    (user_id, family_id, extension_enabled, synced_count, updated_at)
                VALUES (:uid, :fid, :enabled, :count, :now)
                ON CONFLICT (user_id) DO UPDATE SET
                    family_id = EXCLUDED.family_id,
                    extension_enabled = EXCLUDED.extension_enabled,
                    synced_count = EXCLUDED.synced_count,
                    updated_at = EXCLUDED.updated_at
                """
            ),
            {
                "uid": int(user_id),
                "fid": family_id,
                "enabled": bool(extension_enabled),
                "count": int(synced_count),
                "now": now,
            },
        )


def list_family_cd_status(family_id: str) -> List[Dict[str, Any]]:
    ensure_tables()
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT s.user_id, s.extension_enabled, s.synced_count, s.updated_at,
                       fm.name AS display_name, lower(trim(fm.role)) AS role
                FROM antifake_family_cd_status s
                LEFT JOIN family_members fm
                  ON fm.user_id = s.user_id AND fm.family_id = s.family_id
                WHERE s.family_id = :fid
                ORDER BY s.updated_at DESC
                """
            ),
            {"fid": family_id},
        ).mappings().all()
    out: List[Dict[str, Any]] = []
    for row in rows:
        out.append(
            {
                "user_id": int(row["user_id"]),
                "display_name": row.get("display_name"),
                "role": row.get("role"),
                "extension_enabled": bool(row["extension_enabled"]),
                "synced_count": int(row["synced_count"] or 0),
                "updated_at": row["updated_at"].isoformat() if row.get("updated_at") else None,
            }
        )
    return out


def _mask_phone(phone: str) -> str:
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) < 4:
        return "***"
    return f"***{digits[-4:]}"


def list_family_shared_reports(family_id: str, *, limit: int = 30) -> List[Dict[str, Any]]:
    """L-03: approved scam reports visible to family."""
    ensure_tables()
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT id, phone_e164, label, report_type, job_verdict,
                       job_confidence, created_at, moderated_at
                FROM antifake_reports
                WHERE family_id = :fid
                  AND status = 'approved'
                  AND report_type = 'scam'
                ORDER BY moderated_at DESC NULLS LAST, created_at DESC
                LIMIT :limit
                """
            ),
            {"fid": family_id, "limit": limit},
        ).mappings().all()
    return [
        {
            "id": str(row["id"]),
            "phone_masked": _mask_phone(str(row["phone_e164"])),
            "label": row.get("label"),
            "job_verdict": row.get("job_verdict"),
            "job_confidence": row.get("job_confidence"),
            "created_at": row["created_at"].isoformat() if row.get("created_at") else None,
            "moderated_at": row.get("moderated_at").isoformat() if row.get("moderated_at") else None,
        }
        for row in rows
    ]
