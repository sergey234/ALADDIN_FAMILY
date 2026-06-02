# -*- coding: utf-8 -*-
"""p3-05 — Wellness personal data export + delete (152-ФЗ / GDPR-style)."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict

from .wellness_clinician_export import build_clinician_export


def export_wellness_personal_data(
    store: Any,
    user_id: str,
    *,
    days: int = 90,
    locale: str = "ru",
    age_band: str = "teen",
) -> Dict[str, Any]:
    """Full wellness export for data subject request."""
    loc = (locale or "ru").lower()[:2]
    summary = build_clinician_export(
        store, user_id, days=days, locale=loc, age_band=age_band
    )
    settings = store.get_wellness_settings(user_id)
    consent = store.get_consent(user_id)
    return {
        "export_type": "wellness_personal_v1",
        "generated_day": date.today().isoformat(),
        "user_id": user_id,
        "disclaimer": summary.get("disclaimer"),
        "consent": consent,
        "settings": settings,
        "summary": summary,
        "checkins": store.list_wellness_checkins(user_id, days=days),
        "assessments": store.list_wellness_assessments(user_id, limit=50),
        "exercises": store.list_wellness_exercises(user_id, limit=50),
        "outcomes": store.list_wellness_outcomes(user_id, limit=50),
        "dreams": store.list_wellness_dreams(user_id, limit=50),
        "insights": store.list_wellness_insights(user_id, limit=50),
        "habit_plans": store.list_wellness_habit_plans(user_id, limit=20),
        "crisis_log": store.list_wellness_crisis_log(user_id, limit=20),
        "alert_log": store.list_wellness_alert_log(user_id, limit=20),
    }


def delete_wellness_personal_data(store: Any, user_id: str) -> Dict[str, int]:
    """Erase wellness rows for user; returns per-table delete counts."""
    return store.delete_all_wellness_data(user_id)
