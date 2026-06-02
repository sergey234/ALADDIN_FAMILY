# -*- coding: utf-8 -*-
"""p2-34 / p2-35 — trauma referral + alliance."""

from __future__ import annotations

import os
import sys

import pytest

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from security.services.ai_platform.companion_store import CompanionStore
from security.services.ai_platform.wellness_alliance import (
    bump_alliance,
    get_alliance_state,
    hero_emotion_from_score,
)
from security.services.ai_platform.wellness_escalation import evaluate_escalation
from security.services.ai_platform.wellness_trauma_referral import (
    build_trauma_referral_payload,
    detect_trauma_keywords,
    trauma_safety_prompt_block,
)


@pytest.fixture
def store(tmp_path):
    os.environ["COMPANION_DB_PATH"] = str(tmp_path / "trauma.db")
    return CompanionStore(db_path=tmp_path / "trauma.db")


def test_trauma_detect_and_payload():
    hit, _ = detect_trauma_keywords("у меня травма детства")
    assert hit is True
    payload = build_trauma_referral_payload(
        "насилие в семье", age_band="parent", locale="ru"
    )
    assert payload["triggered"] is True
    assert payload["referral"]["lines"]
    assert "специалист" in payload["specialist_note"].lower()


def test_trauma_child_redirect():
    payload = build_trauma_referral_payload(
        "trauma flashback", age_band="child", locale="en"
    )
    assert payload["redirect_pillar"] == "humanistic"


def test_escalation_trauma_l2():
    esc = evaluate_escalation("мне нужен emdr")
    assert esc.level == "L2"
    assert esc.reason == "trauma_keywords"


def test_trauma_safety_block():
    block = trauma_safety_prompt_block("птср", age_band="teen", locale="ru")
    assert "TRAUMA SAFETY" in block


def test_alliance_bump(store):
    uid = "u_all"
    bump_alliance(store, uid, +10, reason="test")
    state = get_alliance_state(store, uid)
    assert state["alliance_score"] == 60
    assert hero_emotion_from_score(80) == "celebrate"
