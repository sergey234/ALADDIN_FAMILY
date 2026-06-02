# -*- coding: utf-8 -*-
"""
p3-04 — Crisis log + 48h self-harm / L3 monitor.
p3-12 — Wellness premium features blocked until cooldown clear + consent.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

CRISIS_LEVEL_L3 = "L3"
CRISIS_COOLDOWN_HOURS = 48


def _parse_utc(ts: str) -> Optional[datetime]:
    raw = (ts or "").strip()
    if not raw:
        return None
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return None


def record_crisis_l3(store: Any, user_id: str, *, source: str) -> Dict[str, Any]:
    """Append L3 crisis row; starts 48h premium wellness cooldown."""
    now = datetime.utcnow().isoformat()
    return store.log_wellness_crisis_event(
        user_id,
        level=CRISIS_LEVEL_L3,
        source=source,
        created_at=now,
    )


def crisis_cooldown_active(store: Any, user_id: str, *, hours: int = CRISIS_COOLDOWN_HOURS) -> bool:
    last = store.last_wellness_crisis_l3_at(user_id)
    if not last:
        return False
    at = _parse_utc(last)
    if not at:
        return False
    return datetime.utcnow() < at + timedelta(hours=max(1, int(hours)))


def hours_until_cooldown_clear(
    store: Any, user_id: str, *, hours: int = CRISIS_COOLDOWN_HOURS
) -> float:
    last = store.last_wellness_crisis_l3_at(user_id)
    if not last:
        return 0.0
    at = _parse_utc(last)
    if not at:
        return 0.0
    ends = at + timedelta(hours=max(1, int(hours)))
    remaining = (ends - datetime.utcnow()).total_seconds() / 3600.0
    return max(0.0, round(remaining, 2))


def wellness_premium_eligible(
    store: Any,
    user_id: str,
    *,
    profile: Optional[Dict[str, Any]] = None,
    age_band: str = "adult",
) -> Dict[str, Any]:
    """
    Premium wellness paths (Jung dreams, deep reflective) require:
    - wellness consent / ethics (age policy)
    - no L3 crisis in the last 48 hours
    """
    from .wellness_age_policy import has_wellness_consent

    prof = profile or {}
    if not has_wellness_consent(prof, age_band=age_band):
        return {
            "eligible": False,
            "reason": "wellness_consent_required",
            "hours_remaining": 0.0,
            "cooldown_active": False,
        }
    if crisis_cooldown_active(store, user_id):
        return {
            "eligible": False,
            "reason": "crisis_cooldown_48h",
            "hours_remaining": hours_until_cooldown_clear(store, user_id),
            "cooldown_active": True,
        }
    return {
        "eligible": True,
        "reason": None,
        "hours_remaining": 0.0,
        "cooldown_active": False,
    }


def build_crisis_status_payload(store: Any, user_id: str) -> Dict[str, Any]:
    active = crisis_cooldown_active(store, user_id)
    last = store.last_wellness_crisis_l3_at(user_id)
    return {
        "cooldown_active": active,
        "cooldown_hours": CRISIS_COOLDOWN_HOURS,
        "hours_remaining": hours_until_cooldown_clear(store, user_id) if active else 0.0,
        "last_l3_at": last,
        "recent_events": store.list_wellness_crisis_log(user_id, limit=5),
    }
