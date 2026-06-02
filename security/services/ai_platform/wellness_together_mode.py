# -*- coding: utf-8 -*-
"""Together Mode — shared breathing session metadata (p2-44)."""

from __future__ import annotations

from typing import Any, Dict

from security.services.ai_platform.wellness_i18n_loader import together_session_from_i18n

DEFAULT_DURATION_SEC = 180


def build_together_session(
    *,
    age_band: str = "parent",
    locale: str = "ru",
    duration_sec: int = DEFAULT_DURATION_SEC,
) -> Dict[str, Any]:
    payload = together_session_from_i18n(
        age_band=age_band,
        locale=locale,
        duration_sec=duration_sec,
    )
    if payload:
        return payload
    loc = (locale or "ru").lower()[:2]
    band = (age_band or "parent").lower()
    is_parent = band in ("parent", "senior", "adult_app")
    return {
        "title_key": "wellness_together_title",
        "intro_key": "wellness_together_parent_intro" if is_parent else "wellness_together_child_intro",
        "title": "Together" if loc == "en" else "Вместе",
        "intro": "",
        "duration_sec": max(60, min(600, int(duration_sec))),
        "breath_in_sec": 4,
        "breath_out_sec": 4,
        "steps": [],
        "exercise_id": "box_breathing",
        "pillar": "humanistic",
    }
