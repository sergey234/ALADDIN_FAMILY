# -*- coding: utf-8 -*-
"""Wellness push + reflective/referral i18n (p18-09…11)."""

from __future__ import annotations


def test_list_reflective_modes_from_i18n():
    from security.services.ai_platform.wellness_i18n_loader import list_reflective_modes_from_i18n

    ru = list_reflective_modes_from_i18n(locale="ru")
    en = list_reflective_modes_from_i18n(locale="en")
    assert len(ru) == 5
    assert ru[0]["label_key"] == "wellness_mode_presence"
    assert ru[0]["label"] != en[0]["label"]


def test_get_referral_payload_from_i18n():
    from security.services.ai_platform.wellness_i18n_loader import get_referral_payload_from_i18n

    ru = get_referral_payload_from_i18n(locale="ru")
    en = get_referral_payload_from_i18n(locale="en")
    assert ru["lines"][0]["label_key"] == "wellness_referral_112"
    assert "112" in ru["lines"][0]["phone"]
    assert len(en["lines"]) >= 2


def test_load_push_message_ru_en():
    from security.services.ai_platform.wellness_i18n_loader import load_push_message

    ru = load_push_message("checkin_evening", "ru")
    en = load_push_message("checkin_evening", "en")
    assert ru != en
    assert load_push_message("nudge_idle_2d", "ru", part="title")
    assert load_push_message("nudge_idle_2d", "en", part="body")


def test_outcome_and_weekly_meaning_i18n():
    from security.services.ai_platform.wellness_i18n_loader import (
        outcome_reminder_from_i18n,
        weekly_meaning_from_i18n,
    )

    ru = outcome_reminder_from_i18n(locale="ru")
    en = outcome_reminder_from_i18n(locale="en")
    assert ru["title"] != en["title"]
    wm = weekly_meaning_from_i18n(locale="en", observe_text="sleep")
    assert "sleep" in wm["prompt"]


def test_together_and_family_i18n():
    from security.services.ai_platform.wellness_i18n_loader import (
        family_theme_label_from_i18n,
        together_session_from_i18n,
    )

    parent = together_session_from_i18n(age_band="parent", locale="ru")
    child = together_session_from_i18n(age_band="teen", locale="en")
    assert parent["intro_key"] == "wellness_together_parent_intro"
    assert child["intro_key"] == "wellness_together_child_intro"
    assert family_theme_label_from_i18n("school", locale="ru") == "Школа"


def test_wellness_reflective_modes_module():
    from security.services.ai_platform.wellness_reflective_modes import list_reflective_modes

    modes = list_reflective_modes(locale="en")
    assert modes[0]["id"] == "presence"


def test_wellness_nudge_uses_push_json():
    from security.services.ai_platform.wellness_nudge import evaluate_idle_nudge

    class _Store:
        def list_wellness_checkins(self, *_a, **_k):
            return []

        def get_wellness_settings(self, *_a, **_k):
            return {}

    out = evaluate_idle_nudge(_Store(), "u1", locale="en")
    assert out["title"] == "We miss you"
