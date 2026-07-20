# -*- coding: utf-8 -*-
"""Fixed wellness guide role — warm self-exploration guide (NOT a therapist).

Versioned by humans. The LLM must NEVER generate this system prompt.
HANDOFF: HANDOFF_WELLNESS_GUIDE_HYBRID_20260720.md (psych-01).
"""

from __future__ import annotations

from typing import Dict, Optional, Tuple

# Bump when role/principles change (human versioning).
GUIDE_ROLE_VERSION = "guide_role_v1.0"

# Session modes — ids align with reflective_modes_v1.json / ReflectiveMode.
GUIDE_MODE_PRESENCE = "presence"
GUIDE_MODE_DEEP = "deep_explore"
GUIDE_MODE_STRUCTURED = "structured_view"  # default
GUIDE_MODE_BLIND = "blind_spots"
GUIDE_MODE_ONE_Q = "single_question"

DEFAULT_GUIDE_MODE = GUIDE_MODE_STRUCTURED

_CHILD_ALLOWED_MODES = frozenset({GUIDE_MODE_PRESENCE})

_FORBIDDEN_ROLE_CLAIMS = (
    "психотерапевт",
    "psychotherapist",
    "психоаналитик",
    "psychoanalyst",
    "20+ лет",
    "20+ years",
    "я лечу",
    "i treat",
    "ставлю диагноз",
    "i diagnose",
    "провожу emdr",
    "conducting emdr",
)

_MODE_INSTRUCTIONS: Dict[str, Dict[str, str]] = {
    GUIDE_MODE_PRESENCE: {
        "ru": "Режим: побудь рядом. Не анализируй глубоко. Дай опору и тепло. Максимум 1 мягкий вопрос.",
        "en": "Mode: stay with me. Do not deep-analyze. Offer support and warmth. At most one gentle question.",
    },
    GUIDE_MODE_DEEP: {
        "ru": "Режим: разбери глубоко. Исследуй бережно, 1–3 вопроса. Без диагнозов и «лечения».",
        "en": "Mode: explore deeply. Inquire gently, 1–3 questions. No diagnoses or treatment claims.",
    },
    GUIDE_MODE_STRUCTURED: {
        "ru": "Режим: взгляд со стороны. Помоги отделить факт / интерпретацию, эмоцию / мысль. Структура, не лекция.",
        "en": "Mode: outside view. Help separate fact vs interpretation, feeling vs thought. Structure, not a lecture.",
    },
    GUIDE_MODE_BLIND: {
        "ru": "Режим: слепые зоны. Мягко покажи возможный паттерн и предложи проверить. Без стыда.",
        "en": "Mode: blind spots. Gently name a possible pattern and invite checking it. No shame.",
    },
    GUIDE_MODE_ONE_Q: {
        "ru": "Режим: только вопрос. Не отвечай советом — задай один сильный мягкий вопрос.",
        "en": "Mode: one question only. Do not advise — ask one strong gentle question.",
    },
}

_ROLE_RU = (
    "Ты — тёплый проводник самоисследования в рамках wellness ALADDIN. "
    "Ты НЕ психотерапевт, НЕ психоаналитик и НЕ ставишь диагнозы. "
    "Ты не «лечишь» и не обещаешь терапию. "
    "Важнее понять, чем быстро исправить. "
    "Создаёшь бережное пространство: живой, внимательный, без нравоучений."
)

_ROLE_EN = (
    "You are a warm self-exploration guide within ALADDIN wellness. "
    "You are NOT a psychotherapist, NOT a psychoanalyst, and you do not diagnose. "
    "You do not «treat» or promise therapy. "
    "Understanding matters more than quick fixes. "
    "You create a careful space: warm, attentive, without lecturing."
)

_PRINCIPLES_RU = (
    "Принципы: (1) сначала исследуй; (2) при сильной эмоции — опора, потом разбор; "
    "(3) 1–3 вопроса за раз; (4) различай факт/интерпретацию и эмоцию/мысль; "
    "(5) осознание ≠ изменение — предлагай маленький шаг; "
    "(6) не романтизируй боль; (7) учитывай сон, нагрузку, контекст жизни; "
    "(8) тело — только мягкий опциональный вопрос, без травма-сессий и EMDR."
)

_PRINCIPLES_EN = (
    "Principles: (1) explore first; (2) if emotion is strong — stabilize, then explore; "
    "(3) 1–3 questions at a time; (4) separate fact/interpretation and feeling/thought; "
    "(5) insight ≠ change — offer a small step; "
    "(6) do not romanticize pain; (7) consider sleep, load, life context; "
    "(8) body — only a gentle optional question; no trauma sessions or EMDR."
)


def _loc(locale: str) -> str:
    return "en" if (locale or "ru").lower()[:2] == "en" else "ru"


def normalize_guide_mode(mode: Optional[str], age_band: str = "teen") -> str:
    raw = (mode or "").strip().lower() or DEFAULT_GUIDE_MODE
    if raw not in _MODE_INSTRUCTIONS:
        raw = DEFAULT_GUIDE_MODE
    band = (age_band or "teen").lower()
    if band == "child" and raw not in _CHILD_ALLOWED_MODES:
        return GUIDE_MODE_PRESENCE
    return raw


def mode_instruction(mode: str, locale: str = "ru") -> str:
    loc = _loc(locale)
    entry = _MODE_INSTRUCTIONS.get(mode) or _MODE_INSTRUCTIONS[DEFAULT_GUIDE_MODE]
    return entry.get(loc) or entry["ru"]


def build_guide_role_block(
    *,
    locale: str = "ru",
    age_band: str = "teen",
    guide_mode: Optional[str] = None,
    escalation: str = "L0",
) -> str:
    """
    Fixed system block for prompt assembler.
    Empty on L2/L3 (crisis path owns the turn).
    """
    esc = (escalation or "L0").upper()
    if esc in ("L2", "L3"):
        return ""

    loc = _loc(locale)
    mode = normalize_guide_mode(guide_mode, age_band=age_band)
    role = _ROLE_EN if loc == "en" else _ROLE_RU
    principles = _PRINCIPLES_EN if loc == "en" else _PRINCIPLES_RU
    instr = mode_instruction(mode, loc)

    lowered = f"{role} {principles}".lower()
    # Positive identity claims only (negations like «НЕ психотерапевт» are required).
    positive_claims = (
        "ты — мой психотерапевт",
        "ты психотерапевт с",
        "you are my psychotherapist",
        "you are a psychotherapist with",
        "я психотерапевт",
        "i am a psychotherapist",
        "провожу emdr",
        "conducting emdr",
    )
    for bad in positive_claims:
        if bad in lowered:
            raise RuntimeError(f"guide role contains forbidden claim: {bad}")

    lines = [
        f"[WELLNESS GUIDE {GUIDE_ROLE_VERSION}]",
        f"age_band={(age_band or 'teen').lower()}",
        f"guide_mode={mode}",
        f"role={role}",
        f"principles={principles}",
        f"session_instruction={instr}",
        "forbidden_user_claims=psychotherapist,psychoanalyst,diagnose,treat,EMDR-session,therapy-promise",
        "note=This block is human-authored and fixed. Do not invent a new system prompt.",
    ]
    return "\n".join(lines) + "\n"


def assert_guide_role_safe_for_tests() -> None:
    """psych-01b helper."""
    for loc in ("ru", "en"):
        block = build_guide_role_block(locale=loc, age_band="teen", guide_mode=DEFAULT_GUIDE_MODE)
        low = block.lower()
        assert "ты — мой психотерапевт" not in low
        assert "you are my psychotherapist" not in low
        assert "проводник" in low or "self-exploration guide" in low
        assert GUIDE_ROLE_VERSION in block
        assert "do not invent a new system prompt" in low or "human-authored" in low


def merge_guide_over_psych(
    *,
    guide_prefix: str,
    psych_prefix: str,
    guide_mode: Optional[str] = None,
    age_band: str = "teen",
    locale: str = "ru",
) -> Tuple[str, str]:
    """
    psych-01c — Guide identity wins; presence / one_question beat PSYCH deepen.

    Returns (guide_prefix, psych_prefix) ready for assembler.
    Does NOT delete PSYCH — only softens technique when mode forbids depth.
    """
    guide = (guide_prefix or "").strip()
    psych = (psych_prefix or "").strip()
    if not guide and not psych:
        return "", ""

    mode = normalize_guide_mode(guide_mode, age_band=age_band)
    loc = _loc(locale)

    # Identity: if psych somehow claims therapist language, strip those lines.
    banned_frags = (
        "психотерапевт",
        "psychotherapist",
        "психоаналитик",
        "psychoanalyst",
        "я лечу",
        "i treat",
        "ставлю диагноз",
        "i diagnose",
        "провожу emdr",
        "conducting emdr",
    )
    if psych:
        kept = []
        for line in psych.splitlines():
            low = line.lower()
            if any(b in low for b in banned_frags):
                continue
            kept.append(line)
        psych = "\n".join(kept).strip()

    # Mode beats deepen: presence / one question → no deepen gear.
    if mode in (GUIDE_MODE_PRESENCE, GUIDE_MODE_ONE_Q) and psych:
        override_ru = (
            "merge_override=presence_or_one_q: no deepen; validate/mirror only; "
            "max 1 gentle question; Guide mode wins over depth_gear."
        )
        override_en = (
            "merge_override=presence_or_one_q: no deepen; validate/mirror only; "
            "max 1 gentle question; Guide mode wins over depth_gear."
        )
        override = override_en if loc == "en" else override_ru
        # Soften: drop deepen hints in psych block text
        lines = []
        for line in psych.splitlines():
            low = line.lower()
            if "depth_gear=deepen" in low or "deepen_one_level" in low:
                lines.append("depth_gear=validate_only_no_analysis")
                continue
            lines.append(line)
        psych = "\n".join(lines).strip()
        if psych:
            psych = psych + "\n" + override
        else:
            psych = override

    if guide and not guide.endswith("\n"):
        guide = guide + "\n"
    if psych and not psych.endswith("\n"):
        psych = psych + "\n"
    return guide, psych


def golden_merged_prefix_for_tests(
    *,
    locale: str = "ru",
    age_band: str = "teen",
    guide_mode: str = GUIDE_MODE_PRESENCE,
) -> str:
    """psych-01c golden: Guide before PSYCH; presence softens deepen."""
    from security.services.ai_platform.companion_psychology import (
        build_psych_internal_block,
    )

    guide = build_guide_role_block(
        locale=locale, age_band=age_band, guide_mode=guide_mode, escalation="L0"
    )
    psych = build_psych_internal_block(age_band, "L0", locale=locale)
    g, p = merge_guide_over_psych(
        guide_prefix=guide,
        psych_prefix=psych,
        guide_mode=guide_mode,
        age_band=age_band,
        locale=locale,
    )
    return g + p
