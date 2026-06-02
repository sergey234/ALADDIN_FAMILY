# -*- coding: utf-8 -*-
"""p2-15 / p2-30 / p2-31 / reflective guards."""

from __future__ import annotations

import os
import sys
from datetime import datetime, timedelta

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from security.services.ai_platform.companion_store import CompanionStore
from security.services.ai_platform.wellness_insights import save_insight_from_exercise
from security.services.ai_platform.wellness_pillar_session import (
    apply_pillar_selection,
    end_pillar_session,
)
from security.services.ai_platform.wellness_outcome_followup import (
    needs_outcome_followup,
    adjust_pillar_after_outcome,
    apply_outcome_pillar_adjustment,
)
from security.services.ai_platform.wellness_session_recap import build_session_recap
from security.services.ai_platform.wellness_reflective_guards import assert_reflective_allowed
from security.services.ai_platform.wellness_reflective_modes import resolve_reflective_mode
from security.services.ai_platform.wellness_reflective_prompt import build_reflective_prompt_block
from security.services.ai_platform.wellness_outcomes import record_outcome


@pytest.fixture
def store(tmp_path):
    os.environ["COMPANION_DB_PATH"] = str(tmp_path / "flow.db")
    return CompanionStore(db_path=tmp_path / "flow.db")


def test_pillar_session_lock(store):
    uid = "u_sess"
    r1 = apply_pillar_selection(store, uid, "cognitive", age_band="teen")
    assert r1.ok
    r2 = apply_pillar_selection(store, uid, "humanistic", age_band="teen")
    assert not r2.ok
    assert r2.reason == "pillar_session_locked"
    r3 = apply_pillar_selection(
        store, uid, "humanistic", age_band="teen", force_switch=True
    )
    assert r3.ok
    end_pillar_session(store, uid)


def test_recap_continuity(store):
    uid = "u_cont"
    save_insight_from_exercise(
        store,
        uid,
        pillar="humanistic",
        answers=[{"step": 1, "text": "устал после школы"}],
        locale="ru",
    )
    recap = build_session_recap(store, uid, age_band="teen", locale="ru")
    assert recap["continuity_message"]
    assert "школ" in recap["continuity_message"]


def test_outcome_24h_due(store):
    uid = "u_out24"
    old = (datetime.utcnow() - timedelta(hours=30)).isoformat()
    store.upsert_wellness_settings(uid, last_session_completed_at=old)
    assert needs_outcome_followup(store, uid)


def test_outcome_adjust_pillar(store):
    uid = "u_adj"
    new = adjust_pillar_after_outcome(
        helpful=1,
        current_pillar="cognitive",
        age_band="teen",
        mood_score=2,
        stress_level=4,
    )
    assert new in ("humanistic", "behavioral", "jung")
    record_outcome(store, uid, pillar="cognitive", helpful=1, age_band="teen")
    adj = apply_outcome_pillar_adjustment(
        store, uid, helpful=1, pillar="cognitive", age_band="teen"
    )
    assert adj.get("adjusted_pillar")


def test_reflective_guards():
    g = assert_reflective_allowed(
        "deep_explore",
        age_band="child",
        reflective_enabled=True,
        jung_enabled=True,
    )
    assert not g.allowed
    g2 = assert_reflective_allowed(
        "presence",
        age_band="teen",
        reflective_enabled=True,
    )
    assert g2.allowed
    assert g2.redirect_pillar == "humanistic"


def test_reflective_mode_resolve_and_prompt():
    assert resolve_reflective_mode("разбери глубоко") == "deep_explore"
    block, guard = build_reflective_prompt_block(
        mode="single_question",
        age_band="teen",
        locale="ru",
        reflective_enabled=True,
        jung_enabled=True,
    )
    assert guard.allowed
    assert "[WELLNESS REFLECTIVE]" in block
