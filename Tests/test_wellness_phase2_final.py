# -*- coding: utf-8 -*-
"""p2-36..48 final phase-2 slice tests."""

from __future__ import annotations

import os
import sys

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from security.services.ai_platform.companion_store import CompanionStore
from security.services.ai_platform.wellness_hub_ab import build_hub_copy, hub_ab_variant
from security.services.ai_platform.wellness_streaks import build_streaks_payload, compute_checkin_streak
from security.services.ai_platform.wellness_together_mode import build_together_session
from security.services.ai_platform.wellness_weekly_meaning import build_weekly_meaning
from security.services.ai_platform.wellness_clinician_export import build_clinician_export
from security.services.ai_platform.wellness_security_fusion import evaluate_security_mood_fusion


@pytest.fixture
def store(tmp_path):
    os.environ["COMPANION_DB_PATH"] = str(tmp_path / "p2final.db")
    return CompanionStore(db_path=tmp_path / "p2final.db")


def test_hub_ab_variant_stable():
    assert hub_ab_variant("user_a") == hub_ab_variant("user_a")
    copy = build_hub_copy("user_a", pillars=["cognitive", "humanistic"], locale="ru")
    assert copy["variant"] in ("control", "b")
    assert len(copy["pillars"]) == 2


def test_streaks(store):
    from datetime import date, timedelta

    uid = "u_str"
    today = date.today()
    for i in range(3):
        day = (today - timedelta(days=i)).isoformat()
        store.upsert_wellness_checkin(
            uid,
            day=day,
            mood_emoji="ok",
            mood_score=3,
            source="test",
            age_band="teen",
        )
    payload = build_streaks_payload(store, uid)
    assert payload["checkin_streak"] >= 3
    assert len(payload["badges"]) == 4


def test_together_and_weekly(store):
    together = build_together_session(age_band="parent", locale="ru")
    assert together["duration_sec"] == 180
    uid = "u_wm"
    store.save_wellness_insight(
        uid,
        pillar="jung",
        observe_text="pause",
        next_step_text="notice",
        source="exercise",
    )
    wm = build_weekly_meaning(store, uid, locale="ru")
    assert wm["show"] is True


def test_clinician_export(store):
    uid = "u_exp"
    store.upsert_wellness_checkin(
        uid,
        day="2026-06-01",
        mood_emoji="sad",
        mood_score=2,
        stress_level=4,
        sleep_hours=6.5,
        source="test",
        age_band="teen",
    )
    doc = build_clinician_export(store, uid, age_band="teen")
    assert doc["checkins_count"] >= 1
    assert "диагноз" in doc["disclaimer"].lower() or "diagnosis" in doc["disclaimer"].lower()


def test_security_fusion(store):
    from datetime import date, timedelta

    uid = "u_fus"
    store.upsert_wellness_settings(uid, parent_share_aggregate=1)
    today = date.today()
    for i in range(3):
        store.upsert_wellness_checkin(
            uid,
            day=(today - timedelta(days=i)).isoformat(),
            mood_emoji="sad",
            mood_score=1,
            source="test",
            age_band="teen",
        )
    alert = evaluate_security_mood_fusion(
        store, uid, online_threat=True, locale="ru"
    )
    assert alert is not None
    assert alert["alert_type"] == "security_mood_fusion"
