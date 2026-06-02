# -*- coding: utf-8 -*-
"""Pillar fatigue: 5 sessions same pillar without improvement (p2-32 / p2-41)."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .wellness_four_pillars import pillars_for_age_band, suggest_pillar

FATIGUE_THRESHOLD = 5
STALE_HELPFUL_MAX = 3


def record_outcome_for_fatigue(
    store: Any,
    user_id: str,
    *,
    pillar: str,
    helpful: int,
) -> Dict[str, Any]:
    """Update streak after outcome tap (helpful 1–5)."""
    settings = store.get_wellness_settings(user_id)
    streak_pillar = settings.get("fatigue_streak_pillar")
    count = int(settings.get("fatigue_streak_count") or 0)
    score = int(helpful)

    if score >= 4:
        count = 0
        streak_pillar = None
    elif score <= STALE_HELPFUL_MAX:
        if streak_pillar == pillar:
            count += 1
        else:
            streak_pillar = pillar
            count = 1
    else:
        count = max(0, count - 1)

    updated = store.upsert_wellness_settings(
        user_id,
        fatigue_streak_pillar=streak_pillar,
        fatigue_streak_count=count,
    )
    return {
        "fatigue_streak_pillar": streak_pillar,
        "fatigue_streak_count": count,
        "settings": updated,
    }


def evaluate_pillar_fatigue(
    store: Any,
    user_id: str,
    *,
    age_band: str = "teen",
    locale: str = "ru",
    jung_enabled: bool = False,
) -> Dict[str, Any]:
    settings = store.get_wellness_settings(user_id)
    pillar = settings.get("fatigue_streak_pillar") or settings.get("primary_pillar")
    count = int(settings.get("fatigue_streak_count") or 0)
    fatigued = bool(pillar and count >= FATIGUE_THRESHOLD)

    suggested = None
    if fatigued and pillar:
        from datetime import date

        checkin = store.get_wellness_checkin(user_id, date.today().isoformat()) or {}
        suggested = suggest_pillar(
            age_band=age_band,
            mood_score=checkin.get("mood_score"),
            stress_level=checkin.get("stress_level"),
            escalation_level=str(settings.get("escalation_level") or "L0"),
            jung_enabled=jung_enabled,
        )
        allowed = pillars_for_age_band(age_band)
        if suggested == pillar:
            alts = [p for p in allowed if p != pillar]
            suggested = alts[0] if alts else pillar

    loc = (locale or "ru").lower()[:2]
    if fatigued:
        if loc == "en":
            message = "Let's try another focus — the same path hasn't helped much lately."
        else:
            message = "Давай попробуем другой способ — эта дорожка в последнее время мало помогает."
    else:
        message = None

    return {
        "fatigued": fatigued,
        "streak_pillar": pillar,
        "streak_count": count,
        "threshold": FATIGUE_THRESHOLD,
        "suggested_pillar": suggested if fatigued else None,
        "message": message,
    }
