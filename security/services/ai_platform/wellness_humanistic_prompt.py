# -*- coding: utf-8 -*-
"""Pillar 3 — humanistic / presence prompt supplement (p2-07)."""

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

PILLAR = "humanistic"
_PACK_VERSION = "v1"


def build_humanistic_prompt_block(ctx: "WellnessPrefixContext") -> str:
    pack = load_pillar_pack(PILLAR, ctx.locale, _PACK_VERSION)
    loc = locale_key(ctx.locale)
    band = normalize_age_band(ctx.age_band)
    esc = (ctx.escalation or "L0").upper()

    lines: list[str] = []
    lines.append(f"pillar_prompt={PILLAR}")
    lines.append(f"mode={'child_presence' if band == 'child' else 'full_lite'}")

    rules = pack_llm_rules(pack, loc)
    if rules:
        lines.append(f"tone={rules}")

    for i, p in enumerate(pack_principles(pack, loc)[:3], start=1):
        lines.append(f"principle_{i}={p}")

    if band == "child":
        if loc == "en":
            lines.append(
                "instruction=Stay close without analyzing thoughts or habits. "
                "Offer calm presence or one breath; no advice unless asked."
            )
        else:
            lines.append(
                "instruction=Будь рядом без разбора мыслей и привычек. "
                "Спокойное присутствие или одно дыхание; совет — только если просят."
            )
    elif ctx.exercise and ctx.exercise.exercise_id in (
        "grounding_54321",
        "box_breathing",
        "dbt_stop",
    ):
        lines.append(
            "instruction=Веди только текущий шаг заземления/дыхания; без анализа."
            if loc == "ru"
            else "instruction=Guide only the current grounding/breath step; no analysis."
        )
    else:
        if loc == "en":
            lines.append(
                "instruction=Validate first; one gentle grounding or breath line max."
            )
        else:
            lines.append(
                "instruction=Сначала признай чувство; максимум одна строка про заземление или дыхание."
            )

    if esc in ("L2", "L3"):
        lines.append("crisis_mode=presence_and_safety_only")

    flavor = hero_flavor_line(
        pack,
        character_id=ctx.character_id,
        locale=ctx.locale,
        escalation=esc,
    )
    if flavor:
        lines.append(f"hero_voice={flavor}")

    return format_pillar_block("[WELLNESS HUMANISTIC]", lines)
