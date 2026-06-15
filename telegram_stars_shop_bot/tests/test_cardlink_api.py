from __future__ import annotations

import pytest

from bot.config import Settings
from bot.services.cardlink_api import (
    cardlink_checkout_configured,
    cardlink_payment_signature,
    parse_cardlink_order_id,
    verify_cardlink_payment_signature,
)


def test_cardlink_payment_signature_known() -> None:
    sig = cardlink_payment_signature("secret", "100.00", "42")
    assert sig == sig.upper()
    assert len(sig) == 32
    assert verify_cardlink_payment_signature("secret", out_sum="100.00", inv_id="42", signature_value=sig)


def test_parse_cardlink_order_id() -> None:
    assert parse_cardlink_order_id("123") == 123
    assert parse_cardlink_order_id("ORDER456") == 456
    assert parse_cardlink_order_id("") is None
    assert parse_cardlink_order_id("abc") is None


def test_cardlink_checkout_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "x")
    monkeypatch.setenv("USD_RUB_RATE", "80")
    monkeypatch.setenv("CARDLINK_ENABLED", "false")
    s = Settings()
    assert cardlink_checkout_configured(s) is False
    monkeypatch.setenv("CARDLINK_ENABLED", "true")
    monkeypatch.setenv("CARDLINK_SHOP_ID", "shop1")
    monkeypatch.setenv("CARDLINK_API_TOKEN", "tok1")
    s2 = Settings()
    assert cardlink_checkout_configured(s2) is True
