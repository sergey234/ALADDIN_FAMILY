# -*- coding: utf-8 -*-
"""24h outcome prompt + pillar adjust after feedback (p2-31)."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from .wellness_four_pillars import pillars_for_age_band, suggest_pillar
from .wellness_i18n_loader import outcome_reminder_from_i18n
from .wellness_pillar_fatigue import record_outcome_for_fatigue


def _parse_iso(ts: str) -> Optional[datetime]:
    try:
        return datetime.fromisoformat(ts.replace("Z", ""))
    except ValueError:
        return None


def has_outcome_since_session(
    store: Any,
    user_id: str,
    session_completed_at: str,
) -> bool:
    for row in store.list_wellness_outcomes(user_id, limit=10):
        created = str(row.get("created_at") or "")
        if created >= session_completed_at:
            return True
    return False


def needs_outcome_followup(
    store: Any,
    user_id: str,
    *,
    hours: int = 24,
) -> bool:
    settings = store.get_wellness_settings(user_id)
    completed_at = str(settings.get("last_session_completed_at") or "")
    if not completed_at:
        return False
    done = _parse_iso(completed_at)
    if not done:
        return False
    if datetime.utcnow() - done < timedelta(hours=hours):
        return False
    if has_outcome_since_session(store, user_id, completed_at):
        return False
    today = date.today().isoformat()
    if str(settings.get("last_outcome_prompt_day") or "") == today:
        return False
    return True


def build_outcome_reminder(
    store: Any,
    user_id: str,
    *,
    locale: str = "ru",
) -> Optional[Dict[str, Any]]:
    if not needs_outcome_followup(store, user_id):
        return None
    settings = store.get_wellness_settings(user_id)
    pillar = settings.get("primary_pillar") or "humanistic"
    copy = outcome_reminder_from_i18n(locale=locale)
    return {
        "alert_type": "outcome_24h",
        "severity": "info",
        "title": copy["title"],
        "body": copy["body"],
        "action": "open_outcome",
        "pillar": pillar,
    }


def dismiss_outcome_prompt(store: Any, user_id: str) -> Dict[str, Any]:
    return store.upsert_wellness_settings(
        user_id,
        last_outcome_prompt_day=date.today().isoformat(),
    )


def adjust_pillar_after_outcome(
    *,
    helpful: int,
    current_pillar: str,
    age_band: str,
    mood_score: Optional[int] = None,
    stress_level: Optional[int] = None,
    jung_enabled: bool = False,
) -> Optional[str]:
    """If session felt worse, suggest another allowed pillar."""
    if helpful >= 4:
        return None
    allowed = pillars_for_age_band(age_band)
    alts = [p for p in allowed if p != current_pillar]
    if not alts:
        return None
    if helpful <= 2:
        mood = mood_score if mood_score is not None else 3
        stress = stress_level if stress_level is not None else 3
        suggested = suggest_pillar(
            age_band=age_band,
            mood_score=mood,
            stress_level=stress,
            escalation_level="L0",
            jung_enabled=jung_enabled,
        )
        if suggested != current_pillar:
            return suggested
        return alts[0]
    return None


def apply_outcome_pillar_adjustment(
    store: Any,
    user_id: str,
    *,
    helpful: int,
    pillar: str,
    age_band: str,
    jung_enabled: bool = False,
) -> Dict[str, Any]:
    checkin = store.get_wellness_checkin(user_id, date.today().isoformat()) or {}
    new_pillar = adjust_pillar_after_outcome(
        helpful=helpful,
        current_pillar=pillar,
        age_band=age_band,
        mood_score=checkin.get("mood_score"),
        stress_level=checkin.get("stress_level"),
        jung_enabled=jung_enabled,
    )
    fatigue = record_outcome_for_fatigue(store, user_id, pillar=pillar, helpful=helpful)
    settings = store.get_wellness_settings(user_id)
    if new_pillar:
        settings = store.upsert_wellness_settings(user_id, primary_pillar=new_pillar)
    store.upsert_wellness_settings(
        user_id,
        last_outcome_prompt_day=date.today().isoformat(),
    )
    return {
        "adjusted_pillar": new_pillar,
        "settings": settings,
        "fatigue": fatigue,
    }
