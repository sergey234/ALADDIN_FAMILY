# -*- coding: utf-8 -*-
"""p2-16 / p2-17 / p2-18 / p2-33 — insights, emotion, plan, mood routing."""

from __future__ import annotations

import os
import sys

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from security.services.ai_platform.companion_store import CompanionStore
from security.services.ai_platform.wellness_emotion_agent import (
    infer_mood_score_from_text,
    resolve_mood_score,
)
from security.services.ai_platform.wellness_insights_extractor import (
    extract_insight_from_exercise,
    save_extracted_insight,
)
from security.services.ai_platform.wellness_mood_routing import suggest_pillar_with_mood_fallback
from security.services.ai_platform.wellness_plan_agent import build_wellness_plan


@pytest.fixture
def store(tmp_path):
    os.environ["COMPANION_DB_PATH"] = str(tmp_path / "agents.db")
    return CompanionStore(db_path=tmp_path / "agents.db")


def test_insights_extractor():
    ext = extract_insight_from_exercise(
        [{"text": "Мысль: всё плохо"}],
        pillar="cognitive",
        locale="ru",
    )
    assert ext.observe_text
    assert ext.next_step_text
    assert "мысл" in ext.understood.lower() or "отделил" in ext.understood.lower()


def test_emotion_regex_fallback():
    assert infer_mood_score_from_text("мне очень тревожно") == 2
    assert infer_mood_score_from_text("I'm happy today") == 4
    score, src = resolve_mood_score(
        checkin={"mood_emoji": "unknown_xyz"},
        notes="грустно и одиноко",
    )
    assert score == 1
    assert src == "notes_regex"


def test_mood_routing_suggest(store):
    from datetime import date

    uid = "u_route"
    store.upsert_wellness_checkin(
        uid,
        day=date.today().isoformat(),
        mood_emoji="sad",
        mood_score=1,
        stress_level=4,
        source="test",
        age_band="teen",
    )
    out = suggest_pillar_with_mood_fallback(
        store, uid, age_band="teen", jung_enabled=False
    )
    assert out["suggested_pillar"] == "humanistic"
    assert out["mood_source"] == "checkin"


def test_plan_agent():
    plan = build_wellness_plan(
        phq_score=12,
        suggested_pillar="cognitive",
        locale="ru",
    )
    assert plan["severity"] == "moderate"
    assert len(plan["steps"]) >= 2


def test_save_extracted_insight(store):
    uid = "u_ins"
    from security.services.ai_platform.wellness_insights_extractor import ExtractedInsight

    row = save_extracted_insight(
        store,
        uid,
        ExtractedInsight("ok", "observe", "next", source="exercise"),
        pillar="behavioral",
    )
    assert row.get("observe_text")
