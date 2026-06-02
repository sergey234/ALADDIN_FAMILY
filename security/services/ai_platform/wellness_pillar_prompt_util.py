# -*- coding: utf-8 -*-
"""Shared helpers for pillar prompt modules (p2-01 / p2-07 / p2-09)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .wellness_age_policy import normalize_age_band
from .wellness_prompt_builder import load_pillar_pack


def locale_key(locale: str) -> str:
    return "en" if (locale or "ru").lower()[:2] == "en" else "ru"


def localized_text(block: Any, locale: str) -> str:
    """Resolve ru/en string or {ru:, en:} dict."""
    loc = locale_key(locale)
    if isinstance(block, dict):
        return str(block.get(loc) or block.get("ru") or block.get("en") or "").strip()
    return str(block or "").strip()


def pack_principles(pack: Dict[str, Any], locale: str) -> List[str]:
    principles = pack.get("principles") or {}
    loc = locale_key(locale)
    items = principles.get(loc) or principles.get("ru") or []
    if isinstance(items, list):
        return [str(x).strip() for x in items if str(x).strip()]
    return []


def pack_llm_rules(pack: Dict[str, Any], locale: str) -> str:
    rules = pack.get("llm_rules") or {}
    return localized_text(rules, locale)


def hero_flavor_line(
    pack: Dict[str, Any],
    *,
    character_id: str,
    locale: str,
    escalation: str = "L0",
) -> str:
    flavors = pack.get("hero_flavor") or {}
    entry = flavors.get(character_id) or flavors.get("aladdin") or {}
    text = ""
    if isinstance(entry, dict):
        if entry.get("ru") or entry.get("en"):
            text = localized_text(entry, locale)
        else:
            nested = entry.get(locale_key(locale)) or entry.get("ru") or entry.get("en")
            text = localized_text(nested, locale)
    if escalation.upper() in ("L2", "L3") and locale_key(locale) == "ru":
        text = (text + " Без шуток и без углубления анализа.").strip()
    elif escalation.upper() in ("L2", "L3"):
        text = (text + " No jokes; do not deepen analysis.").strip()
    return text


def age_band_note(pack: Dict[str, Any], age_band: str, locale: str) -> str:
    band = normalize_age_band(age_band)
    ab = pack.get("age_band") or {}
    entry = ab.get(band) if isinstance(ab, dict) else None
    if not isinstance(entry, dict):
        return ""
    note = entry.get(f"note_{locale_key(locale)}") or entry.get("note_ru") or ""
    return str(note).strip()


def format_pillar_block(header: str, lines: List[str]) -> str:
    body = [ln for ln in lines if ln]
    if not body:
        return ""
    return header + "\n" + "\n".join(body) + "\n"
