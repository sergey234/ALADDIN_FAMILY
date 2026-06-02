# -*- coding: utf-8 -*-
"""Backend wellness_error_* ru/en (p18-15)."""

from __future__ import annotations


def test_wellness_error_from_i18n_ru_en():
    from security.services.ai_platform.wellness_i18n_loader import wellness_error_from_i18n

    ru = wellness_error_from_i18n("wellness_consent_required", locale="ru")
    en = wellness_error_from_i18n("wellness_consent_required", locale="en")
    assert ru["message_key"] == "wellness_error_consent_required"
    assert ru["message"] != en["message"]
    assert "правил" in ru["message"].lower() or "принять" in ru["message"].lower()


def test_wellness_error_unknown_fallback():
    from security.services.ai_platform.wellness_i18n_loader import wellness_error_from_i18n

    row = wellness_error_from_i18n("totally_unknown_code", locale="en")
    assert row["message_key"] == "wellness_error_generic"


def test_wellness_errors_catalog():
    from security.services.ai_platform.wellness_api_errors import build_errors_catalog

    catalog = build_errors_catalog(locale="ru")
    codes = {row["code"] for row in catalog}
    assert "wellness_consent_required" in codes
    assert "crisis_cooldown_48h" in codes


def test_raise_wellness_error_payload():
    from security.services.ai_platform.wellness_api_errors import wellness_error_payload

    payload = wellness_error_payload("jung_disabled", locale="en")
    assert payload["code"] == "jung_disabled"
    assert payload["message_key"] == "wellness_error_jung_disabled"
    assert payload["http_status"] == 403
