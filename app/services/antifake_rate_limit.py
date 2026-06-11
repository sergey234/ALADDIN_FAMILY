"""In-memory sliding-window rate limits for antifake (af-2-09)."""
from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock
from typing import DefaultDict, List

from fastapi import HTTPException

_lock = Lock()
_buckets: DefaultDict[str, List[float]] = defaultdict(list)


def check_rate_limit(*, user_id: int, bucket: str, limit: int, window_sec: int) -> None:
    """Raise HTTP 429 when user exceeds limit within window."""
    key = f"{user_id}:{bucket}"
    now = time.time()
    with _lock:
        hits = _buckets[key]
        hits[:] = [t for t in hits if now - t < window_sec]
        if len(hits) >= limit:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit",
                    "message": "Too many antifake requests. Try again later.",
                    "bucket": bucket,
                    "limit": limit,
                    "window_sec": window_sec,
                },
            )
        hits.append(now)
