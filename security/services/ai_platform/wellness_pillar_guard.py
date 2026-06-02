# -*- coding: utf-8 -*-
"""Block mixing wellness pillars in one LLM session (p1-22)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .wellness_four_pillars import normalize_pillar


@dataclass(frozen=True)
class PillarGuardResult:
    ok: bool
    primary_pillar: Optional[str]
    reason: str = ""


def assert_single_pillar(
    *,
    session_pillar: Optional[str],
    requested_pillar: Optional[str],
    age_band: str,
) -> PillarGuardResult:
    req = normalize_pillar(requested_pillar, age_band)
    sess = normalize_pillar(session_pillar, age_band)

    if req and sess and req != sess:
        return PillarGuardResult(
            ok=False,
            primary_pillar=sess,
            reason="pillar_mismatch",
        )

    primary = sess or req
    if primary and not normalize_pillar(primary, age_band):
        return PillarGuardResult(ok=False, primary_pillar=None, reason="pillar_not_allowed")

    return PillarGuardResult(ok=True, primary_pillar=primary)
