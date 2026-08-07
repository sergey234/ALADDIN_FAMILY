from __future__ import annotations

import asyncio
import logging
import time
from typing import Protocol
from urllib.parse import quote_plus

from bot.config import Settings

_log = logging.getLogger(__name__)


class RateLimitStore(Protocol):
    async def check_and_consume(self, bucket_id: str, limit_per_minute: int) -> bool:
        ...


class MemoryRateLimitStore:
    WINDOW_SEC = 60.0

    def __init__(self) -> None:
        self._buckets: dict[str, list[float]] = {}
        self._lock: asyncio.Lock | None = None

    async def check_and_consume(self, bucket_id: str, limit_per_minute: int) -> bool:
        if int(limit_per_minute) <= 0:
            return True
        now = time.monotonic()
        cutoff = now - self.WINDOW_SEC
        if self._lock is None:
            self._lock = asyncio.Lock()
        async with self._lock:
            bucket = self._buckets.setdefault(bucket_id, [])
            while bucket and bucket[0] < cutoff:
                bucket.pop(0)
            if len(bucket) >= int(limit_per_minute):
                return False
            bucket.append(now)
            return True


class RedisRateLimitStore:
    WINDOW_SEC = 60

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = None
        self._fallback_store = MemoryRateLimitStore()
        self._warned_unavailable = False

    def _build_redis_url(self) -> str:
        raw = (self._settings.redis_url or "").strip()
        if raw:
            return raw
        host = (self._settings.redis_host or "").strip() or "127.0.0.1"
        port = int(self._settings.redis_port or 6379)
        db = int(self._settings.redis_db or 0)
        pwd = (self._settings.redis_password or "").strip()
        if pwd:
            return f"redis://:{quote_plus(pwd)}@{host}:{port}/{db}"
        return f"redis://{host}:{port}/{db}"

    async def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            from redis.asyncio import Redis
        except Exception:
            if not self._warned_unavailable:
                _log.warning("rate_limit_redis_module_unavailable_fallback_memory")
                self._warned_unavailable = True
            return None
        try:
            cli = Redis.from_url(self._build_redis_url(), decode_responses=True)
            await cli.ping()
            self._client = cli
            return self._client
        except Exception:
            if not self._warned_unavailable:
                _log.warning("rate_limit_redis_connect_failed_fallback_memory", exc_info=True)
                self._warned_unavailable = True
            return None

    async def check_and_consume(self, bucket_id: str, limit_per_minute: int) -> bool:
        if int(limit_per_minute) <= 0:
            return True
        cli = await self._get_client()
        if cli is None:
            return await self._fallback_store.check_and_consume(bucket_id, limit_per_minute)
        key = f"aladdin:rl:{bucket_id}"
        try:
            cur = await cli.incr(key)
            if cur == 1:
                await cli.expire(key, self.WINDOW_SEC)
            return int(cur) <= int(limit_per_minute)
        except Exception:
            _log.warning("rate_limit_redis_runtime_failed_fallback_memory", exc_info=True)
            return await self._fallback_store.check_and_consume(bucket_id, limit_per_minute)


def build_rate_limit_store(settings: Settings) -> RateLimitStore:
    backend = (settings.partner_api_rate_limit_backend or "memory").strip().lower()
    if backend == "redis":
        return RedisRateLimitStore(settings)
    return MemoryRateLimitStore()
