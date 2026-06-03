# -*- coding: utf-8 -*-
"""hero-x-68 — Genie humor A/B (max vs high cap)."""

from __future__ import annotations

import hashlib
from typing import Literal

GenieHumorVariant = Literal["max", "high"]


def genie_humor_ab_variant(user_id: str, *, enabled: bool) -> GenieHumorVariant:
    """Deterministic bucket when FEATURE_GENIE_HUMOR_AB is on."""
    if not enabled:
        return "max"
    uid = (user_id or "anon").strip()
    digest = hashlib.sha256(f"genie-humor-ab:{uid}".encode("utf-8")).hexdigest()
    bucket = int(digest[:8], 16) % 2
    return "high" if bucket else "max"


def genie_humor_probability_scale(variant: GenieHumorVariant) -> float:
    """high = ~70% of max humor frequency (data-driven cap experiment)."""
    return 0.70 if variant == "high" else 1.0
