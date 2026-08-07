from __future__ import annotations

import pytest

from bot.config import load_settings
from bot.services.ops_order_notify import notify_ops_order_auto_completed


@pytest.mark.asyncio
async def test_notify_ops_order_auto_completed_sends(monkeypatch: pytest.MonkeyPatch) -> None:
    sent: list[dict] = []

    async def fake_send_alert(settings, **kwargs):
        sent.append(kwargs)

    monkeypatch.setenv("BOT_TOKEN", "1:ops")
    monkeypatch.setenv("USD_RUB_RATE", "100")
    monkeypatch.setenv("ALERTS_ENABLED", "true")
    monkeypatch.setenv("AUTO_FULFILL_SUCCESS_ALERTS_ENABLED", "true")
    settings = load_settings()
    monkeypatch.setattr("bot.services.ops_order_notify.send_alert", fake_send_alert)

    await notify_ops_order_auto_completed(
        settings,
        order_id=44,
        user_id=744254201,
        product_title="⭐ 50 Stars",
        recipient="@Mishabakh",
        provider_ref="c78dbe0a-test",
    )
    assert len(sent) == 1
    assert sent[0]["title"] == "Автовыдача: заказ выдан"
    assert "order_id=#44" in sent[0]["body"]
