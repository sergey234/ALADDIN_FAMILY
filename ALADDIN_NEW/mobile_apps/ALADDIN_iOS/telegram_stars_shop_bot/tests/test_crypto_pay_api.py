from __future__ import annotations

import pytest

from bot.config import Settings
from bot.services import crypto_pay_api as cap


def _s(**kwargs: object) -> Settings:
    base: dict[str, object] = dict(
        BOT_TOKEN="9:x",
        ADMIN_IDS="1",
        API_KEY_PEPPER="k" * 32,
    )
    base.update(kwargs)
    return Settings(**base)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_resolve_rub_per_usdt_fallback_no_cryptopay_token() -> None:
    s = _s(USDT_RUB_RATE=0.0, USD_RUB_RATE=90.0)
    assert await cap.resolve_rub_per_usdt(s) == 90.0


def test_rub_per_asset_direct() -> None:
    rates = [{"source": "USDT", "target": "RUB", "rate": "99.5"}]
    assert cap.rub_per_asset_unit_from_rates(rates, "USDT") == 99.5


def test_rub_per_asset_inverse() -> None:
    rates = [{"source": "RUB", "target": "TON", "rate": "0.02"}]
    assert cap.rub_per_asset_unit_from_rates(rates, "TON") == 50.0


def test_crypto_pay_invoice_api_ready() -> None:
    assert cap.crypto_pay_invoice_api_ready(_s()) is False
    assert cap.crypto_pay_invoice_api_ready(_s(CRYPTO_PAY_ENABLED=True)) is False
    assert cap.crypto_pay_invoice_api_ready(_s(CRYPTO_PAY_ENABLED=True, CRYPTO_PAY_API_TOKEN="abc")) is True


@pytest.mark.asyncio
async def test_create_invoice_uses_mocked_http(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, dict[str, object]]] = []

    async def fake_get(
        settings: Settings,
        method: str,
        params: dict[str, object],
    ) -> dict[str, object] | None:
        calls.append((method, params))
        if method == "getExchangeRates":
            return {"ok": True, "result": [{"source": "USDT", "target": "RUB", "rate": "100"}]}
        if method == "createInvoice":
            return {"ok": True, "result": {"pay_url": "https://t.me/CryptoBot?start=iv_test"}}
        return None

    monkeypatch.setattr(cap, "_crypto_pay_get", fake_get)
    s = _s(
        CRYPTO_PAY_ENABLED=True,
        CRYPTO_PAY_API_TOKEN="test_token",
        CRYPTO_PAY_DEFAULT_ASSET="USDT",
    )
    url = await cap.create_crypto_pay_invoice_checkout_url(s, order_id=12, due_rub=25.0)
    assert url == "https://t.me/CryptoBot?start=iv_test"
    assert [c[0] for c in calls] == ["getExchangeRates", "createInvoice"]
    inv_params = calls[1][1]
    assert inv_params["asset"] == "USDT"
    assert inv_params["amount"] == "0.25"
    assert inv_params["payload"] == "SB1|12|2500"


@pytest.mark.asyncio
async def test_create_invoice_usdt_fallback_rates(monkeypatch: pytest.MonkeyPatch) -> None:
    inv_params: dict[str, object] = {}

    async def fake_get(
        settings: Settings,
        method: str,
        params: dict[str, object],
    ) -> dict[str, object] | None:
        if method == "getExchangeRates":
            return {"ok": True, "result": []}
        if method == "createInvoice":
            inv_params.update(params)
            return {"ok": True, "result": {"bot_invoice_url": "https://t.me/x"}}
        return None

    monkeypatch.setattr(cap, "_crypto_pay_get", fake_get)
    s = _s(
        CRYPTO_PAY_ENABLED=True,
        CRYPTO_PAY_API_TOKEN="tok",
        USD_RUB_RATE=80.0,
        USDT_RUB_RATE=0.0,
    )
    url = await cap.create_crypto_pay_invoice_checkout_url(s, order_id=3, due_rub=40.0)
    assert url == "https://t.me/x"
    assert inv_params["amount"] == "0.5"
    assert inv_params["payload"] == "SB1|3|4000"
