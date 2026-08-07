from __future__ import annotations

from bot.services.telegram_bot_api_health_logic import should_smart_restart


def test_getme_fail_never_restart() -> None:
    ok, reason = should_smart_restart(
        getme_ok=False,
        unit_active=True,
        log_has_update_id=False,
        log_has_timeout_storm=True,
        restarts_this_hour=0,
    )
    assert ok is False
    assert reason == "getme_fail_never_restart"


def test_getme_ok_with_updates_no_restart() -> None:
    ok, reason = should_smart_restart(
        getme_ok=True,
        unit_active=True,
        log_has_update_id=True,
        log_has_timeout_storm=True,
        restarts_this_hour=0,
    )
    assert ok is False
    assert reason == "polling_alive"


def test_getme_ok_stale_timeout_restart() -> None:
    ok, reason = should_smart_restart(
        getme_ok=True,
        unit_active=True,
        log_has_update_id=False,
        log_has_timeout_storm=True,
        restarts_this_hour=0,
    )
    assert ok is True
    assert reason == "restart"


def test_storm_guard() -> None:
    ok, reason = should_smart_restart(
        getme_ok=True,
        unit_active=True,
        log_has_update_id=False,
        log_has_timeout_storm=True,
        restarts_this_hour=3,
        max_restarts_per_hour=3,
    )
    assert ok is False
    assert reason == "storm_guard"


def test_cooldown_blocks_restart() -> None:
    ok, reason = should_smart_restart(
        getme_ok=True,
        unit_active=True,
        log_has_update_id=False,
        log_has_timeout_storm=True,
        restarts_this_hour=0,
        seconds_since_last_restart=60,
        min_seconds_between_restarts=1800,
    )
    assert ok is False
    assert reason == "cooldown"
