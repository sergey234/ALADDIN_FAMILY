from __future__ import annotations

import asyncio

from bot.config import Settings
from bot.services import alerts


def test_send_alert_returns_false_when_disabled(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:test")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("USD_RUB_RATE", "75")
    monkeypatch.setenv("ALERTS_ENABLED", "false")
    s = Settings()
    out = asyncio.run(
        alerts.send_alert(
            settings=s,
            severity="warning",
            title="t",
            body="b",
            dedupe_key="k",
        )
    )
    assert out is False


def test_alert_dedupe_window_blocks_second_send() -> None:
    async def scenario() -> tuple[bool, bool]:
        k = "test:dedupe"
        a = await alerts._dedupe_allowed(k, cooldown_seconds=60, now_ts=100.0)
        b = await alerts._dedupe_allowed(k, cooldown_seconds=60, now_ts=120.0)
        return a, b

    first, second = asyncio.run(scenario())
    assert first is True
    assert second is False
