from __future__ import annotations

import pytest

from bot.config import load_settings
from bot.services.fiat_checkout import fiat_bc_universal_url_active


def test_lava_suppresses_default_ckassa_bc(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:lava")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "lava_test_pepper_minimum_32_chars____")
    monkeypatch.setenv("LAVA_SHOP_ID", "a81738ce-8116-4b99-bdd7-5338fab2162d")
    monkeypatch.setenv("LAVA_SECRET_KEY", "secret")
    monkeypatch.setenv("LAVA_HOOK_URL", "https://example.com/v1/payments/lava-webhook")
    s = load_settings()
    assert (s.ckassa_bc_universal_payment_url or "").strip() == ""
    assert fiat_bc_universal_url_active(s) == ""


def test_ckassa_bc_active_when_explicit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:bc")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "bc_test_pepper_minimum_32_chars_____")
    monkeypatch.setenv("LAVA_SHOP_ID", "a81738ce-8116-4b99-bdd7-5338fab2162d")
    monkeypatch.setenv("LAVA_SECRET_KEY", "secret")
    monkeypatch.setenv("LAVA_HOOK_URL", "https://example.com/v1/payments/lava-webhook")
    monkeypatch.setenv("CKASSA_BC_UNIVERSAL_PAYMENT_URL", "https://bc.ckassa.ru/demo")
    s = load_settings()
    assert fiat_bc_universal_url_active(s) == ""
