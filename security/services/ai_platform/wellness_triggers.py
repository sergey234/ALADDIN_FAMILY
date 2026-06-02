# -*- coding: utf-8 -*-
"""Proactive triggers — 3 days low mood → PHQ-lite (p1-09)."""

from __future__ import annotations

from typing import Any, Dict

from .wellness_age_policy import can_use_phq_lite, normalize_age_band
from .wellness_journal import low_mood_streak_days
from .wellness_nudge import evaluate_idle_nudge


def evaluate_triggers(
    store,
    user_id: str,
    *,
    age_band: str,
    locale: str = "ru",
) -> Dict[str, Any]:
    band = normalize_age_band(age_band)
    streak = low_mood_streak_days(store, user_id, days=7)
    out: Dict[str, Any] = {
        "low_mood_streak_days": streak,
        "suggest_phq_lite": False,
        "suggest_checkin": streak >= 1,
        "reason": None,
    }
    if streak >= 3 and can_use_phq_lite(band):
        out["suggest_phq_lite"] = True
        out["reason"] = "low_mood_streak_3d"
    out.update(evaluate_idle_nudge(store, user_id, locale=locale))
    return out
