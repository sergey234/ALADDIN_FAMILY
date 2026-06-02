# -*- coding: utf-8 -*-
"""
Pillar 4 — Jung lite prompt supplement (p2-09).

Gate: FEATURE_WELLNESS_JUNG=1 (PO checklist p0-08; disable flag on server if App Review requests).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .wellness_age_policy import normalize_age_band
from .wellness_pillar_prompt_util import (
    format_pillar_block,
    hero_flavor_line,
    locale_key,
    pack_llm_rules,
    pack_principles,
)
from .wellness_prompt_builder import load_pillar_pack

if TYPE_CHECKING:
    from .wellness_prompt_builder import WellnessPrefixContext

PILLAR = "jung"
_PACK_VERSION = "v1"


def jung_prompt_allowed(*, jung_enabled: bool) -> bool:
    """Requires env flag FEATURE_WELLNESS_JUNG=1."""
    return bool(jung_enabled)


def build_jung_prompt_block(
    ctx: "WellnessPrefixContext",
    *,
    jung_enabled: bool = False,
) -> str:
    if not jung_prompt_allowed(jung_enabled=jung_enabled):
        return ""

    pack = load_pillar_pack(PILLAR, ctx.locale, _PACK_VERSION)
    loc = locale_key(ctx.locale)
    band = normalize_age_band(ctx.age_band)
    esc = (ctx.escalation or "L0").upper()

    lines: list[str] = []
    lines.append(f"pillar_prompt={PILLAR}")
    lines.append(f"clinical_gate=FEATURE_WELLNESS_JUNG")

    if band == "child":
        lines.append("mode=child_metaphor_only")
        if loc == "en":
            lines.append(
                "instruction=Fairy-tale metaphor only: inner hero or feeling as image. "
                "No dream analysis, no predictions, no archetype labels."
            )
        else:
            lines.append(
                "instruction=Только сказочная метафора: герой внутри или чувство как образ. "
                "Без разбора снов, предсказаний и ярлыков архетипов."
            )
    else:
        lines.append("mode=teen_metaphor_lite")
        rules = pack_llm_rules(pack, loc)
        if rules:
            lines.append(f"tone={rules}")
        for i, p in enumerate(pack_principles(pack, loc)[:2], start=1):
            lines.append(f"principle_{i}={p}")
        if ctx.exercise and ctx.exercise.exercise_id == "dream_note_lite":
            lines.append(
                "instruction=Только шаг дневника сна; символы как метафоры «для тебя сейчас»."
                if loc == "ru"
                else "instruction=Dream journal step only; symbols as metaphors for you now."
            )
        else:
            if loc == "en":
                lines.append(
                    "instruction=One metaphor question; never predict the future or diagnose."
                )
            else:
                lines.append(
                    "instruction=Один вопрос через метафору; не предсказывай будущее и не ставь диагноз."
                )

    lines.append("forbidden=predictions,fortune_telling,therapy_claims,trauma_deep_dive")

    if esc in ("L2", "L3"):
        lines.append("crisis_mode=no_symbol_work")

    flavor = hero_flavor_line(
        pack,
        character_id=ctx.character_id,
        locale=ctx.locale,
        escalation=esc,
    )
    if flavor:
        lines.append(f"hero_voice={flavor}")

    return format_pillar_block("[WELLNESS JUNG]", lines)
