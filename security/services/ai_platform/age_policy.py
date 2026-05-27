# -*- coding: utf-8 -*-
"""Age-band rules for companion (characters, voice, memory)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass(frozen=True)
class AgeBandRules:
    allowed_characters: Tuple[str, ...]
    voice_enabled: bool
    memory_requires_parent_consent: bool
    max_message_length: int


_RULES: Dict[str, AgeBandRules] = {
    "child": AgeBandRules(
        allowed_characters=("unicorn",),
        voice_enabled=True,
        memory_requires_parent_consent=True,
        max_message_length=500,
    ),
    "teen": AgeBandRules(
        allowed_characters=("unicorn", "aladdin", "genie"),
        voice_enabled=True,
        memory_requires_parent_consent=True,
        max_message_length=1500,
    ),
    "parent": AgeBandRules(
        allowed_characters=("unicorn", "aladdin", "genie"),
        voice_enabled=True,
        memory_requires_parent_consent=False,
        max_message_length=2000,
    ),
    "senior": AgeBandRules(
        allowed_characters=("aladdin",),
        voice_enabled=True,
        memory_requires_parent_consent=False,
        max_message_length=2000,
    ),
    "adult_app": AgeBandRules(
        allowed_characters=("unicorn", "aladdin", "genie"),
        voice_enabled=True,
        memory_requires_parent_consent=False,
        max_message_length=8000,
    ),
}


def get_age_band_rules(age_band: str) -> AgeBandRules:
    return _RULES.get(age_band, _RULES["parent"])


def filter_characters_for_age(
    characters: List[Dict[str, Any]],
    age_band: str,
    parent_consent: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    rules = get_age_band_rules(age_band)
    consent = parent_consent or {}
    if not consent.get("child_can_use_companion", True) and age_band in ("child", "teen"):
        return []
    allowed = set(rules.allowed_characters)
    consent_chars = consent.get("allowed_characters")
    if isinstance(consent_chars, list) and consent_chars:
        allowed &= {c for c in consent_chars if c in allowed}
    return [c for c in characters if c.get("id") in allowed]


def companion_access_allowed(age_band: str, parent_consent: Optional[Dict[str, Any]] = None) -> bool:
    consent = parent_consent or {}
    if age_band in ("child", "teen") and consent.get("child_can_use_companion") is False:
        return False
    return consent.get("companion", True) is not False


def memory_allowed(age_band: str, parent_consent: Optional[Dict[str, Any]] = None) -> bool:
    rules = get_age_band_rules(age_band)
    consent = parent_consent or {}
    if rules.memory_requires_parent_consent:
        return bool(consent.get("memory_enabled"))
    return bool(consent.get("memory_enabled", True))
