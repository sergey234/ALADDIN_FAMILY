# -*- coding: utf-8 -*-
"""Unit tests — wellness Phase 1 backend (no server)."""

from security.services.ai_platform.wellness_assessments import score_phq_lite, phq_lite_schema
from security.services.ai_platform.wellness_pillar_guard import assert_single_pillar
from security.services.ai_platform.wellness_prompt_builder import load_pillar_pack
from security.services.ai_platform.wellness_age_policy import can_use_phq_lite, has_wellness_consent


def test_phq_lite_score_minimal():
    r = score_phq_lite([0, 0, 0, 0, 0])
    assert r.score == 0
    assert r.severity == "minimal"
    assert not r.suggest_professional


def test_phq_lite_score_moderate():
    r = score_phq_lite([2, 2, 2, 2, 2])
    assert r.score == 10
    assert r.suggest_professional


def test_phq_lite_schema_has_five_questions():
    s = phq_lite_schema(locale="ru")
    assert len(s["questions"]) == 5
    assert "диагноз" in s["disclaimer"].lower() or "скрининг" in s["disclaimer"].lower()


def test_pillar_guard_blocks_mix():
    g = assert_single_pillar(
        session_pillar="cognitive",
        requested_pillar="jung",
        age_band="teen",
    )
    assert not g.ok
    assert g.reason == "pillar_mismatch"


def test_cognitive_pack_forbidden_phrases():
    pack = load_pillar_pack("cognitive", "ru", "v1")
    assert pack
    phrases = pack.get("forbidden_phrases") or {}
    ru = phrases.get("ru") or phrases
    assert any("диагноз" in str(p).lower() for p in ru)


def test_child_consent_requires_parent_toggle():
    assert not has_wellness_consent({"wellness_accepted": True}, age_band="child")
    assert has_wellness_consent(
        {"wellness_accepted": True, "psychological_support_enabled": True},
        age_band="child",
    )


def test_child_cannot_phq():
    assert not can_use_phq_lite("child")


def test_orchestrator_blocks_drift():
    from security.services.ai_platform.wellness_orchestrator import apply_response_guard

    bad = "Давай сделаем маленький шаг и привычку сегодня."
    r = apply_response_guard(bad, primary_pillar="cognitive", locale="ru")
    assert not r.ok
    assert r.reason


def test_teen_parent_share_default():
    from security.services.ai_platform.wellness_orchestrator import teen_default_parent_share

    assert teen_default_parent_share("teen", None) == 0
    assert teen_default_parent_share("teen", 1) == 1


def test_wellness_loop_suggests_pillar_without_session(tmp_path):
    from security.services.ai_platform.companion_store import CompanionStore
    from security.services.ai_platform.wellness_orchestrator import (
        WellnessLoopPhase,
        run_wellness_loop,
    )

    store = CompanionStore(db_path=tmp_path / "loop.db")
    uid = "u-loop-1"
    loop = run_wellness_loop(
        store,
        uid,
        message="устал и грустно",
        age_band="teen",
        locale="ru",
        requested_pillar=None,
        jung_enabled=False,
    )
    assert loop.guard.ok
    assert loop.phase in (WellnessLoopPhase.SESSION, WellnessLoopPhase.SCREENING)
    assert loop.primary_pillar in ("humanistic", "cognitive", "behavioral")


def test_resolve_agents_crisis():
    from security.services.ai_platform.wellness_escalation import EscalationResult
    from security.services.ai_platform.wellness_orchestrator import resolve_agents_for_turn

    esc = EscalationResult(level="L3", reason="crisis", actions=["call_112"])
    agents = resolve_agents_for_turn(pillar="cognitive", escalation=esc, suggest_phq_lite=False)
    assert "crisis_agent" in agents
    assert "cbt_coach_agent" not in agents


def test_prepare_wellness_full_loop_prefix(tmp_path):
    from security.services.ai_platform.companion_store import CompanionStore
    from security.services.ai_platform.wellness_orchestrator import prepare_wellness_chat_turn

    store = CompanionStore(db_path=tmp_path / "prep.db")
    uid = "u-prep-1"
    store.upsert_wellness_settings(uid, primary_pillar="cognitive")
    prep = prepare_wellness_chat_turn(
        store,
        uid,
        message="тревожные мысли крутятся",
        age_band="teen",
        locale="ru",
        requested_pillar="cognitive",
        character_id="unicorn",
        jung_enabled=True,
        reflective_enabled=False,
        use_full_loop=True,
    )
    assert prep.ok
    assert prep.active_pillar == "cognitive"
    assert "[WELLNESS" in prep.wellness_prefix
    assert "pack_version=cognitive_v1.1" in prep.wellness_prefix
    assert "[WELLNESS AGENTS ACTIVE]" in prep.wellness_prefix
    assert "cbt_coach_agent" in prep.agents_active
    assert prep.loop_phase == "session"


def test_session_pack_lock(tmp_path):
    from security.services.ai_platform.companion_store import CompanionStore
    from security.services.ai_platform.wellness_pack_registry import lock_session_pack

    store = CompanionStore(db_path=tmp_path / "pack.db")
    uid = "u-pack"
    folder, ver = lock_session_pack(store, uid, "humanistic")
    assert folder == "v1"
    assert ver == "humanistic_v1.1"
    folder2, ver2 = lock_session_pack(store, uid, "humanistic")
    assert folder2 == folder
    assert ver2 == ver


def test_wellness_gdpr_delete(tmp_path):
    from security.services.ai_platform.companion_store import CompanionStore
    from security.services.ai_platform.wellness_gdpr import delete_wellness_personal_data

    store = CompanionStore(db_path=tmp_path / "gdpr.db")
    uid = "u-gdpr"
    store.upsert_wellness_checkin(
        uid, day="2026-06-01", mood_emoji="ok", mood_score=3, source="test", age_band="teen"
    )
    counts = delete_wellness_personal_data(store, uid)
    assert counts.get("wellness_checkins", 0) >= 1
    assert store.list_wellness_checkins(uid, days=7) == []


def test_crisis_48h_blocks_premium(tmp_path):
    from security.services.ai_platform.companion_store import CompanionStore
    from security.services.ai_platform.wellness_crisis_monitor import (
        crisis_cooldown_active,
        record_crisis_l3,
        wellness_premium_eligible,
    )

    store = CompanionStore(db_path=tmp_path / "crisis.db")
    uid = "u-crisis-1"
    assert not crisis_cooldown_active(store, uid)
    record_crisis_l3(store, uid, source="test")
    assert crisis_cooldown_active(store, uid)
    gate = wellness_premium_eligible(
        store,
        uid,
        profile={"wellness_accepted": True},
        age_band="teen",
    )
    assert not gate["eligible"]
    assert gate["reason"] == "crisis_cooldown_48h"
    assert gate["hours_remaining"] > 0
