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
        ISTAR_API_KEY="test-istar-key",
        ISTAR_API_BASE="https://v1.fragmentapi.com/api/v1/partner",
    )


@pytest.mark.asyncio
async def test_search_star_recipient_success() -> None:
    resp = httpx.Response(200, json={"success": True, "recipient": "HASH1", "name": "U"})
    http = MagicMock()
    http.request = AsyncMock(return_value=resp)
    c = IstarFulfillClient(_settings(), http)
    h = await c.search_star_recipient(username="john", quantity=100)
    assert h == "HASH1"
    http.request.assert_called_once()


@pytest.mark.asyncio
async def test_search_star_recipient_api_error_body() -> None:
    resp = httpx.Response(200, json={"success": False, "error": "nope"})
    http = MagicMock()
    http.request = AsyncMock(return_value=resp)
    c = IstarFulfillClient(_settings(), http)
    with pytest.raises(IstarFulfillError, match="istar_star_search_failed"):
        await c.search_star_recipient(username="john", quantity=100)


@pytest.mark.asyncio
async def test_create_star_order_success() -> None:
    resp = httpx.Response(
        200,
        json={
            "order_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "pending",
            "username": "john",
            "quantity": 100,
        },
    )
    http = MagicMock()
    http.request = AsyncMock(return_value=resp)
    c = IstarFulfillClient(_settings(), http)
    oid = await c.create_star_order(username="john", recipient_hash="HASH1", quantity=100)
    assert oid == "550e8400-e29b-41d4-a716-446655440000"
