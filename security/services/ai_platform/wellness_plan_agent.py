# -*- coding: utf-8 -*-
"""Lightweight wellness plan after assessments (p2-18)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def build_wellness_plan(
    *,
    age_band: str = "teen",
    phq_score: Optional[int] = None,
    gad_score: Optional[int] = None,
    mbi_score: Optional[int] = None,
    suggested_pillar: str = "humanistic",
    locale: str = "ru",
) -> Dict[str, Any]:
    loc = (locale or "ru").lower()[:2]
    steps: List[str] = []
    severity = "low"

    if phq_score is not None and phq_score >= 15:
        severity = "high"
    elif phq_score is not None and phq_score >= 10:
        severity = "moderate"
    elif gad_score is not None and gad_score >= 10:
        severity = "moderate"
    elif mbi_score is not None and mbi_score >= 10:
        severity = "moderate"

    if loc == "en":
        steps.append("One check-in per day — mood only, no diagnosis.")
        if severity in ("moderate", "high"):
            steps.append("Consider speaking with a specialist — helplines in Trust.")
        if suggested_pillar == "cognitive":
            steps.append("3 days: one thought record when rumination shows up.")
        elif suggested_pillar == "behavioral":
            steps.append("3 days: one if-then micro-step after breakfast.")
        else:
            steps.append("3 days: 2 minutes grounding when stress rises.")
        disclaimer = "Self-help plan, not medical treatment."
    else:
        steps.append("Один check-in в день — только настроение, не диагноз.")
        if severity in ("moderate", "high"):
            steps.append("Имеет смысл поговорить со специалистом — линии в «Безопасность».")
        if suggested_pillar == "cognitive":
            steps.append("3 дня: одна запись мысли, когда накрывает руминация.")
        elif suggested_pillar == "behavioral":
            steps.append("3 дня: один if-then шаг после завтрака.")
        else:
            steps.append("3 дня: 2 минуты заземления, когда растёт стресс.")
        disclaimer = "План самопомощи, не лечение."

    return {
        "severity": severity,
        "suggested_pillar": suggested_pillar,
        "steps": steps,
        "disclaimer": disclaimer,
        "age_band": age_band,
    }
