# -*- coding: utf-8 -*-
"""Wellness four pillars — enum and age gating (p1-07)."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Set


class WellnessPillar(str, Enum):
    COGNITIVE = "cognitive"
    BEHAVIORAL = "behavioral"
    HUMANISTIC = "humanistic"
    JUNG = "jung"


_CHILD_ALLOWED: Set[str] = {
    WellnessPillar.HUMANISTIC.value,
    WellnessPillar.BEHAVIORAL.value,
}

_ALL: List[str] = [p.value for p in WellnessPillar]


def pillars_for_age_band(age_band: str) -> List[str]:
    band = (age_band or "teen").lower()
    if band == "child":
        return list(_CHILD_ALLOWED)
    return list(_ALL)


def is_pillar_allowed(pillar: str, age_band: str) -> bool:
    return pillar in pillars_for_age_band(age_band)


def normalize_pillar(pillar: Optional[str], age_band: str) -> Optional[str]:
    if not pillar:
        return None
    p = pillar.strip().lower()
    if p not in _ALL:
        return None
    if not is_pillar_allowed(p, age_band):
        return None
    return p


def suggest_pillar(
    *,
    age_band: str,
    mood_score: Optional[int] = None,
    stress_level: Optional[int] = None,
    escalation_level: str = "L0",
    jung_enabled: bool = False,
) -> str:
    """
    Phase 2 auto-routing (p2-14). Deterministic; no LLM.
    """
    band = (age_band or "teen").lower()
    allowed = pillars_for_age_band(band)
    esc = (escalation_level or "L0").upper()
    if esc in ("L2", "L3"):
        if WellnessPillar.HUMANISTIC.value in allowed:
            return WellnessPillar.HUMANISTIC.value
        return allowed[0]

    stress = stress_level if stress_level is not None else 3
    mood = mood_score if mood_score is not None else 3

    if band == "child":
        if stress >= 4 and WellnessPillar.HUMANISTIC.value in allowed:
            return WellnessPillar.HUMANISTIC.value
        return WellnessPillar.BEHAVIORAL.value

    if stress >= 4 or mood <= 2:
        if WellnessPillar.HUMANISTIC.value in allowed:
            return WellnessPillar.HUMANISTIC.value

    if mood <= 2 and WellnessPillar.COGNITIVE.value in allowed:
        return WellnessPillar.COGNITIVE.value

    if stress <= 2 and mood >= 4 and WellnessPillar.BEHAVIORAL.value in allowed:
        return WellnessPillar.BEHAVIORAL.value

    if (
        jung_enabled
        and WellnessPillar.JUNG.value in allowed
        and mood >= 3
        and stress <= 3
    ):
        return WellnessPillar.JUNG.value

    return WellnessPillar.HUMANISTIC.value if WellnessPillar.HUMANISTIC.value in allowed else allowed[0]
