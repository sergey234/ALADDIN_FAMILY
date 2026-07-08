# -*- coding: utf-8 -*-
"""p2-24/25 — alerts + family dashboard."""

from __future__ import annotations

import os
import sys

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from security.services.ai_platform.companion_store import CompanionStore
from security.services.ai_platform.wellness_alerts import (
    build_user_alerts,
    build_family_dashboard,
)


@pytest.fixture
def store(tmp_path):
    os.environ["COMPANION_DB_PATH"] = str(tmp_path / "alerts.db")
    return CompanionStore(db_path=tmp_path / "alerts.db")


def test_family_dashboard_opt_out(store):
    uid = "teen1"
    store.upsert_wellness_settings(uid, parent_share_aggregate=0)
    dash = build_family_dashboard(store, uid)
    assert dash["shared"] is False


def test_family_dashboard_shared_aggregate(store):
    uid = "teen2"
    store.upsert_wellness_settings(uid, parent_share_aggregate=1)
    from datetime import date

    store.upsert_wellness_checkin(
        uid, day=date.today().isoformat(), mood_score=3, stress_level=2
    )
    dash = build_family_dashboard(store, uid)
    assert dash["shared"] is True
    assert dash["aggregate"]["days_with_checkin"] >= 1


def test_build_user_alerts_has_checkin(store):
    alerts = build_user_alerts(store, "u1", age_band="teen")
    types = {a.alert_type for a in alerts}
    assert "daily_checkin" in types or "checkin_reminder" in types


def test_family_dashboard_includes_phq_lite_band(store):
    uid = "teen_phq"
    store.upsert_wellness_settings(uid, parent_share_aggregate=1)
    store.save_wellness_assessment(
        uid,
        assessment_type="phq_lite",
        answers=[1, 2, 1, 2, 1],
        score=7,
        severity="mild",
        suggest_professional=False,
    )
    dash = build_family_dashboard(store, uid)
    assert dash["shared"] is True
    phq = dash["aggregate"]["phq_lite"]
    assert phq is not None
    assert phq["severity"] == "mild"
    assert phq["suggest_professional"] is False
