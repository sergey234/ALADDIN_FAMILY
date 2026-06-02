# -*- coding: utf-8 -*-
"""p2-29 — idle nudge after 2 days without check-in."""

from __future__ import annotations

import os
import sys
from datetime import date, timedelta

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from security.services.ai_platform.companion_store import CompanionStore
from security.services.ai_platform.wellness_nudge import (
    days_since_last_checkin,
    evaluate_idle_nudge,
    dismiss_idle_nudge,
    IDLE_NUDGE_THRESHOLD_DAYS,
)
from security.services.ai_platform.wellness_triggers import evaluate_triggers


@pytest.fixture
def store(tmp_path):
    os.environ["COMPANION_DB_PATH"] = str(tmp_path / "nudge.db")
    return CompanionStore(db_path=tmp_path / "nudge.db")


def test_idle_nudge_after_two_days(store):
    uid = "u_idle"
    old = (date.today() - timedelta(days=3)).isoformat()
    store.upsert_wellness_checkin(uid, day=old, mood_emoji="ok", mood_score=3)
    n = evaluate_idle_nudge(store, uid, locale="ru")
    assert n["show_idle_nudge"] is True
    assert n["idle_days"] >= IDLE_NUDGE_THRESHOLD_DAYS


def test_no_nudge_after_recent_checkin(store):
    uid = "u_active"
    store.upsert_wellness_checkin(uid, day=date.today().isoformat(), mood_emoji="ok", mood_score=4)
    n = evaluate_idle_nudge(store, uid)
    assert n["show_idle_nudge"] is False


def test_dismiss_hides_until_tomorrow(store):
    uid = "u_dismiss"
    old = (date.today() - timedelta(days=5)).isoformat()
    store.upsert_wellness_checkin(uid, day=old, mood_emoji="sad", mood_score=1)
    assert evaluate_idle_nudge(store, uid)["show_idle_nudge"] is True
    dismiss_idle_nudge(store, uid)
    assert evaluate_idle_nudge(store, uid)["show_idle_nudge"] is False


def test_triggers_includes_idle_fields(store):
    uid = "u_trig"
    out = evaluate_triggers(store, uid, age_band="teen", locale="ru")
    assert "show_idle_nudge" in out
    assert "idle_days" in out
