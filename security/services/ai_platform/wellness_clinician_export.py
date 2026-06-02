# -*- coding: utf-8 -*-
"""Teen wellness summary for clinician share — JSON/text, not diagnosis (p2-37)."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict

from security.services.ai_platform.wellness_i18n_loader import clinician_export_copy_from_i18n
from .wellness_journal import low_mood_streak_days


def build_clinician_export(
    store: Any,
    user_id: str,
    *,
    days: int = 14,
    locale: str = "ru",
    age_band: str = "teen",
) -> Dict[str, Any]:
    loc = (locale or "ru").lower()[:2]
    rows = store.list_wellness_checkins(user_id, days=days)
    assessments = store.list_wellness_assessments(user_id, limit=10)
    outcomes = store.list_wellness_outcomes(user_id, limit=20)
    settings = store.get_wellness_settings(user_id)

    mood_scores = [r.get("mood_score") for r in rows if r.get("mood_score") is not None]
    avg_mood = round(sum(int(x) for x in mood_scores) / len(mood_scores), 2) if mood_scores else None

    copy = clinician_export_copy_from_i18n(locale=loc)

    return {
        "title": copy["title"],
        "title_key": "wellness_pdf_clinician_title",
        "disclaimer": copy["disclaimer"],
        "disclaimer_key": "wellness_pdf_disclaimer",
        "generated_day": date.today().isoformat(),
        "age_band": age_band,
        "period_days": days,
        "checkins_count": len(rows),
        "avg_mood_score": avg_mood,
        "low_mood_streak_days": low_mood_streak_days(store, user_id, days=7),
        "primary_pillar": settings.get("primary_pillar"),
        "escalation_level": settings.get("escalation_level"),
        "assessments": [
            {
                "type": a.get("assessment_type"),
                "score": a.get("score"),
                "severity": a.get("severity"),
                "day": (a.get("created_at") or "")[:10],
            }
            for a in assessments
        ],
        "outcomes_count": len(outcomes),
        "helpful_avg": (
            round(
                sum(int(o.get("helpful") or 0) for o in outcomes) / len(outcomes),
                2,
            )
            if outcomes
            else None
        ),
        "checkins": [
            {
                "day": r.get("day"),
                "mood_score": r.get("mood_score"),
                "stress_level": r.get("stress_level"),
                "sleep_hours": r.get("sleep_hours"),
            }
            for r in rows[:days]
        ],
    }
