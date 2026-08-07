"""
Circuit breaker для HTTP-вызовов aladdin-shop-vpn-api (vpn-25).

In-process состояние (один процесс бота). При OPEN новые вызовы отклоняются до cooldown.
"""

from __future__ import annotations

import logging
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum

_log = logging.getLogger(__name__)


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class _CircuitSnapshot:
    state: CircuitState
    failures_in_window: int
    opened_until: float


class VpnApiCircuitBreaker:
    def __init__(
        self,
        *,
        failure_threshold: int = 5,
        failure_window_seconds: float = 120.0,
        open_seconds: float = 60.0,
    ) -> None:
        self.failure_threshold = max(1, failure_threshold)
        self.failure_window_seconds = max(1.0, failure_window_seconds)
        self.open_seconds = max(1.0, open_seconds)
        self._fail_ts: deque[float] = deque()
        self._state = CircuitState.CLOSED
        self._opened_until = 0.0
        self._half_open_probe_allowed = True

    def snapshot(self) -> _CircuitSnapshot:
        self._prune_failures()
        return _CircuitSnapshot(
            state=self._state,
            failures_in_window=len(self._fail_ts),
            opened_until=self._opened_until,
        )

    def _prune_failures(self, now: float | None = None) -> None:
        t = now if now is not None else time.time()
        cutoff = t - self.failure_window_seconds
        while self._fail_ts and self._fail_ts[0] < cutoff:
            self._fail_ts.popleft()

    def _transition_open(self, now: float) -> bool:
        """True если только что перешли в OPEN."""
        if self._state == CircuitState.OPEN:
            return False
        self._state = CircuitState.OPEN
        self._opened_until = now + self.open_seconds
        self._half_open_probe_allowed = True
        _log.warning(
            "vpn_api circuit OPEN for %.0fs (failures=%s in %.0fs window)",
            self.open_seconds,
            len(self._fail_ts),
            self.failure_window_seconds,
        )
        return True

    def allow_request(self) -> tuple[bool, str]:
        now = time.time()
        if self._state == CircuitState.OPEN:
            if now < self._opened_until:
                return False, "vpn-api circuit open (cooldown)"
            self._state = CircuitState.HALF_OPEN
            self._half_open_probe_allowed = True
            _log.info("vpn_api circuit HALF_OPEN (probe allowed)")

        if self._state == CircuitState.HALF_OPEN:
            if not self._half_open_probe_allowed:
                return False, "vpn-api circuit half-open (probe in flight)"
        return True, ""

    def record_success(self) -> None:
        self._state = CircuitState.CLOSED
        self._opened_until = 0.0
        self._half_open_probe_allowed = True
        self._fail_ts.clear()

    def record_failure(self) -> bool:
        """
        Учитывает сбой (5xx / сеть / 429). Возвращает True, если circuit только что открылся.
        """
        now = time.time()
        if self._state == CircuitState.HALF_OPEN:
            opened = self._transition_open(now)
            return opened

        self._prune_failures(now)
        self._fail_ts.append(now)
        if len(self._fail_ts) >= self.failure_threshold:
            return self._transition_open(now)
        return False

    def mark_probe_started(self) -> None:
        if self._state == CircuitState.HALF_OPEN:
            self._half_open_probe_allowed = False


# Глобальный breaker на процесс (параметры обновляются из Settings при каждом вызове).
_breaker = VpnApiCircuitBreaker()


def get_breaker(
    *,
    failure_threshold: int,
    failure_window_seconds: float,
    open_seconds: float,
) -> VpnApiCircuitBreaker:
    global _breaker
    _breaker.failure_threshold = max(1, failure_threshold)
    _breaker.failure_window_seconds = max(1.0, failure_window_seconds)
    _breaker.open_seconds = max(1.0, open_seconds)
    return _breaker
