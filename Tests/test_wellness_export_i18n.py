# -*- coding: utf-8 -*-
"""Widget, PDF labels, parent playbook i18n (p18-13)."""

from __future__ import annotations


def test_clinician_export_copy_from_i18n():
    from security.services.ai_platform.wellness_i18n_loader import clinician_export_copy_from_i18n

    ru = clinician_export_copy_from_i18n(locale="ru")
    en = clinician_export_copy_from_i18n(locale="en")
    assert ru["title"] != en["title"]
    assert "диагноз" in ru["disclaimer"].lower() or "самопомощ" in ru["disclaimer"].lower()


def test_weekly_pdf_labels_from_i18n():
    from security.services.ai_platform.wellness_i18n_loader import weekly_pdf_labels_from_i18n

    labels = weekly_pdf_labels_from_i18n(locale="en")
    assert labels["title_key"] == "wellness_pdf_title"
    assert labels["section_checkins_key"] == "wellness_pdf_section_checkins"
    assert labels["share_cta"]


def test_parent_playbook_from_i18n():
    from security.services.ai_platform.wellness_i18n_loader import parent_playbook_from_i18n

    ru = parent_playbook_from_i18n(locale="ru")
    en = parent_playbook_from_i18n(locale="en")
    assert ru["title_key"] == "wellness_parent_playbook_title"
    assert len(ru["phrases"]) >= 4
    assert ru["phrases"][0]["text"] != en["phrases"][0]["text"]


def test_widget_copy_from_i18n():
    from security.services.ai_platform.wellness_i18n_loader import widget_copy_from_i18n

    ru = widget_copy_from_i18n(locale="ru")
    en = widget_copy_from_i18n(locale="en")
    assert ru["title_key"] == "wellness_widget_title"
    assert ru["title"] != en["title"]


def test_build_parent_playbook_module():
    from security.services.ai_platform.wellness_parent_playbook import build_parent_playbook

    payload = build_parent_playbook(locale="ru")
    assert payload["phrases"]
