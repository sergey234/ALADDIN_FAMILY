"""IP sliding-window limits for anonymous web/device auth endpoints.

Sprint B: web register-device.
Step A (2026-11-06): recovery-code login shield — generous limits so a normal
family on one Wi‑Fi (retries, several phones) never feels a lockout.
"""
from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock
from typing import DefaultDict, List, Tuple

from fastapi import HTTPException, Request

_lock = Lock()
_buckets: DefaultDict[str, List[float]] = defaultdict(list)

# Recovery login: many honest retries (network blips) + several devices / NAT.
# Brute-force of 12-hex family ids is still impractical at 40/hour/IP.
DEFAULT_RECOVERY_LIMIT = 40
DEFAULT_RECOVERY_WINDOW_SEC = 3600


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _hit_or_raise(
    key: str,
    *,
    limit: int,
    window_sec: int,
    bucket: str,
    message: str,
) -> Tuple[str, int]:
    """Record one attempt; raise 429 if over budget. Returns (ip_suffix_key, count)."""
    now = time.time()
    with _lock:
        hits = _buckets[key]
        hits[:] = [t for t in hits if now - t < window_sec]
        if len(hits) >= limit:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "rate_limit",
                    "message": message,
                    "bucket": bucket,
                    "limit": limit,
                    "window_sec": window_sec,
                },
            )
        hits.append(now)
        return key, len(hits)


def check_web_register_ip_limit(
    request: Request,
    *,
    limit: int = 30,
    window_sec: int = 3600,
) -> None:
    """Raise HTTP 429 when IP exceeds web register-device budget."""
    ip = client_ip(request)
    _hit_or_raise(
        f"web_register:{ip}",
        limit=limit,
        window_sec=window_sec,
        bucket="web_register",
        message="Too many web sessions from this network. Try again later.",
    )


def check_recovery_login_ip_limit(
    request: Request,
    *,
    limit: int = DEFAULT_RECOVERY_LIMIT,
    window_sec: int = DEFAULT_RECOVERY_WINDOW_SEC,
) -> int:
    """Raise HTTP 429 when IP exceeds recovery-login budget. Returns attempt # in window."""
    ip = client_ip(request)
    _, count = _hit_or_raise(
        f"recovery_login:{ip}",
        limit=limit,
        window_sec=window_sec,
        bucket="recovery_login",
        message=(
            "Слишком много попыток входа с этой сети. "
            "Подождите немного и попробуйте снова — обычно хватает 1–2 минут."
        ),
    )
    return count
