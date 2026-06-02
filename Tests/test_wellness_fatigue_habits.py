# -*- coding: utf-8 -*-
"""p2-32 / p2-05 / p2-06 — fatigue, habits, MBI-lite."""

from __future__ import annotations

import os
import sys

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from security.services.ai_platform.companion_store import CompanionStore
from security.services.ai_platform.wellness_age_policy import can_use_mbi_lite
from security.services.ai_platform.wellness_assessments import score_mbi_lite
from security.services.ai_platform.wellness_habit_plans import create_habit_plan, list_habit_plans
from security.services.ai_platform.wellness_outcome_followup import apply_outcome_pillar_adjustment
from security.services.ai_platform.wellness_pillar_fatigue import (
    FATIGUE_THRESHOLD,
    evaluate_pillar_fatigue,
    record_outcome_for_fatigue,
)
from security.services.ai_platform.wellness_session_recap import build_session_recap


@pytest.fixture
def store(tmp_path):
    os.environ["COMPANION_DB_PATH"] = str(tmp_path / "fatigue.db")
    return CompanionStore(db_path=tmp_path / "fatigue.db")


def test_fatigue_streak_and_recap(store):
    uid = "u_fat"
    pillar = "cognitive"
    for _ in range(FATIGUE_THRESHOLD):
        record_outcome_for_fatigue(store, uid, pillar=pillar, helpful=2)
    fatigue = evaluate_pillar_fatigue(
        store, uid, age_band="teen", jung_enabled=False
    )
    assert fatigue["fatigued"] is True
    assert fatigue["suggested_pillar"] != pillar
    recap = build_session_recap(store, uid, age_band="teen", jung_enabled=False)
    assert recap["pillar_fatigue"]["fatigued"] is True


def test_fatigue_resets_on_helpful(store):
    uid = "u_reset"
    pillar = "humanistic"
    for _ in range(3):
        record_outcome_for_fatigue(store, uid, pillar=pillar, helpful=2)
    record_outcome_for_fatigue(store, uid, pillar=pillar, helpful=5)
    fatigue = evaluate_pillar_fatigue(store, uid, age_band="teen")
    assert fatigue["fatigued"] is False
    assert int(fatigue["streak_count"]) == 0


def test_outcome_apply_records_fatigue(store):
    uid = "u_out"
    store.upsert_wellness_settings(uid, primary_pillar="cognitive")
    result = apply_outcome_pillar_adjustment(
        store, uid, helpful=1, pillar="cognitive", age_band="teen"
    )
    assert "fatigue" in result
    assert result["fatigue"]["fatigue_streak_count"] >= 1


def test_habit_plans(store):
    uid = "u_habit"
    row = create_habit_plan(store, uid, if_then="Если устал, то 5 минут дыхания")
    assert row["if_then"]
    plans = list_habit_plans(store, uid)
    assert len(plans) == 1
    with pytest.raises(ValueError):
        create_habit_plan(store, uid, if_then="  ")


def test_mbi_lite_age_and_score():
    assert can_use_mbi_lite("parent") is True
    assert can_use_mbi_lite("child") is False
    result = score_mbi_lite([2, 2, 2, 2, 2], locale="ru")
    assert result.score == 10
    assert result.disclaimer
