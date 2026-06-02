# -*- coding: utf-8 -*-
"""Exercise i18n JSON tests (p18-08)."""

from __future__ import annotations


def test_thought_record_i18n_meta():
    from security.services.ai_platform.wellness_i18n_loader import exercise_meta_from_i18n

    meta = exercise_meta_from_i18n("thought_record")
    assert meta is not None
    assert meta["total_steps"] == 5
    assert meta["steps"][0]["hint"]["ru"]
    assert meta["steps"][0]["hint"]["en"]


def test_dream_note_lite_i18n_meta():
    from security.services.ai_platform.wellness_i18n_loader import exercise_meta_from_i18n

    meta = exercise_meta_from_i18n("dream_note_lite")
    assert meta is not None
    assert meta["pillar"] == "jung"
    assert len(meta["steps"]) == 3


def test_exercise_engine_prefers_i18n_json():
    from security.services.ai_platform.wellness_exercise_engine import get_exercise_meta

    meta = get_exercise_meta("cognitive", "thought_record")
    assert meta["total_steps"] == 5
    hint = meta["steps"][0]["hint"]
    assert "ru" in hint and "en" in hint


def test_exercise_title_i18n():
    from security.services.ai_platform.wellness_i18n_loader import exercise_title_i18n

    assert "thought" in exercise_title_i18n("thought_record", "en").lower()
    assert "мысл" in exercise_title_i18n("thought_record", "ru").lower()
