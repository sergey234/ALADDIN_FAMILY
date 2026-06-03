# -*- coding: utf-8
"""Vedic / universal wisdom snippet picker (hero-x-10…12, hero-x-15)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import yaml

_VEDIC_ROOT = Path(__file__).resolve().parent / "companion_knowledge" / "vedic" / "v1"
_AGE_ORDER = ("child", "teen", "parent", "senior")
_RELIGION_WORDS = re.compile(
    r"бог|храм|молитв|вера|религи|ислам|христиан|будд|инду|"
    r"god|temple|prayer|religion|hindu|buddh",
    re.I,
)


@dataclass(frozen=True)
class WisdomSnippet:
    id: str
    theme: str
    ru_paraphrase: str
    en_paraphrase: str
    snippet_tier: str
    tone: str


def _age_rank(band: str) -> int:
    b = (band or "teen").lower()
    return _AGE_ORDER.index(b) if b in _AGE_ORDER else 1


def _snippet_age_min(snippet: Dict[str, Any]) -> str:
    return str(snippet.get("age_band_min") or "teen").lower()


def _snippet_allowed_for_age(snippet: Dict[str, Any], age_band: str) -> bool:
    return _age_rank(age_band) >= _age_rank(_snippet_age_min(snippet))


@lru_cache(maxsize=1)
def load_wisdom_snippets() -> Tuple[Dict[str, Any], Tuple[Dict[str, Any], ...]]:
    merged: List[Dict[str, Any]] = []
    meta: Dict[str, Any] = {}
    for name in ("wisdom.yaml", "gita_lite.yaml", "mahabharata_lite.yaml"):
        path = _VEDIC_ROOT / name
        if not path.is_file():
            continue
        with open(path, encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        if not meta and data.get("forbidden_user_words"):
            meta["forbidden_user_words"] = list(data.get("forbidden_user_words") or [])
        merged.extend(list(data.get("snippets") or []))
    return meta, tuple(merged)


def _domain_themes(domain: str) -> List[str]:
    d = (domain or "general").lower()
    mapping = {
        "school": ["school", "exam_stress", "anxiety"],
        "feelings": ["feelings", "anxiety", "grief"],
        "wellness": ["feelings", "anxiety", "sleep"],
        "loneliness": ["loneliness", "friends", "grief"],
        "work": ["work", "money_worries", "parenting_stress"],
        "family": ["family", "parenting_stress", "relationships"],
        "friends": ["friends", "internet_drama"],
        "health_feelings": ["sleep", "health_feelings", "tired"],
        "daily_life": ["daily_life", "motivation"],
        "general": ["motivation", "feelings", "daily_life"],
    }
    return mapping.get(d, [d, "feelings", "daily_life"])


def _text_has_religion_words(text: str) -> bool:
    return bool(_RELIGION_WORDS.search(text or ""))


def pick_wisdom_snippet(
    character_id: str,
    domain: str,
    mood: str,
    age_band: str,
    *,
    locale: str = "ru",
    used_snippet_ids: Optional[Sequence[str]] = None,
    turn_count: int = 0,
) -> Optional[WisdomSnippet]:
    """
    Pick one wisdom snippet for prompt injection.
    hero-x-15: skip used ids; frequency cap 1 per 5 turns handled by caller.
    """
    if mood in ("sad", "lonely", "comfort_needed", "anxious"):
        return None

    meta, snippets = load_wisdom_snippets()
    used = set(used_snippet_ids or [])
    themes = _domain_themes(domain)
    char = character_id if character_id in ("unicorn", "aladdin", "genie") else "aladdin"
    band = (age_band or "teen").lower()

    candidates: List[Dict[str, Any]] = []
    for sn in snippets:
        if sn.get("id") in used:
            continue
        chars = sn.get("characters") or []
        if char not in chars:
            continue
        if not _snippet_allowed_for_age(sn, band):
            continue
        tier = str(sn.get("snippet_tier") or "vedic_lite")
        if band == "child" and tier != "universal":
            continue
        if char in ("aladdin", "genie") and band != "child" and tier == "universal":
            continue
        sn_themes = [str(t).lower() for t in (sn.get("themes") or [])]
        if not any(t in sn_themes for t in themes):
            continue
        ru = str(sn.get("ru_paraphrase") or "")
        if not ru or _text_has_religion_words(ru):
            continue
        candidates.append(sn)

    if not candidates:
        return None

    # Stable pick by turn_count for testability
    idx = turn_count % len(candidates)
    chosen = candidates[idx]
    theme = str((chosen.get("themes") or ["general"])[0])
    loc = (locale or "ru").lower()[:2]
    ru = str(chosen.get("ru_paraphrase") or "")
    en = str(chosen.get("en_paraphrase") or ru)
    text = en if loc == "en" else ru
    return WisdomSnippet(
        id=str(chosen.get("id") or ""),
        theme=theme,
        ru_paraphrase=text,
        en_paraphrase=en,
        snippet_tier=str(chosen.get("snippet_tier") or ""),
        tone=str(chosen.get("tone") or "calm_mentor"),
    )


def format_wisdom_block(snippet: WisdomSnippet) -> str:
    return (
        f"[WISDOM v1] theme={snippet.theme} tier={snippet.snippet_tier} "
        f"tone={snippet.tone} snippet={snippet.ru_paraphrase}\n"
    )


def wisdom_frequency_allowed(turn_count: int, *, cap_every: int = 5) -> bool:
    """hero-x-15: at most one wisdom inject per N turns."""
    if turn_count <= 0:
        return True
    return turn_count % cap_every == 0
