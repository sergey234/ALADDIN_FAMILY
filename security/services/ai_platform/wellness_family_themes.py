# -*- coding: utf-8 -*-
"""Parent-facing themes aggregate — no chat text (p2-46)."""

from __future__ import annotations

import re
from typing import Any, Dict, List

from security.services.ai_platform.wellness_i18n_loader import (
    family_theme_label_from_i18n,
    family_theme_label_key,
    family_themes_disclaimer_from_i18n,
)

_THEME_RULES: List[tuple] = [
    ("school", [r"школ", r"урок", r"экзамен", r"homework", r"school"]),
    ("friends", [r"друг", r"однокласс", r"friend", r"bully", r"травл"]),
    ("anxiety", [r"тревож", r"паник", r"anxious", r"worried"]),
    ("sleep", [r"сон", r"не сп", r"sleep", r"устал"]),
    ("family", [r"родител", r"мама", r"папа", r"family", r"дома"]),
    ("mood_low", [r"груст", r"плох", r"sad", r"lonely"]),
]


def _collect_text_blobs(store: Any, teen_user_id: str, *, days: int = 14) -> str:
    parts: List[str] = []
    for row in store.list_wellness_checkins(teen_user_id, days=days):
        if row.get("notes"):
            parts.append(str(row["notes"]))
        if row.get("mood_emoji"):
            parts.append(str(row["mood_emoji"]))
    for row in store.list_wellness_assessments(teen_user_id, limit=5):
        parts.append(str(row.get("severity") or ""))
    return " ".join(parts).lower()


def infer_family_themes(
    store: Any,
    teen_user_id: str,
    *,
    locale: str = "ru",
) -> List[Dict[str, str]]:
    blob = _collect_text_blobs(store, teen_user_id)
    loc = (locale or "ru").lower()[:2]
    found: List[Dict[str, str]] = []
    for theme_id, patterns in _THEME_RULES:
        for pat in patterns:
            if re.search(pat, blob, re.I):
                found.append(
                    {
                        "id": theme_id,
                        "label_key": family_theme_label_key(theme_id),
                        "label": family_theme_label_from_i18n(theme_id, locale=loc),
                    }
                )
                break
    if not found:
        streak = 0
        for row in store.list_wellness_checkins(teen_user_id, days=7):
            if row.get("mood_score") is not None and int(row["mood_score"]) <= 2:
                streak += 1
        if streak >= 2:
            found.append(
                {
                    "id": "mood_low",
                    "label_key": family_theme_label_key("mood_low"),
                    "label": family_theme_label_from_i18n("mood_low", locale=loc),
                }
            )
    return found[:6]


def build_family_themes_payload(
    store: Any,
    teen_user_id: str,
    *,
    locale: str = "ru",
) -> Dict[str, Any]:
    from .wellness_alerts import build_family_dashboard

    dash = build_family_dashboard(store, teen_user_id, locale=locale)
    if not dash.get("shared"):
        return {**dash, "themes": []}
    themes = infer_family_themes(store, teen_user_id, locale=locale)
    return {
        **dash,
        "dashboard_title_key": "wellness_family_dashboard_title",
        "no_transcript_key": "wellness_family_no_transcript",
        "themes": themes,
        "themes_disclaimer": family_themes_disclaimer_from_i18n(locale=locale),
    }
