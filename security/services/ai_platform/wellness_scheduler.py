# -*- coding: utf-8 -*-
"""Wellness reminder scheduler hooks (p2-25). Cron calls /api/wellness/scheduler/run."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

from security.services.ai_platform.wellness_alerts import build_user_alerts, log_alert


def run_daily_reminders(
    store: Any,
    *,
    target_hour: int = 19,
    locale: str = "ru",
) -> Dict[str, Any]:
    """
    MVP: scan users with wellness consent who have no check-in today after target_hour (UTC).
  Real push delivery = iOS/APNs later (p18-11).
    """
    now = datetime.utcnow()
    if now.hour < target_hour:
        return {"ok": True, "skipped": True, "reason": "before_reminder_hour"}

    # MVP: no full user scan table — endpoint returns payload for current user only.
    return {
        "ok": True,
        "skipped": False,
        "target_hour": target_hour,
        "note": "per_user_via_build_user_alerts",
    }


def reminders_for_user(
    store: Any,
    user_id: str,
    *,
    age_band: str = "teen",
    locale: str = "ru",
    target_hour: int = 19,
) -> List[Dict[str, Any]]:
    now = datetime.utcnow()
    if now.hour < target_hour:
        return []
    alerts = build_user_alerts(store, user_id, age_band=age_band, locale=locale)
    out: List[Dict[str, Any]] = []
    for a in alerts:
        if a.alert_type in ("daily_checkin", "checkin_reminder", "outcome_24h"):
            log_alert(
                store,
                user_id,
                alert_type=a.alert_type,
                severity=a.severity,
                action_taken="scheduled_reminder",
            )
            out.append(
                {
                    "alert_type": a.alert_type,
                    "title": a.title,
                    "body": a.body,
                    "action": a.action,
                }
            )
    return out
