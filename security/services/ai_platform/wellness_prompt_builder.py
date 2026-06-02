# -*- coding: utf-8 -*-
"""Build [WELLNESS v1] prefix from Knowledge Pack (p1-26 / ADR)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

_KNOWLEDGE_ROOT = Path(__file__).resolve().parent / "wellness_knowledge"


@dataclass(frozen=True)
class WellnessExerciseContext:
    exercise_id: str = ""
    step_index: int = 0
    step_total: int = 0


@dataclass(frozen=True)
class WellnessPrefixContext:
    primary_pillar: str
    escalation: str = "L0"
    age_band: str = "teen"
    exercise: Optional[WellnessExerciseContext] = None
    character_id: str = "aladdin"
    locale: str = "ru"
    pack_version: str = ""
    pack_folder: str = "v1"


def load_pillar_pack(
    pillar: str,
    locale: str = "ru",
    version: str = "v1",
) -> Dict[str, Any]:
    path = _KNOWLEDGE_ROOT / pillar / version / "pack.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"Knowledge pack not found: {path}")
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Invalid pack format: {path}")
    return data


def _hero_flavor_key(pack: Dict[str, Any], character_id: str) -> str:
    flavors = pack.get("hero_flavor") or {}
    entry = flavors.get(character_id) or flavors.get("aladdin") or {}
    if isinstance(entry, dict):
        return str(entry.get("flavor_key") or "mentor_short")
    return "mentor_short"


def _step_instruction(
    pack: Dict[str, Any],
    ctx: WellnessPrefixContext,
) -> str:
    if not ctx.exercise or not ctx.exercise.exercise_id:
        rules = pack.get("llm_rules") or {}
        if ctx.locale == "en":
            return str(rules.get("en") or rules.get("ru") or "")
        return str(rules.get("ru") or "")
    exercises = pack.get("exercises") or {}
    ex = exercises.get(ctx.exercise.exercise_id) or {}
    steps = ex.get("steps") or []
    idx = max(0, ctx.exercise.step_index - 1)
    if idx >= len(steps):
        return ""
    step = steps[idx] or {}
    instr = step.get("instruction") or {}
    if ctx.locale == "en":
        return str(instr.get("en") or instr.get("ru") or "")
    return str(instr.get("ru") or "")


def build_wellness_prefix(
    ctx: WellnessPrefixContext,
) -> str:
    pack = load_pillar_pack(
        ctx.primary_pillar,
        locale=ctx.locale,
        version=ctx.pack_folder or "v1",
    )
    pack_version = ctx.pack_version or str(pack.get("pack_version") or f"{ctx.primary_pillar}_v1.0")
    allowed = ",".join(pack.get("allowed_topics") or [])
    forbidden = ",".join(pack.get("forbidden_concepts") or [])

    exercise_id = ""
    exercise_step = ""
    if ctx.exercise and ctx.exercise.exercise_id:
        exercise_id = ctx.exercise.exercise_id
        if ctx.exercise.step_total:
            exercise_step = f"{ctx.exercise.step_index}/{ctx.exercise.step_total}"

    instruction = _step_instruction(pack, ctx)
    hero_flavor = _hero_flavor_key(pack, ctx.character_id)

    lines = [
        "[WELLNESS v1]",
        f"primary_pillar={ctx.primary_pillar}",
        f"escalation={ctx.escalation}",
        f"age_band={ctx.age_band}",
        f"pack_version={pack_version}",
        f"hero_flavor={hero_flavor}",
        f"allowed_topics={allowed}",
        f"forbidden={forbidden}",
    ]
    if exercise_id:
        lines.append(f"exercise={exercise_id}")
    if exercise_step:
        lines.append(f"exercise_step={exercise_step}")
    if instruction:
        lines.append(f"instruction={instruction.strip()}")

    return "\n".join(lines) + "\n"


def build_pillar_prompt_block(
    ctx: WellnessPrefixContext,
    *,
    jung_enabled: bool = False,
) -> str:
    """Age- and pillar-specific supplement (p2-01 / p2-07 / p2-09)."""
    pillar = (ctx.primary_pillar or "").strip().lower()
    if pillar == "cognitive":
        from .wellness_cognitive_prompt import build_cognitive_prompt_block

        return build_cognitive_prompt_block(ctx)
    if pillar == "humanistic":
        from .wellness_humanistic_prompt import build_humanistic_prompt_block

        return build_humanistic_prompt_block(ctx)
    if pillar == "jung":
        from .wellness_jung_prompt import build_jung_prompt_block

        return build_jung_prompt_block(ctx, jung_enabled=jung_enabled)
    return ""
