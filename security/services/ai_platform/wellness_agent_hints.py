# -*- coding: utf-8 -*-
"""
p3-02 — Agent registry prompt hints (single LLM turn, not COMPANION_USE_ORCHESTRATOR).

Wellness agents guide tone/focus inside one Companion call; separate multi-agent
orchestration is `orchestrator.py` + COMPANION_USE_ORCHESTRATOR (unrelated).
"""

from __future__ import annotations

from typing import Dict, List

_AGENT_HINTS: Dict[str, Dict[str, str]] = {
    "cbt_coach_agent": {
        "ru": "Фокус: мысли-ловушки, факты vs догадки, один переформулирующий вопрос.",
        "en": "Focus: thought traps, facts vs guesses, one reframing question.",
    },
    "habit_coach_agent": {
        "ru": "Фокус: один маленький шаг или if-then, без больших планов.",
        "en": "Focus: one small step or if-then, no big plans.",
    },
    "presence_coach_agent": {
        "ru": "Фокус: принятие, тёплое присутствие, без советов и оценок.",
        "en": "Focus: acceptance, warm presence, no advice or judgment.",
    },
    "symbol_coach_agent": {
        "ru": "Фокус: метафоры и символы, без предсказаний и диагнозов.",
        "en": "Focus: metaphors and symbols, no predictions or diagnoses.",
    },
    "reflective_agent": {
        "ru": "Фокус: мягкое зеркало — один открытый вопрос для размышления.",
        "en": "Focus: gentle mirror — one open reflection question.",
    },
    "clinical_screening_agent": {
        "ru": "Фокус: короткий скрининг PHQ-lite, напомни что это не диагноз.",
        "en": "Focus: brief PHQ-lite screening; remind it's not a diagnosis.",
    },
    "crisis_agent": {
        "ru": "Кризис L3: эмпатия, взрослый/112, без углубления в терапию.",
        "en": "Crisis L3: empathy, trusted adult/112, no deep therapy.",
    },
    "self_harm_detection_agent": {
        "ru": "Безопасность: не обещай заменить людей; направь к живой помощи.",
        "en": "Safety: don't promise to replace people; guide to live help.",
    },
    "family_bridge_agent": {
        "ru": "Мягко предложи написать близкому человеку, без давления.",
        "en": "Gently suggest messaging someone close, without pressure.",
    },
}


def build_wellness_agents_block(agents: List[str], *, locale: str = "ru") -> str:
    """Append to wellness prefix so LLM follows active agent roles."""
    if not agents:
        return ""
    loc = (locale or "ru").lower()[:2]
    lines = ["[WELLNESS AGENTS ACTIVE]"]
    for agent_id in agents:
        hints = _AGENT_HINTS.get(agent_id) or {}
        text = hints.get(loc) or hints.get("ru") or ""
        if text:
            lines.append(f"- {agent_id}: {text}")
        else:
            lines.append(f"- {agent_id}")
    return "\n".join(lines) + "\n"
