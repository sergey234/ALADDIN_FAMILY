# -*- coding: utf-8 -*-
"""Psychology internal KB — [PSYCH v1 internal] for LLM only (hero-x-20, hero-x-21)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

import yaml

_INTERNAL_PATH = (
    Path(__file__).resolve().parent
    / "companion_knowledge"
    / "psychology"
    / "v1"
    / "internal.yaml"
)


@lru_cache(maxsize=1)
def load_psychology_internal() -> Dict[str, Any]:
    with open(_INTERNAL_PATH, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError("invalid psychology internal pack")
    return data


def _locale_key(locale: str) -> str:
    return "en" if (locale or "ru").lower()[:2] == "en" else "ru"


def build_psych_internal_block(
    age_band: str,
    escalation: str = "L0",
    *,
    locale: str = "ru",
) -> str:
    """
    Compressed system block — never shown in API catalog or user UI.
    Skips depth on L2/L3.
    """
    esc = (escalation or "L0").upper()
    if esc in ("L2", "L3"):
        return ""

    pack = load_psychology_internal()
    loc = _locale_key(locale)
    band = (age_band or "teen").lower()
    if band not in ("child", "teen", "parent", "senior"):
        band = "teen"

    ladder: List[str] = []
    for step in pack.get("listening_ladder") or []:
        if not isinstance(step, dict):
            continue
        key = f"user_style_{loc}"
        text = str(step.get(key) or step.get("user_style_ru") or "")
        if text:
            ladder.append(f"{step.get('id')}:{text}")

    playbooks = pack.get("age_band_playbooks") or {}
    pb = playbooks.get(band) or playbooks.get("teen") or {}

    depth = (pack.get("depth_gear") or {}).get(esc) or (pack.get("depth_gear") or {}).get("L0")
    rules = pack.get("user_output_rules") or {}
    output_rule = str(rules.get(loc) or rules.get("ru") or "").strip().replace("\n", " ")

    distortions: List[str] = []
    for label, entry in (pack.get("distortion_labels_internal") or {}).items():
        if not isinstance(entry, dict):
            continue
        hint = str(entry.get(f"user_hint_{loc}") or entry.get("user_hint_ru") or "")
        if hint:
            distortions.append(f"{label}→{hint[:80]}")

    lines = [
        "[PSYCH v1 internal]",
        f"age_band={band}",
        f"escalation={esc}",
        f"depth_gear={depth}",
        f"listening_ladder={' | '.join(ladder[:3])}",
        f"playbook_max_q={pb.get('max_questions', 1)}",
        f"distortions_internal={' ; '.join(distortions[:4])}",
        f"user_output={output_rule[:240]}",
    ]
    return "\n".join(lines) + "\n"
