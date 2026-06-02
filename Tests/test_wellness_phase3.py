# -*- coding: utf-8 -*-
"""Phase 3 wellness modules smoke tests."""

from __future__ import annotations


def test_premium_features_gate_free_user():
    from security.services.ai_platform.wellness_premium_access import wellness_premium_features_gate

    class StubStore:
        def last_wellness_crisis_l3_at(self, _uid):
            return None

    gate = wellness_premium_features_gate(
        StubStore(),
        "u1",
        {"subscription_level": "free"},
        profile={"wellness_accepted": True},
        age_band="teen",
    )
    assert gate["allowed"] is False
    assert gate["reason"] == "wellness_premium_subscription_required"


def test_values_card_schema():
    from security.services.ai_platform.wellness_values_card import build_values_card_schema

    schema = build_values_card_schema(locale="en")
    assert schema["title_key"] == "wellness_values_card_title"
    assert len(schema["values"]) >= 4


def test_seasonal_playbooks():
    from security.services.ai_platform.wellness_seasonal import list_seasonal_playbooks

    books = list_seasonal_playbooks(locale="ru")
    assert any(b["id"] == "exams" for b in books)


def test_sleep_stories():
    from security.services.ai_platform.wellness_sleep_stories import list_sleep_stories

    stories = list_sleep_stories(locale="en")
    assert len(stories) >= 5


def test_pillar_rive_payload():
    from security.services.ai_platform.wellness_pillar_rive import pillar_rive_payload

    payload = pillar_rive_payload("cognitive")
    assert payload["rive_state"] == "think"


def test_family_talk_prompts():
    from security.services.ai_platform.wellness_family_prompt import build_family_talk_prompts

    payload = build_family_talk_prompts(locale="ru", topic="mood")
    assert len(payload["prompts"]) >= 2


def test_parent_playbook_llm_flag():
    from security.services.ai_platform.wellness_parent_playbook import build_parent_playbook

    payload = build_parent_playbook(locale="ru", topic="school", use_llm=False)
    assert payload["phrases"]
