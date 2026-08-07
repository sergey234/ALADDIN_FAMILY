from __future__ import annotations

import pytest

from bot.config import load_settings
from bot.services.istar_fulfill_client import IstarFulfillError
from bot.services.istar_wallet_monitor import (
    istar_error_is_server_http,
    notify_ops_istar_search_http_error,
)


def test_istar_error_is_server_http_detects_500() -> None:
    exc = IstarFulfillError("istar_http_500", status_code=500, body="Internal Server Error")
    assert istar_error_is_server_http(exc) is True


def test_istar_error_is_server_http_ignores_4xx() -> None:
    exc = IstarFulfillError("istar_http_404", status_code=404)
    assert istar_error_is_server_http(exc) is False


@pytest.mark.asyncio
async def test_notify_ops_istar_search_http_error_sends_for_5xx(monkeypatch: pytest.MonkeyPatch) -> None:
    sent: list[dict] = []

    async def fake_send_alert(settings, **kwargs):
        sent.append(kwargs)

    monkeypatch.setenv("BOT_TOKEN", "1:istar")
    monkeypatch.setenv("USD_RUB_RATE", "100")
    monkeypatch.setenv("AUTO_FULFILL_FAILURE_ALERTS_ENABLED", "true")
    settings = load_settings()
    monkeypatch.setattr("bot.services.istar_wallet_monitor.send_alert", fake_send_alert)

    exc = IstarFulfillError("istar_http_500", status_code=500)
    await notify_ops_istar_search_http_error(
        settings, order_id=10, username="testuser", exc=exc
    )
    assert len(sent) == 1
    assert sent[0]["title"] == "iStar API 5xx on recipient search"
    assert sent[0]["dedupe_key"] == "istar_search_http_5xx"


@pytest.mark.asyncio
async def test_notify_ops_istar_search_http_error_skips_4xx(monkeypatch: pytest.MonkeyPatch) -> None:
    sent: list[dict] = []

    async def fake_send_alert(settings, **kwargs):
        sent.append(kwargs)

    monkeypatch.setenv("BOT_TOKEN", "1:istar")
    monkeypatch.setenv("USD_RUB_RATE", "100")
    settings = load_settings()
    monkeypatch.setattr("bot.services.istar_wallet_monitor.send_alert", fake_send_alert)

    exc = IstarFulfillError("istar_star_search_failed:{'success': False}")
    await notify_ops_istar_search_http_error(
        settings, order_id=10, username="bad", exc=exc
    )
    assert sent == []
