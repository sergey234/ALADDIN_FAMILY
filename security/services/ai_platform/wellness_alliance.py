# -*- coding: utf-8 -*-
"""Therapeutic alliance score + hero emotion mapping (p2-35)."""

from __future__ import annotations

from typing import Any, Dict, Optional

DEFAULT_ALLIANCE = 50
MIN_SCORE = 0
MAX_SCORE = 100


def hero_emotion_from_score(score: int) -> str:
    """Avatar tone hint: calm | warm | concerned | celebrate."""
    s = max(MIN_SCORE, min(MAX_SCORE, int(score)))
    if s >= 75:
        return "celebrate"
    if s >= 55:
        return "warm"
    if s >= 35:
        return "calm"
    return "concerned"


def get_alliance_state(store: Any, user_id: str) -> Dict[str, Any]:
    settings = store.get_wellness_settings(user_id)
    score = int(settings.get("alliance_score") or DEFAULT_ALLIANCE)
    emotion = str(settings.get("hero_emotion") or hero_emotion_from_score(score))
    return {
        "alliance_score": score,
        "hero_emotion": emotion,
        "trust_band": _trust_band(score),
    }


def _trust_band(score: int) -> str:
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def bump_alliance(
    store: Any,
    user_id: str,
    delta: int,
    *,
    reason: str = "",
) -> Dict[str, Any]:
    current = int(store.get_wellness_settings(user_id).get("alliance_score") or DEFAULT_ALLIANCE)
    new_score = max(MIN_SCORE, min(MAX_SCORE, current + int(delta)))
    emotion = hero_emotion_from_score(new_score)
    store.update_wellness_alliance(
        user_id,
        alliance_score=new_score,
        hero_emotion=emotion,
    )
    return {
        "alliance_score": new_score,
        "hero_emotion": emotion,
        "delta": int(delta),
        "reason": reason,
        "trust_band": _trust_band(new_score),
    }


def apply_alliance_for_checkin(store: Any, user_id: str) -> Dict[str, Any]:
    return bump_alliance(store, user_id, +2, reason="checkin")


def apply_alliance_for_outcome(store: Any, user_id: str, *, helpful: int) -> Dict[str, Any]:
    if helpful >= 4:
        return bump_alliance(store, user_id, +5, reason="outcome_positive")
    if helpful <= 2:
        return bump_alliance(store, user_id, -2, reason="outcome_low")
    return bump_alliance(store, user_id, +1, reason="outcome_neutral")


def apply_alliance_for_exercise_done(store: Any, user_id: str) -> Dict[str, Any]:
    return bump_alliance(store, user_id, +3, reason="exercise_complete")


def apply_alliance_for_trauma_trigger(store: Any, user_id: str) -> Dict[str, Any]:
    return bump_alliance(store, user_id, -5, reason="trauma_safety")


def apply_alliance_for_crisis(store: Any, user_id: str) -> Dict[str, Any]:
    return bump_alliance(store, user_id, -10, reason="crisis")
