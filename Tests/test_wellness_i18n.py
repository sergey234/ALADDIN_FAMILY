# -*- coding: utf-8 -*-
"""Wellness i18n tests (p18-04…06)."""

from __future__ import annotations


def test_resolve_wellness_locale_accept_language_priority():
    from security.services.ai_platform.wellness_i18n_loader import resolve_wellness_locale

    assert resolve_wellness_locale(query_locale="ru", accept_language="en-US,en;q=0.9") == "en"
    assert resolve_wellness_locale(query_locale="en", accept_language="ru-RU") == "ru"
    assert resolve_wellness_locale(query_locale="en") == "en"
    assert resolve_wellness_locale() == "ru"


def test_phq_lite_schema_from_i18n_ru_en():
    from security.services.ai_platform.wellness_i18n_loader import phq_lite_schema_from_i18n

    ru = phq_lite_schema_from_i18n(locale="ru")
    en = phq_lite_schema_from_i18n(locale="en")
    assert ru is not None and en is not None
    assert len(ru["questions"]) == 5
    assert ru["questions"][0]["text"] != en["questions"][0]["text"]
    assert "скрининг" in ru["disclaimer"].lower() or "диагноз" in ru["disclaimer"].lower()
    assert "screening" in en["disclaimer"].lower()


def test_wellness_assessments_phq_lite_uses_json():
    from security.services.ai_platform.wellness_assessments import phq_lite_schema

    schema = phq_lite_schema(locale="en")
    assert schema["assessment_type"] == "phq_lite"
    assert schema["questions"][0]["id"] == "q1"
    assert len(schema["answer_options"]) == 4


def test_wellness_crisis_message_and_actions():
    from security.services.ai_platform.wellness_i18n_loader import (
        wellness_crisis_message,
        wellness_suggested_actions_for_level,
    )

    ru = wellness_crisis_message("ru")
    en = wellness_crisis_message("en")
    assert "112" in ru
    assert "112" in en
    l3 = wellness_suggested_actions_for_level("L3", "ru")
    assert any(a["id"] == "wellness_referral_112" for a in l3)
    l2 = wellness_suggested_actions_for_level("L2", "en")
    assert any(a["id"] == "wellness_open_referral" for a in l2)


def test_l3_referral_filters_emergency_lines_only():
    from security.services.ai_platform.wellness_i18n_loader import get_referral_payload_from_i18n

    l3 = get_referral_payload_from_i18n(locale="ru", level="L3")
    ids = {line["id"] for line in l3["lines"]}
    assert ids == {"112", "child_helpline"}
    for line in l3["lines"]:
        assert line["phone"]

    l2 = get_referral_payload_from_i18n(locale="ru", level="L2")
    assert len(l2["lines"]) >= len(l3["lines"])


def test_companion_crisis_response_uses_i18n():
    from security.services.ai_platform.companion_ethics import companion_crisis_response

    ru = companion_crisis_response("ru")
    en = companion_crisis_response("en")
    assert "112" in ru
    assert "112" in en
    assert ru != en


def test_wellness_escalation_suggested_actions():
    from security.services.ai_platform.wellness_i18n_loader import (
        wellness_suggested_actions_for_escalation,
    )

    actions = wellness_suggested_actions_for_escalation(
        "L3", "ru", escalation_actions=["call_112"]
    )
    assert len(actions) >= 2
    ids = {a["id"] for a in actions}
    assert "wellness_referral_112" in ids
