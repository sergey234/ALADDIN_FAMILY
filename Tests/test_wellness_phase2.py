# -*- coding: utf-8 -*-
"""Wellness Phase 2 unit tests."""

from __future__ import annotations

import os
import sys
import tempfile

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from security.services.ai_platform.companion_store import CompanionStore
from security.services.ai_platform.wellness_four_pillars import suggest_pillar
from security.services.ai_platform.wellness_assessments import score_phq9, phq9_schema
from security.services.ai_platform.wellness_exercise_engine import (
    list_catalog,
    start_exercise,
    advance_exercise,
)
from security.services.ai_platform.wellness_session_recap import build_session_recap
from security.services.ai_platform.wellness_outcomes import record_outcome


@pytest.fixture
def store(tmp_path):
    db = tmp_path / "wellness_p2.db"
    os.environ["COMPANION_DB_PATH"] = str(db)
    return CompanionStore(db_path=str(db))


def test_suggest_pillar_stress_humanistic(store):
    p = suggest_pillar(age_band="teen", mood_score=3, stress_level=5, escalation_level="L0")
    assert p == "humanistic"


def test_suggest_pillar_child_behavioral(store):
    p = suggest_pillar(age_band="child", mood_score=4, stress_level=2)
    assert p in ("behavioral", "humanistic")


def test_child_no_jung_catalog(store):
    items = list_catalog("jung", age_band="child", jung_enabled=True)
    assert items == []


def test_thought_record_flow(store):
    uid = "u_p2"
    session = start_exercise(
        store, uid, pillar="cognitive", exercise_id="thought_record", age_band="teen"
    )
    assert session.step_index == 1
    assert session.step_total == 5
    assert session.hint
    for i in range(5):
        session = advance_exercise(
            store, uid, session.id, answer=f"step{i}", locale="ru"
        )
    assert session.completed is True


def test_behavioral_pack_catalog(store):
    items = list_catalog("behavioral", age_band="teen")
    ids = {x["exercise_id"] for x in items}
    assert "micro_habit" in ids
    assert "if_then_plan" in ids


def test_session_recap(store):
    from datetime import date

    uid = "u_recap"
    today = date.today().isoformat()
    store.upsert_wellness_checkin(
        uid,
        day=today,
        mood_emoji="sad",
        mood_score=2,
        stress_level=4,
    )
    recap = build_session_recap(store, uid, age_band="teen", locale="ru")
    assert recap["suggested_pillar"] == "humanistic"
    assert "message" in recap


def test_phq9_crisis_flag():
    r = score_phq9([0, 0, 0, 0, 0, 0, 0, 0, 2])
    assert r.crisis_flag is True
    assert r.suggest_professional is True


def test_phq9_schema_nine_questions():
    s = phq9_schema(locale="ru")
    assert len(s["questions"]) == 9
    assert s["max_score"] == 27


def test_gad7_score_severe():
    from security.services.ai_platform.wellness_assessments import score_gad7

    r = score_gad7([3, 3, 3, 2, 2, 2, 2])
    assert r.score >= 15
    assert r.suggest_professional


def test_outcome_record(store):
    uid = "u_out"
    result = record_outcome(
        store, uid, pillar="humanistic", helpful=4, age_band="teen"
    )
    assert result.helpful == 4
    rows = store.list_wellness_outcomes(uid)
    assert len(rows) == 1
