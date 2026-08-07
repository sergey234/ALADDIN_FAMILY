from __future__ import annotations

import pytest

from bot.config import Settings
from bot.services.ckassa_api import (
    CKASSA_DEMO_SECRET,
    CKASSA_DEMO_SHOP,
    ckassa_callback_signature,
    ckassa_checkout_configured,
    ckassa_request_signature,
    rub_to_kopecks,
)


def test_rub_to_kopecks() -> None:
    assert rub_to_kopecks(100.0) == 10000
    assert rub_to_kopecks(99.99) == 9999


def test_request_signature_matches_wordpress_plugin_vector() -> None:
    # Строка: shop|orderId|amount|secret (алгоритм WC_Gateway_Ckassa).
    sig = ckassa_request_signature(CKASSA_DEMO_SECRET, CKASSA_DEMO_SHOP, order_id=1, amount_kopecks=10000)
    assert sig == "QjgzRUQwMDdEQjI3OUVDMUY1OTdGRUYyQUI4MzgyNTQ1MEYxRENDOEVEMDk0ODUyMEFERjg2QTc1NDMxQjhGNg=="


def test_callback_signature_vector() -> None:
    sig = ckassa_callback_signature(
        CKASSA_DEMO_SECRET,
        CKASSA_DEMO_SHOP,
        order_id=1,
        reg_pay_num="REG1",
        amount_kopecks=10000,
        result="success",
    )
    assert sig == "MTRDNTk4QkNCREQwNjkzQjJCQzkzMUU3OTI1MkY3ODVENjNCOUVGM0ZBNjQ2QTQ4MUY2QTUyRkNFQjFCNTlGMg=="


def test_checkout_configured_requires_callback_in_prod(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:ck")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "p" * 32)
    monkeypatch.setenv("CKASSA_ENABLED", "true")
    monkeypatch.setenv("CKASSA_TEST_MODE", "false")
    monkeypatch.setenv("CKASSA_SHOP_TOKEN", "shop-uuid")
    monkeypatch.setenv("CKASSA_SECRET_KEY", "sec")
    monkeypatch.setenv("CKASSA_CALLBACK_PUBLIC_URL", "")
    s = Settings()
    assert ckassa_checkout_configured(s) is False
    monkeypatch.setenv("CKASSA_CALLBACK_PUBLIC_URL", "https://example.com/v1/payments/ckassa-webhook")
    s2 = Settings()
    assert ckassa_checkout_configured(s2) is True


def test_test_mode_configured_without_env_tokens(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:ck2")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "p" * 32)
    monkeypatch.setenv("CKASSA_ENABLED", "true")
    monkeypatch.setenv("CKASSA_TEST_MODE", "true")
    s = Settings()
    assert ckassa_checkout_configured(s) is True
