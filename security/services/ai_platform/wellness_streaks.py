# -*- coding: utf-8 -*-
"""Check-in streaks and soft badges (p2-48)."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List

_BADGE_THRESHOLDS = (3, 7, 14, 30)


def compute_checkin_streak(store: Any, user_id: str, *, max_days: int = 60) -> int:
    rows = store.list_wellness_checkins(user_id, days=max_days)
    days_with_checkin = sorted(
        {str(r.get("day")) for r in rows if r.get("day")},
        reverse=True,
    )
    if not days_with_checkin:
        return 0
    streak = 0
    cursor = date.today()
    day_set = set(days_with_checkin)
    while cursor.isoformat() in day_set:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def _badge_for_streak(streak: int) -> Optional[Dict[str, Any]]:
    earned = [t for t in _BADGE_THRESHOLDS if streak >= t]
    if not earned:
        return None
    level = max(earned)
    return {
        "badge_id": f"checkin_{level}",
        "threshold_days": level,
        "label_key": f"wellness_badge_checkin_{level}",
    }


def build_streaks_payload(
    store: Any,
    user_id: str,
    *,
    locale: str = "ru",
) -> Dict[str, Any]:
    streak = compute_checkin_streak(store, user_id)
    badge = _badge_for_streak(streak)
    next_threshold = next((t for t in _BADGE_THRESHOLDS if streak < t), None)
    loc = (locale or "ru").lower()[:2]
    if loc == "en":
        message = f"{streak} day(s) of check-ins in a row."
    else:
        message = f"{streak} день(дней) check-in подряд."
    badges: List[Dict[str, Any]] = []
    for t in _BADGE_THRESHOLDS:
        badges.append(
            {
                "badge_id": f"checkin_{t}",
                "threshold_days": t,
                "earned": streak >= t,
                "label_key": f"wellness_badge_checkin_{t}",
            }
        )
    return {
        "checkin_streak": streak,
        "current_badge": badge,
        "next_threshold_days": next_threshold,
        "message": message,
        "badges": badges,
    }
