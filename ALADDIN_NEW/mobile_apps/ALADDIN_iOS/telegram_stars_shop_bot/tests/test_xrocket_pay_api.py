from __future__ import annotations

import pytest

from bot.config import Settings
from bot.services import xrocket_pay_api as xr


def _s(**kwargs: object) -> Settings:
    base: dict[str, object] = dict(
        BOT_TOKEN="9:x",
        ADMIN_IDS="1",
        API_KEY_PEPPER="k" * 32,
    )
    base.update(kwargs)
    return Settings(**base)  # type: ignore[arg-type]


def test_xrocket_invoice_api_ready() -> None:
    assert xr.xrocket_invoice_api_ready(_s()) is False
    assert xr.xrocket_invoice_api_ready(_s(XROCKET_PAY_ENABLED=True)) is False
    assert xr.xrocket_invoice_api_ready(_s(XROCKET_PAY_ENABLED=True, XROCKET_PAY_API_KEY="k")) is True


@pytest.mark.asyncio
async def test_create_xrocket_invoice(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    async def fake_post(settings: Settings, path: str, body: dict[str, object]) -> dict[str, object] | None:
        captured["path"] = path
        captured["body"] = body
        return {"success": True, "data": {"link": "https://t.me/xRocket?start=inv_test"}}

    monkeypatch.setattr(xr, "_xrocket_post_json", fake_post)

    async def fake_resolve(settings: Settings) -> float:
        return 100.0

    monkeypatch.setattr(xr, "resolve_rub_per_usdt", fake_resolve)

    s = _s(XROCKET_PAY_ENABLED=True, XROCKET_PAY_API_KEY="secret")
    url = await xr.create_xrocket_invoice_checkout_url(s, order_id=9, due_rub=50.0)
    assert url == "https://t.me/xRocket?start=inv_test"
    assert captured["path"] == "/tg-invoices"
    b = captured["body"]
    assert isinstance(b, dict)
    assert b["currency"] == "USDT"
    assert b["numPayments"] == 1
    assert b["payload"] == "SB1|9|5000"
    assert abs(float(b["amount"]) - 0.5) < 1e-9
