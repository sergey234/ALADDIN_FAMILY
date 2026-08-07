from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from bot.config import Settings
from bot.services.istar_fulfill_client import IstarFulfillClient, IstarFulfillError


def _settings() -> Settings:
    return Settings(  # type: ignore[call-arg]
        BOT_TOKEN="9:t",
        ADMIN_IDS="1",
        API_KEY_PEPPER="k" * 32,
        ISTAR_API_KEY="test-apifragment-key",
        ISTAR_API_BASE="https://apifragment.online",
        APIFRAGMENT_PAYMENT_METHOD="usdt_ton",
    )


@pytest.mark.asyncio
async def test_search_star_recipient_success() -> None:
    resp = httpx.Response(200, json={"username": "john", "name": "U"})
    http = MagicMock()
    http.request = AsyncMock(return_value=resp)
    c = IstarFulfillClient(_settings(), http)
    h = await c.search_star_recipient(username="john", quantity=100)
    assert h == "john"
    http.request.assert_called_once()
    args = http.request.await_args
    assert "/resolve_user/john" in str(args)


@pytest.mark.asyncio
async def test_search_star_recipient_bad_shape() -> None:
    resp = httpx.Response(200, json=["not", "a", "dict"])
    http = MagicMock()
    http.request = AsyncMock(return_value=resp)
    c = IstarFulfillClient(_settings(), http)
    with pytest.raises(IstarFulfillError, match="apifragment_resolve_bad_shape"):
        await c.search_star_recipient(username="john", quantity=100)


@pytest.mark.asyncio
async def test_create_star_order_success() -> None:
    resp = httpx.Response(
        200,
        json={
            "task_id": 22201,
            "status": "accepted",
            "message": "queued",
        },
    )
    http = MagicMock()
    http.request = AsyncMock(return_value=resp)
    c = IstarFulfillClient(_settings(), http)
    oid = await c.create_star_order(
        username="john", recipient_hash="john", quantity=100, order_id=55
    )
    assert oid == "22201"
    kwargs = http.request.await_args.kwargs
    body = kwargs.get("json") or {}
    assert body.get("payment_method") == "usdt_ton"
    assert body.get("idempotency_key") == "shop-55"
    assert "/stars" in str(http.request.await_args)
