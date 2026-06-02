# -*- coding: utf-8 -*-
"""Wellness alerts + family aggregate signals (p2-24). No chat text."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, List

from security.services.ai_platform.wellness_i18n_loader import (
    family_dashboard_message_from_i18n,
    family_mood_trend_down_from_i18n,
    load_alert_text,
    load_push_message,
)
from security.services.ai_platform.wellness_outcome_followup import build_outcome_reminder
from security.services.ai_platform.wellness_triggers import evaluate_triggers
from security.services.ai_platform.wellness_escalation import evaluate_escalation
from security.services.ai_platform.wellness_journal import low_mood_streak_days


@dataclass(frozen=True)
class WellnessAlert:
    alert_type: str
    severity: str
    title: str
    body: str
    action: str


def build_user_alerts(
    store: Any,
    user_id: str,
    *,
    age_band: str = "teen",
    locale: str = "ru",
) -> List[WellnessAlert]:
    alerts: List[WellnessAlert] = []
    triggers = evaluate_triggers(store, user_id, age_band=age_band)
    if triggers.get("suggest_checkin"):
        alerts.append(
            WellnessAlert(
                alert_type="checkin_reminder",
                severity="info",
                title=load_alert_text("checkin_reminder_title", locale),
                body=load_alert_text("checkin_reminder_body", locale),
                action="open_checkin",
            )
        )
    if triggers.get("suggest_phq_lite") and age_band != "child":
        alerts.append(
            WellnessAlert(
                alert_type="phq_lite_suggested",
                severity="watch",
                title=load_alert_text("phq_suggest_title", locale),
                body=load_alert_text("phq_suggest_body", locale),
                action="open_phq_lite",
            )
        )
    outcome = build_outcome_reminder(store, user_id, locale=locale)
    if outcome:
        alerts.append(
            WellnessAlert(
                alert_type=outcome["alert_type"],
                severity=outcome["severity"],
                title=outcome["title"],
                body=outcome["body"],
                action=outcome["action"],
            )
        )
    settings = store.get_wellness_settings(user_id)
    if str(settings.get("escalation_level") or "") == "L2":
        alerts.append(
            WellnessAlert(
                alert_type="trauma_referral",
                severity="watch",
                title=load_alert_text("trauma_referral_title", locale),
                body=load_alert_text("trauma_referral_body", locale),
                action="open_referral",
            )
        )
    if not store.get_wellness_checkin(user_id, date.today().isoformat()):
        hour = int(settings.get("daily_reminder_hour") or 19)
        alerts.append(
            WellnessAlert(
                alert_type="daily_checkin",
                severity="info",
                title=load_push_message("checkin_evening", locale),
                body=load_alert_text("daily_checkin_body", locale, hour=hour),
                action="open_checkin",
            )
        )
    return alerts


def log_alert(
    store: Any,
    user_id: str,
    *,
    alert_type: str,
    severity: str,
    action_taken: str,
) -> Dict[str, Any]:
    return store.save_wellness_alert_log(
        user_id,
        alert_type=alert_type,
        severity=severity,
        action_taken=action_taken,
        created_at=datetime.utcnow().isoformat(),
    )


def build_family_dashboard(
    store: Any,
    teen_user_id: str,
    *,
    locale: str = "ru",
) -> Dict[str, Any]:
    """Aggregate only if teen enabled parent_share_aggregate."""
    settings = store.get_wellness_settings(teen_user_id)
    if int(settings.get("parent_share_aggregate") or 0) != 1:
        return {
            "shared": False,
            "reason": "teen_opt_out",
            "aggregate": None,
        }
    rows = store.list_wellness_checkins(teen_user_id, days=7)
    moods = [r.get("mood_score") for r in rows if r.get("mood_score") is not None]
    avg_mood = round(sum(moods) / len(moods), 1) if moods else None
    streak = low_mood_streak_days(store, teen_user_id, days=7)
    esc = evaluate_escalation("", days_low_mood=streak)
    mood_trend = family_mood_trend_down_from_i18n(locale=locale, days=streak) if streak >= 2 else None
    return {
        "shared": True,
        "aggregate": {
            "days_with_checkin": len(rows),
            "avg_mood_score": avg_mood,
            "low_mood_streak_days": streak,
            "escalation_hint": esc.level if esc.level in ("L2", "L3") else "L0",
            "message": family_dashboard_message_from_i18n(locale=locale),
            "mood_trend_label": mood_trend,
        },
    }
