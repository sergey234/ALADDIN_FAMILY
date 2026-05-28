from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from bot.config import Settings
from bot.services import vpn_api_circuit
from bot.services.vpn_ops_health import collect_vpn_ops_health


class _ClosedBreaker:
    def snapshot(self):
        from types import SimpleNamespace

        return SimpleNamespace(state=vpn_api_circuit.CircuitState.CLOSED)


@pytest.mark.asyncio
async def test_collect_vpn_ops_health_ok_when_api_up(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VPN_API_BASE_URL", "http://127.0.0.1:8002")
    monkeypatch.setenv("VPN_API_HMAC_SECRET", "x" * 32)
    settings = Settings(
        bot_token="1:test",
        vpn_ops_health_interval_seconds=300,
    )
    with (
        patch(
            "bot.services.vpn_ops_health.vpn_api_client.get_public_health",
            new_callable=AsyncMock,
            return_value=(True, '{"status":"ok"}'),
        ),
        patch(
            "bot.services.vpn_ops_health.vpn_api_client.get_public_ready",
            new_callable=AsyncMock,
            return_value=(True, {"status": "ready", "wg": "wg0"}, 200),
        ),
        patch(
            "bot.services.vpn_ops_health.admin_stats_repo.fetch_vpn_controlplane_metrics",
            new_callable=AsyncMock,
            return_value={
                "vpn_cp_available": 1,
                "vpn_cp_jobs_pending": 0,
                "vpn_cp_jobs_failed": 0,
                "vpn_cp_jobs_processing": 0,
                "vpn_cp_accounts_vpn_failed": 0,
                "vpn_cp_accounts_vpn_provisioning": 0,
            },
        ),
        patch(
            "bot.services.vpn_ops_health.admin_stats_repo.count_vpn_stale_pending_jobs",
            new_callable=AsyncMock,
            return_value=0,
        ),
        patch(
            "bot.services.vpn_ops_health.vpn_api_circuit.get_breaker",
            return_value=_ClosedBreaker(),
        ),
    ):
        snap = await collect_vpn_ops_health(settings)
    assert snap.issue_codes == [], snap.issue_codes
    assert snap.status == "ok"
