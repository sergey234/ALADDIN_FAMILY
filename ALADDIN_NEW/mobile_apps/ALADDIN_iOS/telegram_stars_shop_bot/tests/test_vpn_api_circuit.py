"""Тесты circuit breaker vpn-api (vpn-25)."""

from __future__ import annotations

from bot.services.vpn_api_circuit import CircuitState, VpnApiCircuitBreaker, get_breaker


def test_circuit_opens_after_threshold() -> None:
    b = VpnApiCircuitBreaker(failure_threshold=3, failure_window_seconds=60, open_seconds=30)
    assert b.allow_request()[0]
    assert not b.record_failure()
    assert not b.record_failure()
    opened = b.record_failure()
    assert opened
    assert b.snapshot().state == CircuitState.OPEN
    allowed, reason = b.allow_request()
    assert not allowed
    assert "circuit open" in reason


def test_circuit_closes_on_success() -> None:
    b = VpnApiCircuitBreaker(failure_threshold=2, failure_window_seconds=60, open_seconds=1)
    b.record_failure()
    b.record_failure()
    assert b.snapshot().state == CircuitState.OPEN
    b.record_success()
    assert b.snapshot().state == CircuitState.CLOSED
    assert b.allow_request()[0]


def test_get_breaker_updates_params() -> None:
    b = get_breaker(failure_threshold=7, failure_window_seconds=90, open_seconds=45)
    assert b.failure_threshold == 7
    assert b.failure_window_seconds == 90.0
    assert b.open_seconds == 45.0
