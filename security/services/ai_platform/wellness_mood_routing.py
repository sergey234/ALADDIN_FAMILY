# -*- coding: utf-8 -*-
"""Pillar suggestion with emotion-agent mood fallback (p2-33)."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, Optional

from .wellness_emotion_agent import resolve_mood_for_user, resolve_mood_score
from .wellness_four_pillars import suggest_pillar


def suggest_pillar_with_mood_fallback(
    store: Any,
    user_id: str,
    *,
    age_band: str,
    escalation_level: str = "L0",
    jung_enabled: bool = False,
    message: str = "",
) -> Dict[str, Any]:
    today = date.today().isoformat()
    checkin = store.get_wellness_checkin(user_id, today) or {}
    mood_score, mood_source = resolve_mood_score(
        checkin=checkin,
        message=message,
        notes=str(checkin.get("notes") or ""),
    )
    if mood_score is None and message:
        mood_score, mood_source = resolve_mood_for_user(
            store, user_id, message=message
        )

    stress_level = checkin.get("stress_level")
    suggested = suggest_pillar(
        age_band=age_band,
        mood_score=mood_score,
        stress_level=stress_level,
        escalation_level=escalation_level,
        jung_enabled=jung_enabled,
    )
    return {
        "suggested_pillar": suggested,
        "mood_score": mood_score,
        "mood_source": mood_source,
        "stress_level": stress_level,
        "age_band": age_band,
    }
