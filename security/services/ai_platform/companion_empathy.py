# -*- coding: utf-8
"""Empathy validation-first hints (hero-x-40)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import yaml

_MACROS_PATH = (
    Path(__file__).resolve().parent
    / "companion_knowledge"
    / "empathy"
    / "v1"
    / "empathy_macros.yaml"
)


@lru_cache(maxsize=1)
def load_empathy_macros() -> Dict[str, Any]:
    with open(_MACROS_PATH, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def empathy_validation_hint(
    mood: str,
    *,
    age_band: str = "teen",
    locale: str = "ru",
) -> str:
    """Validation-first macro for heavy moods."""
    pack = load_empathy_macros()
    loc = "en" if (locale or "ru").lower()[:2] == "en" else "ru"
    moods = set(pack.get("validation_first_moods") or [])
    m = (mood or "neutral").lower()
    if m not in moods:
        return ""

    macros = pack.get("macros") or {}
    entry = macros.get(m) or macros.get("default") or {}
    line = str(entry.get(loc) or entry.get("ru") or "")

    parts = [line] if line else []
    name_hint = pack.get("name_feeling_hint") or {}
    if m in ("sad", "anxious", "lonely"):
        nh = str(name_hint.get(loc) or name_hint.get("ru") or "")
        if nh:
            parts.append(nh)
    if (age_band or "").lower() == "senior":
        senior = pack.get("senior_pause") or {}
        sp = str(senior.get(loc) or senior.get("ru") or "")
        if sp:
            parts.append(sp)
    return " ".join(parts)
