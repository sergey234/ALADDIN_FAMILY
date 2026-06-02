# -*- coding: utf-8 -*-
"""Session recap for Hub / companion continuity (p2-30 / p2-39)."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, Optional

from security.services.ai_platform.wellness_exercise_engine import get_active_session
from security.services.ai_platform.wellness_four_pillars import suggest_pillar
from security.services.ai_platform.wellness_i18n_loader import session_recap_message_from_i18n
from security.services.ai_platform.wellness_insights import continuity_message, get_last_wellness_insight
from security.services.ai_platform.wellness_outcome_followup import (
    build_outcome_reminder,
    needs_outcome_followup,
)
from security.services.ai_platform.wellness_pillar_fatigue import evaluate_pillar_fatigue


def build_session_recap(
    store: Any,
    user_id: str,
    *,
    age_band: str = "teen",
    locale: str = "ru",
    jung_enabled: bool = False,
) -> Dict[str, Any]:
    today = date.today().isoformat()
    checkin = store.get_wellness_checkin(user_id, today)
    settings = store.get_wellness_settings(user_id)
    active = get_active_session(store, user_id, locale=locale)
    last_insight = get_last_wellness_insight(store, user_id)

    mood_score = None
    stress_level = None
    if checkin:
        mood_score = checkin.get("mood_score")
        stress_level = checkin.get("stress_level")

    esc = str(settings.get("escalation_level") or "L0")
    suggested = suggest_pillar(
        age_band=age_band,
        mood_score=mood_score,
        stress_level=stress_level,
        escalation_level=esc,
        jung_enabled=jung_enabled,
    )
    primary = settings.get("primary_pillar") or suggested
    loc = (locale or "ru").lower()[:2]

    low_mood = bool(checkin and mood_score is not None and int(mood_score) <= 2)
    active_incomplete = bool(active and not active.completed)
    message = session_recap_message_from_i18n(
        locale=loc,
        active_exercise=active_incomplete,
        low_mood=low_mood and not active_incomplete,
    )

    cont = continuity_message(last_insight, locale=loc)
    if cont:
        message = cont

    outcome_due = needs_outcome_followup(store, user_id)
    outcome_reminder = build_outcome_reminder(store, user_id, locale=loc) if outcome_due else None
    fatigue = evaluate_pillar_fatigue(
        store,
        user_id,
        age_band=age_band,
        locale=loc,
        jung_enabled=jung_enabled,
    )

    return {
        "day": today,
        "primary_pillar": primary,
        "suggested_pillar": suggested,
        "session_pillar_locked": settings.get("session_pillar_locked"),
        "active_exercise": (
            {
                "id": active.id,
                "pillar": active.pillar,
                "exercise_id": active.exercise_id,
                "step_index": active.step_index,
                "step_total": active.step_total,
            }
            if active
            else None
        ),
        "checkin_today": checkin,
        "last_insight": last_insight,
        "continuity_message": cont,
        "outcome_due": outcome_due,
        "outcome_reminder": outcome_reminder,
        "pillar_fatigue": fatigue,
        "message": message,
    }
