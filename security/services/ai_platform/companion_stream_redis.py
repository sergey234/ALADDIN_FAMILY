# -*- coding: utf-8 -*-
"""P1-12 (partial) — Redis-backed companion stream token cache with SQLite fallback."""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_REDIS_PREFIX = "companion:stream:"
_DEFAULT_TTL_SEC = int(os.getenv("COMPANION_STREAM_CACHE_TTL_SEC", "1800"))


def stream_cache_backend() -> str:
    return os.getenv("COMPANION_STREAM_CACHE_BACKEND", "sqlite").strip().lower()


def _redis_client():
    try:
        import redis  # type: ignore
    except ImportError:
        return None
    url = os.getenv("REDIS_URL") or os.getenv("COMPANION_REDIS_URL")
    if not url:
        return None
    try:
        return redis.Redis.from_url(url, decode_responses=True)
    except Exception as exc:
        logger.warning("Companion Redis unavailable: %s", exc)
        return None


def put_stream_cache_redis(
    message_id: str,
    user_id: str,
    tokens: List[str],
    meta: Dict[str, Any],
    *,
    ttl_sec: int = _DEFAULT_TTL_SEC,
) -> bool:
    client = _redis_client()
    if client is None:
        return False
    payload = json.dumps({"user_id": user_id, "tokens": tokens, "meta": meta})
    try:
        client.setex(f"{_REDIS_PREFIX}{message_id}", ttl_sec, payload)
        return True
    except Exception as exc:
        logger.warning("put_stream_cache_redis failed: %s", exc)
        return False


def get_stream_cache_redis(
    message_id: str, user_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    client = _redis_client()
    if client is None:
        return None
    try:
        raw = client.get(f"{_REDIS_PREFIX}{message_id}")
        if not raw:
            return None
        data = json.loads(raw)
        if user_id and str(data.get("user_id")) != str(user_id):
            return None
        return {"tokens": data.get("tokens") or [], "meta": data.get("meta") or {}}
    except Exception as exc:
        logger.warning("get_stream_cache_redis failed: %s", exc)
        return None


def delete_stream_cache_redis(message_id: str) -> None:
    client = _redis_client()
    if client is None:
        return
    try:
        client.delete(f"{_REDIS_PREFIX}{message_id}")
    except Exception as exc:
        logger.warning("delete_stream_cache_redis failed: %s", exc)
