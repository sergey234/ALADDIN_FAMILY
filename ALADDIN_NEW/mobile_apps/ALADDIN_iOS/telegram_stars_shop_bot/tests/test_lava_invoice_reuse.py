from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.config import Settings
from bot.services.lava_api import (
    create_invoice_payment_meta,
    lava_invoice_pay_url_from_id,
    lava_provider_order_id,
    normalize_lava_pay_url,
    parse_lava_shop_order_id,
)


def test_parse_lava_shop_order_id() -> None:
    assert parse_lava_shop_order_id("59") == 59
    assert parse_lava_shop_order_id("59-r2") == 59
    assert parse_lava_shop_order_id("59-r10") == 59
    assert parse_lava_shop_order_id("bad") is None


def test_lava_provider_order_id() -> None:
    assert lava_provider_order_id(59, 1) == "59"
    assert lava_provider_order_id(59, 2) == "59-r2"


def test_normalize_lava_pay_url_adds_lang() -> None:
    assert normalize_lava_pay_url("https://pay.lava.ru/invoice/x") == (
        "https://pay.lava.ru/invoice/x?lang=ru"
    )
    assert normalize_lava_pay_url("https://pay.lava.ru/invoice/x?lang=en") == (
        "https://pay.lava.ru/invoice/x?lang=ru"
    )


def test_lava_invoice_pay_url_from_id_has_lang() -> None:
    assert lava_invoice_pay_url_from_id("abc") == "https://pay.lava.ru/invoice/abc?lang=ru"


@pytest.mark.asyncio
async def test_create_invoice_reuses_on_duplicate_order_id(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:lava")
    monkeypatch.setenv("USD_RUB_RATE", "100")
    monkeypatch.setenv("LAVA_SHOP_ID", "shop-uuid")
    monkeypatch.setenv("LAVA_SECRET_KEY", "s" * 16)
    monkeypatch.setenv("LAVA_HOOK_URL", "https://ex.example/hook")
    settings = Settings()

    status_data = {
        "status": "created",
        "url": "https://pay.lava.ru/existing",
        "id": "inv-existing",
    }

    class FakeResp:
        status_code = 422
        text = '{"error":{"orderId":["OrderId должен быть уникальным"]}}'

        def json(self):
            return {}

    async def fake_post(*_a, **_k):
        return FakeResp()

    with patch(
        "bot.services.lava_api.fetch_invoice_status",
        new=AsyncMock(return_value=status_data),
    ), patch("bot.services.lava_api.httpx.AsyncClient") as client_cls:
        client_cls.return_value.__aenter__.return_value.post = fake_post
        res = await create_invoice_payment_meta(
            settings,
            order_id=48,
            sum_rub=100.0,
            include_service=["card"],
            existing_invoice_id="inv-existing",
        )

    assert res.pay_url == "https://pay.lava.ru/existing?lang=ru"
    assert res.external_id == "inv-existing"


@pytest.mark.asyncio
async def test_create_invoice_reuses_when_status_has_no_url(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:lava")
    monkeypatch.setenv("USD_RUB_RATE", "100")
    monkeypatch.setenv("LAVA_SHOP_ID", "shop-uuid")
    monkeypatch.setenv("LAVA_SECRET_KEY", "s" * 16)
    monkeypatch.setenv("LAVA_HOOK_URL", "https://ex.example/hook")
    settings = Settings()

    status_data = {
        "status": "created",
        "id": "31295617-3b7c-432c-a1a8-3ef38dc6afb7",
        "order_id": "48",
        "include_service": ["sbp"],
    }

    class FakeResp:
        status_code = 422
        text = '{"error":{"orderId":["OrderId должен быть уникальным"]}}'

        def json(self):
            return {}

    async def fake_post(*_a, **_k):
        return FakeResp()

    with patch(
        "bot.services.lava_api.fetch_invoice_status",
        new=AsyncMock(return_value=status_data),
    ), patch("bot.services.lava_api.httpx.AsyncClient") as client_cls:
        client_cls.return_value.__aenter__.return_value.post = fake_post
        res = await create_invoice_payment_meta(
            settings,
            order_id=48,
            sum_rub=100.0,
            include_service=["card"],
            existing_invoice_id="31295617-3b7c-432c-a1a8-3ef38dc6afb7",
        )

    assert res.pay_url == (
        "https://pay.lava.ru/invoice/31295617-3b7c-432c-a1a8-3ef38dc6afb7?lang=ru"
    )
    assert res.external_id == "31295617-3b7c-432c-a1a8-3ef38dc6afb7"


@pytest.mark.asyncio
async def test_create_invoice_reissues_when_previous_expired(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:lava")
    monkeypatch.setenv("USD_RUB_RATE", "100")
    monkeypatch.setenv("LAVA_SHOP_ID", "shop-uuid")
    monkeypatch.setenv("LAVA_SECRET_KEY", "s" * 16)
    monkeypatch.setenv("LAVA_HOOK_URL", "https://ex.example/hook")
    settings = Settings()

    expired_status = {"status": "expired", "id": "old-inv"}

    class FakeResp:
        status_code = 200
        text = ""

        def json(self):
            return {
                "data": {
                    "url": "https://pay.lava.ru/invoice/new-inv?lang=ru",
                    "id": "new-inv",
                }
            }

    posts: list[dict] = []

    async def fake_post(url, **_k):
        posts.append({"url": url})
        return FakeResp()

    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    client.post = fake_post

    with patch(
        "bot.services.lava_api.fetch_invoice_status",
        new=AsyncMock(return_value=expired_status),
    ), patch("bot.services.lava_api.httpx.AsyncClient", return_value=client):
        res = await create_invoice_payment_meta(
            settings,
            order_id=48,
            sum_rub=74.0,
            include_service=["card"],
            existing_invoice_id="old-inv",
            lava_attempt=1,
        )

    assert res.pay_url == "https://pay.lava.ru/invoice/new-inv?lang=ru"
    assert res.external_id == "new-inv"
    assert res.lava_attempt == 2
    assert res.error == "lava_invoice_expired_reissued"
    assert posts
