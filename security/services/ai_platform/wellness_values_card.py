# -*- coding: utf-8 -*-
"""ACT values card — optional humanistic micro-exercise (p3-07)."""

from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional


DEFAULT_VALUES = (
    {"id": "kindness", "label_key": "wellness_values_kindness"},
    {"id": "growth", "label_key": "wellness_values_growth"},
    {"id": "connection", "label_key": "wellness_values_connection"},
    {"id": "calm", "label_key": "wellness_values_calm"},
    {"id": "health", "label_key": "wellness_values_health"},
)


def build_values_card_schema(*, locale: str = "ru") -> Dict[str, Any]:
    from security.services.ai_platform.wellness_i18n_loader import normalize_wellness_locale

    loc = normalize_wellness_locale(locale)
    title = "Что для меня важно на этой неделе?" if loc == "ru" else "What matters to me this week?"
    subtitle = (
        "Выберите 1–2 ценности — без оценок"
        if loc == "ru"
        else "Pick 1–2 values — no grades"
    )
    return {
        "title": title,
        "title_key": "wellness_values_card_title",
        "subtitle": subtitle,
        "subtitle_key": "wellness_values_card_subtitle",
        "values": list(DEFAULT_VALUES),
        "max_pick": 2,
        "week_of": date.today().isocalendar()[1],
    }


def save_values_card(
    store: Any,
    user_id: str,
    *,
    value_ids: List[str],
    note: Optional[str] = None,
) -> Dict[str, Any]:
    picked = [v for v in value_ids if v][:2]
    observe = ",".join(picked)
    if note:
        observe = f"{observe}|{note[:200]}"
    row = store.save_wellness_insight(
        user_id,
        pillar="humanistic",
        observe_text=observe,
        next_step_text=date.today().isoformat(),
        source="values_card",
    )
    return {"ok": True, "values_card": {"value_ids": picked, "note": note, "insight_id": row.get("id")}}


def get_values_card(store: Any, user_id: str) -> Dict[str, Any]:
    rows = store.list_wellness_insights(user_id, limit=5)
    card_rows = [r for r in rows if (r.get("source") or "") == "values_card"]
    latest = card_rows[0] if card_rows else {}
    value_ids: List[str] = []
    note = ""
    if latest:
        obs = str(latest.get("observe_text") or "")
        if "|" in obs:
            ids_part, note = obs.split("|", 1)
            value_ids = [x for x in ids_part.split(",") if x]
        else:
            value_ids = [x for x in obs.split(",") if x]
    return {"values_card": {"value_ids": value_ids, "note": note, "saved_at": latest.get("next_step_text")}}
