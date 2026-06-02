# -*- coding: utf-8
"""Merge senior wellness check-ins with elderly health journal (p3-08)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def merge_senior_journal(
    store: Any,
    user_id: str,
    *,
    days: int = 14,
    elderly_entries: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Combine wellness check-ins + optional local elderly health journal rows."""
    checkins = store.list_wellness_checkins(user_id, days=days)
    local = elderly_entries or []
    merged: List[Dict[str, Any]] = []
    for row in checkins:
        merged.append(
            {
                "kind": "wellness_checkin",
                "date": row.get("created_at") or row.get("date"),
                "mood": row.get("mood"),
                "sleep_hours": row.get("sleep_hours"),
                "stress_level": row.get("stress_level"),
            }
        )
    for row in local:
        merged.append(
            {
                "kind": "elderly_health",
                "date": row.get("date"),
                "text": row.get("text") or row.get("entry"),
            }
        )
    merged.sort(key=lambda r: str(r.get("date") or ""), reverse=True)
    return {
        "days": days,
        "entries": merged[: days * 3],
        "checkin_count": len(checkins),
        "elderly_count": len(local),
    }
