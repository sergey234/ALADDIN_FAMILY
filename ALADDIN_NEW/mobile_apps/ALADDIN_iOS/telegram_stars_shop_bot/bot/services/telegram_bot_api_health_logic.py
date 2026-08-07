"""Решение smart-restart (br-c*): getMe FAIL → никогда не restart."""

from __future__ import annotations


def should_smart_restart(
    *,
    getme_ok: bool,
    unit_active: bool,
    log_has_update_id: bool,
    log_has_timeout_storm: bool,
    restarts_this_hour: int,
    max_restarts_per_hour: int = 3,
    smart_restart_enabled: bool = True,
    seconds_since_last_restart: float | None = None,
    min_seconds_between_restarts: int = 1800,
) -> tuple[bool, str]:
    if not smart_restart_enabled:
        return False, "disabled"
    if not getme_ok:
        return False, "getme_fail_never_restart"
    if not unit_active:
        return False, "unit_not_active"
    if log_has_update_id:
        return False, "polling_alive"
    if not log_has_timeout_storm:
        return False, "no_timeout_evidence"
    if (
        seconds_since_last_restart is not None
        and seconds_since_last_restart < max(0, int(min_seconds_between_restarts))
    ):
        return False, "cooldown"
    if restarts_this_hour >= max_restarts_per_hour:
        return False, "storm_guard"
    return True, "restart"
