# -*- coding: utf-8 -*-
"""Post-LLM guard for companion free chat (hero-x-08)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from typing import List, Optional, Tuple

from security.services.ai_platform.wellness_orchestrator import _THERAPY_CLAIM

_PILLARS = ("cognitive", "humanistic", "behavioral", "jung")


@dataclass(frozen=True)
class CompanionGuardResult:
    ok: bool
    text: str
    reason: str = ""


@lru_cache(maxsize=1)
def _forbidden_substrings() -> Tuple[str, ...]:
    from security.services.ai_platform.wellness_prompt_builder import load_pillar_pack

    seen: List[str] = []
    for pillar in _PILLARS:
        for loc in ("ru", "en"):
            pack = load_pillar_pack(pillar, locale=loc)
            phrases = pack.get("forbidden_phrases") or {}
            if isinstance(phrases, dict):
                for lst in phrases.values():
                    if isinstance(lst, list):
                        for p in lst:
                            s = str(p).strip()
                            if s and s not in seen:
                                seen.append(s)
    return tuple(seen)


def scan_companion_forbidden(text: str) -> Optional[str]:
    """Return reason if user-visible forbidden phrase detected."""
    if not text:
        return None
    if _THERAPY_CLAIM.search(text):
        return "therapy_claim"
    for phrase in _forbidden_substrings():
        if phrase and re.search(re.escape(phrase), text, re.I):
            return f"forbidden_phrase:{phrase}"
    extra = re.compile(
        r"психоанализ|я\s+ваш\s+терапевт|я\s+лечу|clinical\s+diagnosis",
        re.I,
    )
    if extra.search(text):
        return "forbidden_clinical"
    return None


def apply_companion_response_guard(
    response_text: str,
    *,
    locale: str = "ru",
) -> CompanionGuardResult:
    """Replace reply if forbidden clinical/therapy language leaks."""
    reason = scan_companion_forbidden(response_text or "")
    if not reason:
        return CompanionGuardResult(ok=True, text=response_text or "")
    loc = (locale or "ru").lower()[:2]
    if loc == "en":
        safe = (
            "I'm here as a caring friend to talk things through — not as a doctor or therapist. "
            "What feels most important right now?"
        )
    else:
        safe = (
            "Я рядом как заботливый друг — помогу разобраться, но не как врач или терапевт. "
            "Что сейчас для тебя самое важное?"
        )
    return CompanionGuardResult(ok=False, text=safe, reason=reason)
