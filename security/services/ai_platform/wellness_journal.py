# -*- coding: utf-8 -*-
"""Wellness journal — check-ins + mood from chat (p1-02)."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from .wellness_age_policy import normalize_age_band

MOOD_SCORES = {
    "great": 5,
    "ok": 3,
    "sad": 1,
    "anxious": 2,
    "tired": 2,
    "joyful": 5,
    "neutral": 3,
}


def mood_score_from_emoji(mood_emoji: Optional[str]) -> Optional[int]:
    if not mood_emoji:
        return None
    key = mood_emoji.strip().lower()
    return MOOD_SCORES.get(key)


def record_checkin(
    store,
    *,
    user_id: str,
    mood_emoji: str,
    sleep_hours: Optional[float] = None,
    stress_level: Optional[int] = None,
    energy_level: Optional[int] = None,
    notes: Optional[str] = None,
    source: str = "app",
    age_band: str = "teen",
    day: Optional[str] = None,
) -> Dict[str, Any]:
    day = day or date.today().isoformat()
    score = mood_score_from_emoji(mood_emoji)
    return store.upsert_wellness_checkin(
        user_id,
        day=day,
        mood_emoji=mood_emoji,
        mood_score=score,
        sleep_hours=sleep_hours,
        stress_level=stress_level,
        energy_level=energy_level,
        notes=notes,
        source=source,
        age_band=normalize_age_band(age_band),
    )


def record_mood_from_chat(
    store,
    *,
    user_id: str,
    mood: str,
    age_band: str = "teen",
) -> Optional[Dict[str, Any]]:
    """Lightweight auto-entry when companion mood classifier detects low mood."""
    key = (mood or "").strip().lower()
    if key not in MOOD_SCORES:
        return None
    if key in ("great", "ok", "joyful", "neutral", "playful", "excited", "curious"):
        return None
    return record_checkin(
        store,
        user_id=user_id,
        mood_emoji=key if key in MOOD_SCORES else "sad",
        source="chat",
        age_band=age_band,
    )


def low_mood_streak_days(store, user_id: str, *, days: int = 7) -> int:
    rows = store.list_wellness_checkins(user_id, days=days)
    streak = 0
    for row in sorted(rows, key=lambda r: r.get("day") or "", reverse=True):
        score = row.get("mood_score")
        if score is None:
            continue
        if int(score) <= 2:
            streak += 1
        else:
            break
    return streak
