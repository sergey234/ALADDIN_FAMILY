"""Тесты backoff / retryable для vpn worker (vpn-26)."""

from __future__ import annotations

from aladdin_shop_vpn_api.worker import _is_retryable_job_error, _job_backoff_seconds


def test_retryable_unknown_job_type() -> None:
    assert not _is_retryable_job_error(RuntimeError("unknown job_type foo"))


def test_retryable_not_configured() -> None:
    assert not _is_retryable_job_error(RuntimeError("WG provision not configured"))


def test_retryable_generic() -> None:
    assert _is_retryable_job_error(RuntimeError("wg set failed: timeout"))


def test_backoff_grows() -> None:
    assert _job_backoff_seconds(1) == 30
    assert _job_backoff_seconds(2) == 60
    assert _job_backoff_seconds(10) == 300
