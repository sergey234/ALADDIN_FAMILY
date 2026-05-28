from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from bot.config import Settings
from bot.services.vpn_post_purchase_delivery import (
    _fetch_conf_when_ready,
    vpn_paid_ack_html,
    wg_conf_filename,
)


def test_wg_conf_filename() -> None:
    assert wg_conf_filename(12345) == "aladdin-wg-12345.conf"


def test_vpn_paid_ack_html_contains_order() -> None:
    html = vpn_paid_ack_html(order_id=99)
    assert "99" in html
    assert "AiMonkeyVPN" in html
    assert ".conf" in html
    assert "QR" in html
    assert "этот чат" in html


@pytest.mark.asyncio
async def test_fetch_conf_when_ready_immediate() -> None:
    settings = Settings(
        bot_token="1:test",
        vpn_api_base_url="http://127.0.0.1:8091",
        vpn_api_hmac_secret="x" * 32,
        vpn_provision_delivery_timeout_seconds=10,
        vpn_provision_delivery_poll_seconds=1,
    )
    with patch(
        "bot.services.vpn_post_purchase_delivery.vpn_api_client.post_wg_conf",
        new_callable=AsyncMock,
        return_value=(True, "[Interface]\n", ""),
    ):
        conf, err = await _fetch_conf_when_ready(settings, 42)
    assert conf == "[Interface]\n"
    assert err is None
