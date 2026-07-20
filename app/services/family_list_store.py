"""P1.6 AnyList-lite: shared family checklist (last-write wins)."""
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

_DEFAULT: Dict[str, Any] = {"items": [], "updated_at": None}

_CREATE = """
CREATE TABLE IF NOT EXISTS family_shared_lists (
    family_id VARCHAR(64) PRIMARY KEY,
    list_json JSONB NOT NULL,
    updated_by_user_id BIGINT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""


def ensure_tables() -> None:
    with engine.begin() as conn:
        conn.execute(text(_CREATE.strip()))


def _normalize_item(raw: Any) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict):
        return None
    text_val = str(raw.get("text") or "").strip()
    if not text_val:
        return None
    item_id = str(raw.get("id") or "").strip() or str(uuid.uuid4())
    return {
        "id": item_id[:64],
        "text": text_val[:200],
        "checked": bool(raw.get("checked", False)),
    }


def normalize_list(raw: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    base = deepcopy(_DEFAULT)
    if not isinstance(raw, dict):
        return base
    items_in = raw.get("items") if isinstance(raw.get("items"), list) else []
    items: List[Dict[str, Any]] = []
    for entry in items_in[:100]:
        normalized = _normalize_item(entry)
        if normalized:
            items.append(normalized)
    base["items"] = items
    return base


def get_list_for_user(user_id: int) -> Dict[str, Any]:
    ensure_tables()
    family_id = resolve_primary_family_id(user_id)
    if not family_id or not is_family_member(user_id, family_id):
        return {"family_id": None, "list": normalize_list(None), "configured": False}
    with engine.connect() as conn:
        row = conn.execute(
            text(
                """
                SELECT list_json, updated_at, updated_by_user_id
                FROM family_shared_lists
                WHERE family_id = :fid
                LIMIT 1
                """
            ),
            {"fid": family_id},
        ).first()
    if not row:
        return {
            "family_id": family_id,
            "list": normalize_list(None),
            "configured": False,
        }
    payload = row[0]
    if isinstance(payload, str):
        payload = json.loads(payload)
    return {
        "family_id": family_id,
        "list": normalize_list(payload if isinstance(payload, dict) else None),
        "configured": True,
        "updated_at": row[1].isoformat() if row[1] else None,
        "updated_by_user_id": int(row[2]) if row[2] is not None else None,
    }


def set_list_for_user(*, user_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Last-write wins: POST replaces the whole list for the family."""
    ensure_tables()
    family_id = resolve_primary_family_id(user_id)
    if not family_id or not is_family_member(user_id, family_id):
        raise PermissionError("no_family")

    normalized = normalize_list(payload)
    now = datetime.now(timezone.utc)
    normalized["updated_at"] = now.isoformat()
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO family_shared_lists
                    (family_id, list_json, updated_by_user_id, updated_at)
                VALUES (:fid, CAST(:cfg AS JSONB), :uid, :now)
                ON CONFLICT (family_id) DO UPDATE SET
                    list_json = EXCLUDED.list_json,
                    updated_by_user_id = EXCLUDED.updated_by_user_id,
                    updated_at = EXCLUDED.updated_at
                """
            ),
            {
                "fid": family_id,
                "cfg": json.dumps({"items": normalized["items"]}),
                "uid": int(user_id),
                "now": now,
            },
        )
    return {
        "family_id": family_id,
        "list": normalized,
        "configured": True,
        "updated_at": now.isoformat(),
    }
