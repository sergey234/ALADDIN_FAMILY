from __future__ import annotations

import pytest

from bot.config import Settings
from bot.keyboards.shop_kb import admin_order_kb
from bot.services.admin_crypto_paid_gate import (
    crypto_invoice_providers_enabled,
    crypto_manual_paid_gate_applies,
    is_crypto_channel_payment_method,
)
from bot.services.admin_order_ff import AdminOrderFfContext, ff_context_from_order_row


def test_is_crypto_channel() -> None:
    assert is_crypto_channel_payment_method("crypto") is True
    assert is_crypto_channel_payment_method("mixcr") is True
    assert is_crypto_channel_payment_method("mix_crypto") is True
    assert is_crypto_channel_payment_method("fiat") is False
    assert is_crypto_channel_payment_method("mixfi") is False


def test_gate_applies_only_when_providers_on(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:g")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "p" * 32)
    monkeypatch.setenv("CRYPTO_PAY_ENABLED", "false")
    monkeypatch.setenv("XROCKET_PAY_ENABLED", "false")
    s = Settings()
    order = {"status": "pending_payment", "payment_method": "crypto"}
    assert crypto_manual_paid_gate_applies(order, s) is False

    monkeypatch.setenv("CRYPTO_PAY_ENABLED", "true")
    s2 = Settings()
    assert crypto_manual_paid_gate_applies(order, s2) is True


def test_gate_not_for_fiat_pending(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:g2")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "p" * 32)
    monkeypatch.setenv("CRYPTO_PAY_ENABLED", "true")
    s = Settings()
    order = {"status": "pending_payment", "payment_method": "fiat"}
    assert crypto_manual_paid_gate_applies(order, s) is False


def test_gate_fiat_when_ckassa_configured(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:g3")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "p" * 32)
    monkeypatch.setenv("CRYPTO_PAY_ENABLED", "false")
    monkeypatch.setenv("XROCKET_PAY_ENABLED", "false")
    monkeypatch.setenv("CKASSA_ENABLED", "true")
    monkeypatch.setenv("CKASSA_SHOP_TOKEN", "shop-uuid")
    monkeypatch.setenv("CKASSA_SECRET_KEY", "sec")
    monkeypatch.setenv("CKASSA_CALLBACK_PUBLIC_URL", "https://ex.example/v1/payments/ckassa-webhook")
    s = Settings()
    order = {"status": "pending_payment", "payment_method": "fiat"}
    assert crypto_manual_paid_gate_applies(order, s) is True
    mix = {"status": "pending_payment", "payment_method": "mix_fiat"}
    assert crypto_manual_paid_gate_applies(mix, s) is True


def test_ff_context_includes_payment_method() -> None:
    row = {"status": "pending_payment", "payment_method": "crypto", "fulfillment_attempt_count": 0}
    ctx = ff_context_from_order_row(row)
    assert ctx is not None
    assert ctx.payment_method == "crypto"


def _cds(markup) -> list[str]:
    dumped = markup.model_dump(mode="python", exclude_none=True)
    out: list[str] = []
    for row in dumped.get("inline_keyboard") or []:
        for btn in row:
            cd = btn.get("callback_data")
            if cd:
                out.append(str(cd))
    return out


def test_kb_pending_crypto_uses_paidbg(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:kb")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "p" * 32)
    monkeypatch.setenv("CRYPTO_PAY_ENABLED", "true")
    s = Settings()
    assert crypto_invoice_providers_enabled(s) is True
    ctx = AdminOrderFfContext(
        status="pending_payment",
        fulfillment_mode_raw="auto",
        attempt_count=0,
        has_provider_ref=False,
        payment_method="crypto",
    )
    cds = _cds(admin_order_kb(42, settings=s, actor_id=1, order_ff=ctx))
    assert any("adm:paidbg:42" in c for c in cds)
    assert not any(c == "adm:paid:42" for c in cds)


def test_kb_pending_crypto_providers_off_still_adm_paid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:kb2")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "p" * 32)
    monkeypatch.setenv("CRYPTO_PAY_ENABLED", "false")
    monkeypatch.setenv("XROCKET_PAY_ENABLED", "false")
    s = Settings()
    ctx = AdminOrderFfContext(
        status="pending_payment",
        fulfillment_mode_raw="auto",
        attempt_count=0,
        has_provider_ref=False,
        payment_method="crypto",
    )
    cds = _cds(admin_order_kb(5, settings=s, actor_id=1, order_ff=ctx))
    assert any("adm:paid:5" in c for c in cds)
    assert not any("paidbg" in c for c in cds)
