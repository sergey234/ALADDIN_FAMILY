# -*- coding: utf-8 -*-
"""Proactive nudge after 2+ days without check-in (p2-29)."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict

from security.services.ai_platform.wellness_i18n_loader import load_push_message

IDLE_NUDGE_THRESHOLD_DAYS = 2


def days_since_last_checkin(store: Any, user_id: str) -> int:
    rows = store.list_wellness_checkins(user_id, days=60)
    if not rows:
        return 999
    last_day = str(rows[0].get("day") or "")
    try:
        last = date.fromisoformat(last_day)
    except ValueError:
        return 999
    return max(0, (date.today() - last).days)


def evaluate_idle_nudge(
    store: Any,
    user_id: str,
    *,
    locale: str = "ru",
) -> Dict[str, Any]:
    idle_days = days_since_last_checkin(store, user_id)
    settings = store.get_wellness_settings(user_id)
    last_nudge_day = str(settings.get("last_idle_nudge_day") or "")
    today = date.today().isoformat()
    show = idle_days >= IDLE_NUDGE_THRESHOLD_DAYS and last_nudge_day != today

    title = load_push_message("nudge_idle_2d", locale, part="title")
    body = load_push_message("nudge_idle_2d", locale, part="body")

    return {
        "idle_days": idle_days if idle_days < 900 else None,
        "show_idle_nudge": show,
        "nudge_type": "idle_2d" if show else None,
        "title": title if show else None,
        "body": body if show else None,
        "push_message": load_push_message("nudge_idle_2d", locale) if show else None,
        "action": "open_checkin" if show else None,
        "threshold_days": IDLE_NUDGE_THRESHOLD_DAYS,
    }


def dismiss_idle_nudge(store: Any, user_id: str) -> Dict[str, Any]:
    today = date.today().isoformat()
    settings = store.upsert_wellness_settings(user_id, last_idle_nudge_day=today)
    return {"ok": True, "dismissed_day": today, "settings": settings}
