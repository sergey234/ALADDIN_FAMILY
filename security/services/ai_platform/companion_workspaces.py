# -*- coding: utf-8 -*-
"""P3-03 — Companion chat workspaces (folder per topic)."""

from __future__ import annotations

import secrets
from typing import Any, Dict, List, Optional


def create_workspace(
    store: Any,
    user_id: str,
    title: str,
    *,
    character_id: str = "unicorn",
) -> Dict[str, Any]:
    wid = f"ws-{secrets.token_hex(6)}"
    payload = {
        "workspace_id": wid,
        "title": (title or "Новый чат")[:80],
        "character_id": character_id,
    }
    store.upsert_workspace(user_id, wid, payload)
    return payload


def list_workspaces(store: Any, user_id: str, *, limit: int = 30) -> List[Dict[str, Any]]:
    return store.list_workspaces(user_id, limit=limit)


def resolve_thread_for_workspace(
    store: Any,
    user_id: str,
    workspace_id: Optional[str],
    fallback_thread: Optional[str],
) -> str:
    if not workspace_id:
        return fallback_thread or f"companion-{secrets.token_hex(8)}"
    row = store.get_workspace(user_id, workspace_id)
    if row and row.get("thread_id"):
        return str(row["thread_id"])
    tid = fallback_thread or f"companion-{secrets.token_hex(8)}"
    if row:
        row["thread_id"] = tid
        store.upsert_workspace(user_id, workspace_id, row)
    return tid
