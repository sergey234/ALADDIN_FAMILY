# -*- coding: utf-8 -*-
"""p2-28 — age/crisis/Jung gates (unit, no server)."""

from __future__ import annotations

import os
import sys

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from security.services.ai_platform.wellness_age_policy import (
    can_use_phq_lite,
    can_use_full_assessments,
)
from security.services.ai_platform.wellness_exercise_engine import list_catalog
from security.services.ai_platform.wellness_four_pillars import suggest_pillar
from security.services.ai_platform.wellness_pillar_guard import assert_single_pillar
from security.services.ai_platform.wellness_assessments import score_phq9
from security.services.ai_platform.wellness_escalation import evaluate_escalation


def test_child_no_phq_lite():
    assert not can_use_phq_lite("child")


def test_child_no_full_assessments():
    assert not can_use_full_assessments("child")


def test_child_no_jung_catalog_even_if_flag():
    assert list_catalog("jung", age_band="child", jung_enabled=True) == []


def test_teen_has_phq9_access():
    assert can_use_full_assessments("teen")


def test_phq9_q9_sets_crisis_flag():
    r = score_phq9([0] * 8 + [2])
    assert r.crisis_flag is True


def test_crisis_escalation_not_l0():
    esc = evaluate_escalation("хочу умереть причинить себе вред")
    assert esc.level in ("L2", "L3")


def test_crisis_suggest_humanistic_pillar():
    p = suggest_pillar(age_band="teen", mood_score=2, stress_level=5, escalation_level="L3")
    assert p == "humanistic"


def test_pillar_guard_blocks_jung_when_session_cognitive():
    g = assert_single_pillar(session_pillar="cognitive", requested_pillar="jung", age_band="teen")
    assert not g.ok
