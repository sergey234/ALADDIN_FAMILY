# -*- coding: utf-8 -*-
"""Pillar 1 — cognitive / CBT-lite prompt supplement (p2-01)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .wellness_age_policy import normalize_age_band
from .wellness_pillar_prompt_util import (
    age_band_note,
    format_pillar_block,
    hero_flavor_line,
    locale_key,
    pack_llm_rules,
    pack_principles,
)
from .wellness_prompt_builder import load_pillar_pack

if TYPE_CHECKING:
    from .wellness_prompt_builder import WellnessPrefixContext

PILLAR = "cognitive"
_PACK_VERSION = "v1"


def build_cognitive_prompt_block(ctx: "WellnessPrefixContext") -> str:
    pack = load_pillar_pack(PILLAR, ctx.locale, _PACK_VERSION)
    loc = locale_key(ctx.locale)
    band = normalize_age_band(ctx.age_band)
    esc = (ctx.escalation or "L0").upper()

    lines: list[str] = []
    lines.append(f"pillar_prompt={PILLAR}")
    lines.append(f"mode={'child_ultra_lite' if band == 'child' else 'teen_full'}")

    rules = pack_llm_rules(pack, loc)
    if rules:
        lines.append(f"tone={rules}")

    for i, p in enumerate(pack_principles(pack, loc)[:3], start=1):
        lines.append(f"principle_{i}={p}")

    note = age_band_note(pack, band, loc)
    if note:
        lines.append(f"age_note={note}")

    if band == "child":
        if loc == "en":
            lines.append(
                "instruction=Simple words only: what happened, what you think, "
                "one gentle question. No thought-record steps or school terms."
            )
        else:
            lines.append(
                "instruction=Только простые слова: что случилось, что думаешь, "
                "один мягкий вопрос. Без шагов дневника мыслей и без терминов школ."
            )
    elif ctx.exercise and ctx.exercise.exercise_id:
        lines.append(
            "instruction=Перефразируй только текущий шаг упражнения; один вопрос."
            if loc == "ru"
            else "instruction=Rephrase only the current exercise step; one question."
        )
    else:
        if loc == "en":
            lines.append(
                "instruction=Separate fact vs guess vs feeling; one micro-question."
            )
        else:
            lines.append(
                "instruction=Отдели факт от догадки и чувства; один микро-вопрос."
            )

    if esc in ("L2", "L3"):
        lines.append("crisis_mode=no_deep_analysis")

    flavor = hero_flavor_line(
        pack,
        character_id=ctx.character_id,
        locale=ctx.locale,
        escalation=esc,
    )
    if flavor:
        lines.append(f"hero_voice={flavor}")

    return format_pillar_block("[WELLNESS COGNITIVE]", lines)
