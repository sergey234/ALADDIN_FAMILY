# -*- coding: utf-8 -*-
"""Child/teen age-variant i18n (p18-14)."""

from __future__ import annotations


def test_load_age_variants_manifest():
    from security.services.ai_platform.wellness_i18n_loader import load_age_variants_manifest

    manifest = load_age_variants_manifest()
    keys = manifest.get("keys_with_variants") or []
    assert "wellness_hub_title" in keys
    assert len(keys) >= 20


def test_age_copy_from_i18n_child_teen():
    from security.services.ai_platform.wellness_i18n_loader import age_copy_from_i18n

    child_ru = age_copy_from_i18n("wellness_assessment_crisis_hint", age_band="child", locale="ru")
    teen_en = age_copy_from_i18n("wellness_assessment_crisis_hint", age_band="teen", locale="en")
    parent_ru = age_copy_from_i18n("wellness_assessment_crisis_hint", age_band="parent", locale="ru")
    assert "взросл" in child_ru.lower()
    assert "adult" in teen_en.lower()
    assert parent_ru
    assert child_ru != parent_ru or teen_en != parent_ru


def test_age_copy_fallback_base():
    from security.services.ai_platform.wellness_i18n_loader import age_copy_from_i18n

    text = age_copy_from_i18n("wellness_hub_subtitle", age_band="unknown", locale="en")
    assert text
