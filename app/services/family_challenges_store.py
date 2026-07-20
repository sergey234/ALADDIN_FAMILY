"""P2.9h FamilyChallenge: custom family challenges (max 5 active). Last-write wins."""
from __future__ import annotations

import json
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import text

from app.database.database import engine
from app.services.antifake_family_store import (
    is_family_member,
    resolve_primary_family_id,
)

MAX_CHALLENGES = 5
_DEFAULT: Dict[str, Any] = {"challenges": [], "updated_at": None}

_CREATE = """
CREATE TABLE IF NOT EXISTS family_challenges (
    family_id VARCHAR(64) PRIMARY KEY,
    challenges_json JSONB NOT NULL,
    updated_by_user_id BIGINT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def ensure_tables() -> None:
    with engine.begin() as conn:
        conn.execute(text(_CREATE.strip()))


def _normalize_challenge(raw: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict):
        return None
    title = str(raw.get("title") or "").strip()
    if not title:
        return None
    cid = str(raw.get("id") or "").strip() or str(uuid.uuid4())
    emoji = str(raw.get("emoji") or "").strip()[:8]
    member_ids_raw = raw.get("member_ids") or raw.get("memberIds") or []
    member_ids: List[str] = []
    if isinstance(member_ids_raw, list):
        for mid in member_ids_raw[:32]:
            s = str(mid or "").strip()
            if s:
                member_ids.append(s[:64])
    created_by = str(raw.get("created_by") or raw.get("createdBy") or "").strip()[:64]
    return {
        "id": cid[:64],
        "title": title[:120],
        "emoji": emoji or "🏁",
        "member_ids": member_ids,
        "enabled": bool(raw.get("enabled", True)),
        "created_by": created_by,
    }


def normalize_payload(raw: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    base = deepcopy(_DEFAULT)
    if not isinstance(raw, dict):
        return base
    items_in = raw.get("challenges") if isinstance(raw.get("challenges"), list) else []
    items: List[Dict[str, Any]] = []
    for entry in items_in:
        normalized = _normalize_challenge(entry)
        if normalized:
            items.append(normalized)
        if len(items) >= MAX_CHALLENGES:
            break
    base["challenges"] = items
    return base


def get_challenges_for_user(user_id: int) -> Dict[str, Any]:
    ensure_tables()
    family_id = resolve_primary_family_id(user_id)
    if not family_id or not is_family_member(user_id, family_id):
        return {
            "family_id": None,
            "challenges": normalize_payload(None)["challenges"],
            "configured": False,
            "max": MAX_CHALLENGES,
        }
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT challenges_json, updated_at, updated_by_user_id
                FROM family_challenges
                WHERE family_id = :fid
                LIMIT 1
                """
            ),
            {"fid": family_id},
        ).first()
    if not row:
        return {
            "family_id": family_id,
            "challenges": [],
            "configured": False,
            "max": MAX_CHALLENGES,
        }
    payload = row[0]
    if isinstance(payload, str):
        payload = json.loads(payload)
    normalized = normalize_payload(
        payload if isinstance(payload, dict) else {"challenges": payload if isinstance(payload, list) else []}
    )
    return {
        "family_id": family_id,
        "challenges": normalized["challenges"],
        "configured": True,
        "max": MAX_CHALLENGES,
        "updated_at": row[1].isoformat() if row[1] else None,
        "updated_by_user_id": int(row[2]) if row[2] is not None else None,
    }


def set_challenges_for_user(*, user_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Last-write wins: POST replaces the whole challenges list for the family."""
    ensure_tables()
    family_id = resolve_primary_family_id(user_id)
    if not family_id or not is_family_member(user_id, family_id):
        raise PermissionError("no_family")

    normalized = normalize_payload(payload)
    if len(normalized["challenges"]) > MAX_CHALLENGES:
        raise ValueError("max_challenges")

    now = datetime.now(timezone.utc)
    normalized["updated_at"] = now.isoformat()
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO family_challenges
                    (family_id, challenges_json, updated_by_user_id, updated_at)
                VALUES (:fid, CAST(:cfg AS JSONB), :uid, :now)
                ON CONFLICT (family_id) DO UPDATE SET
                    challenges_json = EXCLUDED.challenges_json,
                    updated_by_user_id = EXCLUDED.updated_by_user_id,
                    updated_at = EXCLUDED.updated_at
                """
            ),
            {
                "fid": family_id,
                "cfg": json.dumps({"challenges": normalized["challenges"]}),
                "uid": int(user_id),
                "now": now,
            },
        )
    return {
        "family_id": family_id,
        "challenges": normalized["challenges"],
        "configured": True,
        "max": MAX_CHALLENGES,
        "updated_at": now.isoformat(),
    }
