# -*- coding: utf-8 -*-
"""p2-01 / p2-07 / p2-09 — pillar prompt supplements."""

from __future__ import annotations

import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from security.services.ai_platform.wellness_cognitive_prompt import build_cognitive_prompt_block
from security.services.ai_platform.wellness_humanistic_prompt import build_humanistic_prompt_block
from security.services.ai_platform.wellness_jung_prompt import (
    build_jung_prompt_block,
    jung_prompt_allowed,
)
from security.services.ai_platform.wellness_prompt_builder import (
    WellnessPrefixContext,
    build_pillar_prompt_block,
    build_wellness_prefix,
)


def _ctx(**kwargs) -> WellnessPrefixContext:
    defaults = dict(
        primary_pillar="cognitive",
        escalation="L0",
        age_band="teen",
        character_id="aladdin",
        locale="ru",
    )
    defaults.update(kwargs)
    return WellnessPrefixContext(**defaults)


def test_cognitive_teen_block():
    block = build_cognitive_prompt_block(_ctx(primary_pillar="cognitive"))
    assert "[WELLNESS COGNITIVE]" in block
    assert "mode=teen_full" in block
    assert "hero_voice=" in block


def test_cognitive_child_ultra_lite():
    block = build_cognitive_prompt_block(
        _ctx(primary_pillar="cognitive", age_band="child")
    )
    assert "mode=child_ultra_lite" in block
    assert "дневника мыслей" in block or "thought-record" in block


def test_humanistic_child_presence():
    block = build_humanistic_prompt_block(
        _ctx(primary_pillar="humanistic", age_band="child")
    )
    assert "[WELLNESS HUMANISTIC]" in block
    assert "mode=child_presence" in block


def test_jung_disabled_empty():
    assert not jung_prompt_allowed(jung_enabled=False)
    assert build_jung_prompt_block(_ctx(primary_pillar="jung"), jung_enabled=False) == ""


def test_jung_enabled_metaphor():
    block = build_jung_prompt_block(_ctx(primary_pillar="jung"), jung_enabled=True)
    assert "[WELLNESS JUNG]" in block
    assert "clinical_gate=FEATURE_WELLNESS_JUNG" in block
    assert "forbidden=predictions" in block


def test_jung_child_no_dream_analysis():
    block = build_jung_prompt_block(
        _ctx(primary_pillar="jung", age_band="child"),
        jung_enabled=True,
    )
    assert "mode=child_metaphor_only" in block
    assert "снов" in block or "dream" in block.lower()


def test_build_pillar_prompt_block_router():
    cog = build_pillar_prompt_block(_ctx(primary_pillar="cognitive"))
    assert "[WELLNESS COGNITIVE]" in cog
    jung_off = build_pillar_prompt_block(
        _ctx(primary_pillar="jung"), jung_enabled=False
    )
    assert jung_off == ""


def test_full_prefix_includes_pillar_block():
    ctx = _ctx(primary_pillar="humanistic")
    full = build_wellness_prefix(ctx) + build_pillar_prompt_block(
        ctx, jung_enabled=False
    )
    assert "[WELLNESS v1]" in full
    assert "[WELLNESS HUMANISTIC]" in full
    assert "primary_pillar=humanistic" in full
