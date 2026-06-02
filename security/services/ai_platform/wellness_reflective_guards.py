# -*- coding: utf-8 -*-
"""Reflective mode guards — teen/crisis/flags (p2-13)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .wellness_age_policy import normalize_age_band
from .wellness_reflective_modes import ReflectiveMode


@dataclass(frozen=True)
class ReflectiveGuardResult:
    allowed: bool
    reason: str = ""
    redirect_pillar: Optional[str] = None


def assert_reflective_allowed(
    mode: str,
    *,
    age_band: str,
    escalation_level: str = "L0",
    reflective_enabled: bool = False,
    jung_enabled: bool = False,
) -> ReflectiveGuardResult:
    if not reflective_enabled:
        return ReflectiveGuardResult(False, "reflective_disabled")
    band = normalize_age_band(age_band)
    esc = (escalation_level or "L0").upper()
    if esc in ("L2", "L3"):
        return ReflectiveGuardResult(False, "crisis_block_reflective")
    m = (mode or "").strip().lower()
    if m == ReflectiveMode.PRESENCE.value:
        return ReflectiveGuardResult(
            True,
            redirect_pillar="humanistic",
        )
    if band == "child" and m in (
        ReflectiveMode.DEEP_EXPLORE.value,
        ReflectiveMode.BLIND_SPOTS.value,
        ReflectiveMode.STRUCTURED_VIEW.value,
    ):
        return ReflectiveGuardResult(False, "reflective_blocked_child")
    if m == ReflectiveMode.DEEP_EXPLORE.value and not jung_enabled:
        return ReflectiveGuardResult(False, "jung_disabled")
    if m in {e.value for e in ReflectiveMode}:
        return ReflectiveGuardResult(True)
    return ReflectiveGuardResult(False, "unknown_reflective_mode")
