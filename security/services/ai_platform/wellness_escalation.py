# -*- coding: utf-8 -*-
"""Wellness escalation L0–L3 (p1-20). Ethics L3 overrides via companion_ethics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .companion_ethics import evaluate_companion_ethics
from .wellness_trauma_referral import detect_trauma_keywords

_LEVELS = ("L0", "L1", "L2", "L3")


@dataclass(frozen=True)
class EscalationResult:
    level: str
    reason: str
    actions: List[str]


def evaluate_escalation(
    message: str,
    *,
    phq_lite_score: Optional[int] = None,
    days_low_mood: int = 0,
) -> EscalationResult:
    ethics = evaluate_companion_ethics(message or "")
    if ethics.crisis or ethics.level == "L3":
        return EscalationResult(
            level="L3",
            reason="crisis_ethics",
            actions=["call_112", "tell_trusted_adult", "block_deep_modes"],
        )

    trauma_hit, _ = detect_trauma_keywords(message or "")
    if trauma_hit:
        return EscalationResult(
            level="L2",
            reason="trauma_keywords",
            actions=["referral_specialist", "stop_jung_deep", "open_referral_sheet"],
        )

    if phq_lite_score is not None and phq_lite_score >= 10:
        return EscalationResult(
            level="L2",
            reason="phq_lite_high",
            actions=["referral_map", "suggest_professional"],
        )

    if days_low_mood >= 3:
        return EscalationResult(
            level="L1",
            reason="low_mood_streak",
            actions=["offer_phq_lite"],
        )

    if ethics.level == "L2":
        return EscalationResult(
            level="L2",
            reason="ethics_l2",
            actions=["social_bridge", "referral_soft"],
        )

    return EscalationResult(level="L0", reason="default", actions=["pillar_session"])
