from __future__ import annotations

import time
from collections import defaultdict, deque


class PerClientRateLimiter:
    """Скользящее окно: не более max_hits за window_sec секунд на api_client_id."""

    def __init__(self, *, max_hits: int = 120, window_sec: float = 60.0) -> None:
        self.max_hits = max_hits
        self.window_sec = window_sec
        self._hits: dict[int, deque[float]] = defaultdict(deque)

    def allow(self, client_id: int) -> bool:
        now = time.monotonic()
        dq = self._hits[client_id]
        while dq and dq[0] < now - self.window_sec:
            dq.popleft()
        if len(dq) >= self.max_hits:
            return False
        dq.append(now)
        return True
