# -*- coding: utf-8 -*-
"""Session insights for recap continuity (p2-30)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def save_insight_from_exercise(
    store: Any,
    user_id: str,
    *,
    pillar: str,
    answers: List[Dict[str, Any]],
    locale: str = "ru",
) -> Dict[str, Any]:
    from .wellness_insights_extractor import (
        extract_insight_from_exercise,
        save_extracted_insight,
    )

    extracted = extract_insight_from_exercise(
        answers, pillar=pillar, locale=locale
    )
    return save_extracted_insight(store, user_id, extracted, pillar=pillar)


def get_last_wellness_insight(store: Any, user_id: str) -> Optional[Dict[str, Any]]:
    return store.get_last_wellness_insight(user_id)


def continuity_message(
    insight: Optional[Dict[str, Any]],
    *,
    locale: str = "ru",
) -> Optional[str]:
    if not insight:
        return None
    observe = str(insight.get("observe_text") or "").strip()
    if not observe:
        return None
    from security.services.ai_platform.wellness_i18n_loader import continuity_prefix_message

    return continuity_prefix_message(locale=locale, observe_text=observe)
