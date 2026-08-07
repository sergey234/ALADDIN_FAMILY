"""Circuit breaker: пауза автовыдачи при серии 5xx от iStar."""

from __future__ import annotations

import logging
import time

_log = logging.getLogger(__name__)

# Подряд временных сбоев → пауза всего воркера.
_OPEN_AFTER_CONSECUTIVE = 3
_OPEN_DURATION_SEC = 30 * 60

_consecutive_transient: int = 0
_open_until_mono: float = 0.0


def istar_circuit_is_open() -> bool:
    return time.monotonic() < _open_until_mono


def istar_circuit_seconds_until_open() -> int:
    if not istar_circuit_is_open():
        return 0
    return max(0, int(_open_until_mono - time.monotonic()))


def istar_circuit_record_success() -> None:
    global _consecutive_transient, _open_until_mono
    _consecutive_transient = 0
    _open_until_mono = 0.0


def istar_circuit_record_transient_failure() -> bool:
    """
    Учитывает временный сбой. Возвращает True, если circuit только что открыт.
    """
    global _consecutive_transient, _open_until_mono
    _consecutive_transient += 1
    if _consecutive_transient < _OPEN_AFTER_CONSECUTIVE:
        return False
    _open_until_mono = time.monotonic() + _OPEN_DURATION_SEC
    _consecutive_transient = 0
    _log.warning(
        "istar_circuit_open duration_sec=%s reason=consecutive_transient_failures",
        _OPEN_DURATION_SEC,
    )
    return True
