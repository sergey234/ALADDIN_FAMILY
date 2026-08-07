from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from bot.config import Settings
from bot.services import vpn_api_circuit
from bot.services import vpn_ops_health as voh
from bot.services.vpn_ops_health import collect_vpn_ops_health, maybe_alert_vpn_ops_health


class _ClosedBreaker:
    def snapshot(self):
        from types import SimpleNamespace

        return SimpleNamespace(state=vpn_api_circuit.CircuitState.CLOSED)


@pytest.fixture(autouse=True)
def _reset_streak(monkeypatch: pytest.MonkeyPatch) -> None:
    voh._bad_streak = 0
    voh._last_notified_status = "ok"
    voh._last_alert_sent_ts = 0.0
    monkeypatch.setenv("VPN_PATH_METRICS_ENABLED", "false")


def test_digest_sleep_respects_interval() -> None:
    from bot.services.vpn_ops_health import digest_sleep_seconds

    assert digest_sleep_seconds(interval=18000, last_sent_ts=0.0, now_ts=1_000_000.0) == 45.0
    # только что отправили — ждать полный интервал
    assert digest_sleep_seconds(interval=18000, last_sent_ts=1_000_000.0, now_ts=1_000_000.0) == 18000.0
    # прошло 2 часа из 5 — осталось 3 часа
    assert digest_sleep_seconds(
        interval=18000, last_sent_ts=1_000_000.0, now_ts=1_000_000.0 + 7200
    ) == 10800.0
    # интервал уже вышел
    assert digest_sleep_seconds(
        interval=18000, last_sent_ts=1_000_000.0, now_ts=1_000_000.0 + 18000
    ) == 0.0


def test_digest_state_roundtrip(tmp_path) -> None:
    from bot.services.vpn_ops_health import load_last_digest_sent_ts, save_last_digest_sent_ts

    p = tmp_path / "digest.last_ts"
    assert load_last_digest_sent_ts(p) == 0.0
    save_last_digest_sent_ts(12345.5, p)
    assert load_last_digest_sent_ts(p) == 12345.5


@pytest.mark.asyncio
async def test_vpn_ops_health_alert_throttled_same_status(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALERTS_ENABLED", "true")
    settings = Settings(
        bot_token="1:test",
        vpn_ops_health_critical_after=1,
        vpn_ops_health_alert_cooldown_seconds=18000,
    )
    snap = voh.VpnOpsHealthSnapshot(
        status="degraded",
        checked_at_utc="2026-01-01T00:00:00+00:00",
        issue_codes=["swap_149_high"],
        lines_html=["swap"],
    )
    sent: list[str] = []

    async def _fake_alert(_settings, *, severity, title, body, dedupe_key) -> bool:
        sent.append(title)
        return True

    with patch("bot.services.vpn_ops_health.send_alert", side_effect=_fake_alert):
        await maybe_alert_vpn_ops_health(settings, snap)
        await maybe_alert_vpn_ops_health(settings, snap)
    assert len(sent) == 1
    assert "degraded" in sent[0]


@pytest.mark.asyncio
async def test_vpn_ops_health_alert_body_is_short(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ALERTS_ENABLED", "true")
    settings = Settings(
        bot_token="1:test",
        vpn_ops_health_critical_after=1,
        vpn_ops_health_alert_cooldown_seconds=18000,
    )
    long_report = ["• API ok", "<b>📊 VPN — полный отчёт</b>", "1) Мост RTT"] * 5
    snap = voh.VpnOpsHealthSnapshot(
        status="degraded",
        checked_at_utc="2026-01-01T00:00:00+00:00",
        issue_codes=["swap_149_elevated", "contabo_cf_volatile"],
        lines_html=long_report,
    )
    bodies: list[str] = []

    async def _fake_alert(_settings, *, severity, title, body, dedupe_key) -> bool:
        bodies.append(body)
        return True

    with patch("bot.services.vpn_ops_health.send_alert", side_effect=_fake_alert):
        await maybe_alert_vpn_ops_health(settings, snap)
    assert bodies
    assert "полный отчёт" not in bodies[0].lower() or "дайджест" in bodies[0].lower()
    assert "swap_149_elevated" not in bodies[0]  # human hint, not raw code only
    assert "высокий swap" in bodies[0].lower() or "повышенный swap" in bodies[0].lower()
    assert "Мост RTT" not in bodies[0]


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
    assert snap.status == "ok"
    assert snap.issue_codes == []


@pytest.mark.asyncio
async def test_ready_fail_is_degraded_not_critical(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VPN_API_BASE_URL", "http://127.0.0.1:8091")
    settings = Settings(bot_token="1:test")
    with (
        patch(
            "bot.services.vpn_ops_health.vpn_api_client.get_public_health",
            new_callable=AsyncMock,
            return_value=(True, "ok"),
        ),
        patch(
            "bot.services.vpn_ops_health.vpn_api_client.get_public_ready",
            new_callable=AsyncMock,
            return_value=(False, "HTTP 503: wg down", 503),
        ),
        patch(
            "bot.services.vpn_ops_health.admin_stats_repo.fetch_vpn_controlplane_metrics",
            new_callable=AsyncMock,
            return_value={"vpn_cp_available": 1, "vpn_cp_jobs_pending": 0, "vpn_cp_jobs_failed": 0,
                          "vpn_cp_jobs_processing": 0, "vpn_cp_accounts_vpn_failed": 0,
                          "vpn_cp_accounts_vpn_provisioning": 0},
        ),
        patch(
            "bot.services.vpn_ops_health.admin_stats_repo.count_vpn_stale_pending_jobs",
            new_callable=AsyncMock,
            return_value=0,
        ),
        patch("bot.services.vpn_ops_health.vpn_api_circuit.get_breaker", return_value=_ClosedBreaker()),
    ):
        snap = await collect_vpn_ops_health(settings)
    assert snap.status == "degraded"
    assert "api_ready_fail" in snap.issue_codes
    assert "api_health_down" not in snap.issue_codes


@pytest.mark.asyncio
async def test_critical_alert_requires_consecutive_failures() -> None:
    settings = Settings(
        bot_token="1:test",
        vpn_ops_health_critical_after=2,
        vpn_ops_health_interval_seconds=300,
    )
    snap = voh.VpnOpsHealthSnapshot(
        status="critical",
        checked_at_utc="2026-01-01T00:00:00+00:00",
        issue_codes=["api_health_down"],
        lines_html=["fail"],
    )
    sent: list[str] = []

    async def _fake_alert(_settings, *, severity, title, body, dedupe_key) -> bool:
        sent.append(severity)
        return True

    with patch("bot.services.vpn_ops_health.send_alert", side_effect=_fake_alert):
        await maybe_alert_vpn_ops_health(settings, snap)
        assert sent == ["warning"]
        await maybe_alert_vpn_ops_health(settings, snap)
        assert sent == ["warning", "critical"]
