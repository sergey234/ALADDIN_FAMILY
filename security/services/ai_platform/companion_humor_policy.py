# -*- coding: utf-8 -*-
"""Humor SSOT loader and hint builder (hero-x-01…03, hero-x-44)."""

from __future__ import annotations

import hashlib
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

_TIERS_PATH = (
    Path(__file__).resolve().parent / "companion_knowledge" / "humor" / "v1" / "tiers.yaml"
)

_KEYWORD_OVERRIDE = re.compile(
    r"грустн|печал|тоск|плачу|мне плохо|хочу умереть|боюсь|не рад|"
    r"sad|depressed|want to die|scared|feel bad",
    re.I,
)
_CRISIS_KEYWORD = re.compile(
    r"самоуб|покончить с собой|режу себя|хочу умереть|навредить себе|"
    r"kill myself|suicide",
    re.I,
)


@lru_cache(maxsize=1)
def load_humor_tiers() -> Dict[str, Any]:
    """Load humor tiers YAML (SSOT)."""
    with open(_TIERS_PATH, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data


def apply_keyword_mood_override(message: str, mood: str) -> str:
    """hero-x-44: keyword → sad/comfort_needed for humor hard stop."""
    msg = message or ""
    if _CRISIS_KEYWORD.search(msg):
        return "comfort_needed"
    if _KEYWORD_OVERRIDE.search(msg):
        return "sad"
    return mood


def _escalation_blocks_humor(escalation: str) -> bool:
    esc = (escalation or "L0").upper()
    matrix = load_humor_tiers().get("escalation_matrix") or {}
    rule = matrix.get(esc) or matrix.get("L0")
    return rule == "no_humor" or esc in ("L1", "L2", "L3")


def humor_hard_stop(
    mood: str,
    escalation: str = "L0",
    *,
    age_band: str = "parent",
    message: str = "",
) -> bool:
    tiers = load_humor_tiers()
    stops = tiers.get("humor_hard_stops") or {}
    mood = apply_keyword_mood_override(message, mood)
    if mood in tuple(stops.get("moods") or ()):
        return True
    if _escalation_blocks_humor(escalation):
        return True
    if age_band == "child":
        return False
    return False


def _freq_key(mood: str, escalation: str) -> str:
    esc = (escalation or "L0").upper()
    m = (mood or "neutral").lower()
    return f"{esc}_{m}"


def humor_injection_probability(
    character_id: str,
    mood: str,
    escalation: str = "L0",
    *,
    humor_preference: str = "normal",
    genie_ab_scale: float = 1.0,
) -> float:
    tiers = load_humor_tiers()
    char_freq = (tiers.get("humor_frequency") or {}).get(character_id) or {}
    key = _freq_key(mood, escalation)
    prob = 0.0
    if key in char_freq:
        prob = float(char_freq[key])
    else:
        fallback = f"{(escalation or 'L0').upper()}_{mood or 'neutral'}"
        if fallback in char_freq:
            prob = float(char_freq[fallback])
        elif character_id == "genie" and escalation.upper() == "L0":
            prob = 0.35
    if character_id == "genie":
        prob *= genie_ab_scale
    if (humor_preference or "normal").strip().lower() == "less":
        prob *= 0.45
    return max(0.0, min(1.0, prob))


def should_inject_humor(
    character_id: str,
    mood: str,
    escalation: str = "L0",
    *,
    age_band: str = "parent",
    message: str = "",
    turn_key: str = "",
    humor_preference: str = "normal",
    genie_ab_scale: float = 1.0,
) -> bool:
    """Deterministic humor turn gate (not stand-up every reply)."""
    if humor_hard_stop(mood, escalation, age_band=age_band, message=message):
        return False
    prob = humor_injection_probability(
        character_id,
        mood,
        escalation,
        humor_preference=humor_preference,
        genie_ab_scale=genie_ab_scale,
    )
    if prob <= 0:
        return False
    if not turn_key:
        return prob >= 0.5
    digest = hashlib.sha256(turn_key.encode("utf-8")).hexdigest()
    bucket = int(digest[:8], 16) / 0xFFFFFFFF
    return bucket < prob


def sarcasm_allowed(character_id: str, age_band: str) -> bool:
    tiers = load_humor_tiers()
    sarcasm = tiers.get("sarcasm") or {}
    if age_band == "child" or sarcasm.get("child") is False:
        return False
    rule = sarcasm.get(character_id)
    return rule in ("situational_pg_only", "rare_dry_wit")


def humor_hint_for_character(
    character_id: str,
    mood: str,
    escalation: str = "L0",
    *,
    age_band: str = "parent",
    message: str = "",
    turn_key: str = "",
    humor_preference: str = "normal",
    genie_ab_scale: float = 1.0,
) -> str:
    """Build humor hint for intent router / companion chat."""
    tiers = load_humor_tiers()
    templates = tiers.get("hint_templates") or {}
    mood = apply_keyword_mood_override(message, mood)

    if humor_hard_stop(mood, escalation, age_band=age_band, message=message):
        return str(templates.get("hard_stop") or "Без шуток — только эмпатия и поддержка.")

    inject = should_inject_humor(
        character_id,
        mood,
        escalation,
        age_band=age_band,
        message=message,
        turn_key=turn_key,
        humor_preference=humor_preference,
        genie_ab_scale=genie_ab_scale,
    )

    if character_id == "genie":
        if inject:
            hint = str(templates.get("genie_with_humor") or "")
            if sarcasm_allowed(character_id, age_band):
                return hint
            return hint.replace("иногда лёгкий сарказм про ситуацию (не про человека). ", "")
        return str(
            templates.get("genie_without_humor")
            or "Джин: тёплый ответ без шутки — чередуй, не стендап."
        )

    if character_id == "unicorn":
        if inject and mood == "playful":
            return str(templates.get("unicorn_with_humor") or "")
        if inject:
            return str(templates.get("unicorn_neutral") or "")
        return ""

    if character_id == "aladdin":
        if inject and mood == "playful":
            return str(templates.get("aladdin_with_humor") or templates.get("aladdin_playful") or "")
        if inject:
            return str(templates.get("aladdin_playful") or "")
        return ""

    return ""


def resolve_escalation_level(message: str) -> str:
    """Map wellness escalation to L0–L3 for humor gating."""
    from security.services.ai_platform.wellness_escalation import evaluate_escalation

    return evaluate_escalation(message or "").level
