# -*- coding: utf-8 -*-
"""Weekly meaning prompt — 10 min self-reflection (p2-45)."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any, Dict, Optional

from security.services.ai_platform.wellness_i18n_loader import (
    load_push_message,
    weekly_meaning_from_i18n,
)


def _parse_day(ts: str) -> Optional[date]:
    try:
        return datetime.fromisoformat(ts.replace("Z", "")).date()
    except ValueError:
        return None


def should_show_weekly_meaning(
    store: Any,
    user_id: str,
    *,
    cooldown_days: int = 7,
) -> bool:
    settings = store.get_wellness_settings(user_id)
    last = settings.get("last_weekly_meaning_day")
    if last:
        try:
            last_d = date.fromisoformat(str(last))
            if (date.today() - last_d).days < cooldown_days:
                return False
        except ValueError:
            pass
    insights = store.get_last_wellness_insight(user_id)
    if insights:
        return True
    rows = store.list_wellness_checkins(user_id, days=14)
    return len(rows) >= 3


def build_weekly_meaning(
    store: Any,
    user_id: str,
    *,
    locale: str = "ru",
    age_band: str = "teen",
) -> Dict[str, Any]:
    insight = store.get_last_wellness_insight(user_id)
    observe = str((insight or {}).get("observe_text") or "").strip()
    copy = weekly_meaning_from_i18n(locale=locale, observe_text=observe)
    return {
        "show": should_show_weekly_meaning(store, user_id),
        "title": copy["title"],
        "body": copy["body"],
        "prompt": copy["prompt"],
        "title_key": "wellness_weekly_meaning_title",
        "body_key": "wellness_weekly_meaning_body",
        "push_message": load_push_message("weekly_meaning", locale),
        "suggested_pillar": "jung" if age_band != "child" else "humanistic",
        "duration_minutes": 10,
    }


def mark_weekly_meaning_shown(store: Any, user_id: str) -> Dict[str, Any]:
    return store.update_wellness_misc(
        user_id,
        last_weekly_meaning_day=date.today().isoformat(),
    )
