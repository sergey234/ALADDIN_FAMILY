from __future__ import annotations

import asyncio
import hashlib
import logging
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from bot.config import Settings
from bot.services.alerts import send_alert
from partner_api.rate_limit_store import RateLimitStore, build_rate_limit_store

_log = logging.getLogger(__name__)


def _is_webhook_path(path: str) -> bool:
    p = path.lower()
    return "webhook" in p or p.endswith("/payments/provider-webhook")


def _client_ip(request: Request) -> str:
    if request.client:
        return request.client.host or "unknown"
    return "unknown"


class PartnerRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding window (60 s) per ключ.
    Backend: memory (default) или redis (общий лимит между репликами).
    - Вебхуки платежей: лимит на IP (PARTNER_API_RATE_LIMIT_WEBHOOK_PER_MINUTE).
    - /v1 с X-API-KEY: лимит на хэш ключа + IP (PARTNER_API_RATE_LIMIT_API_PER_MINUTE).
    - Прочее (health, docs, openapi): мягкий лимит на IP (PARTNER_API_RATE_LIMIT_PUBLIC_PER_MINUTE).
    0 в настройке — класс лимита отключён.
    """

    def __init__(self, app: Callable, *, store: RateLimitStore | None = None) -> None:
        super().__init__(app)
        self._store = store

    async def _allow(self, key: str, limit: int, settings: Settings) -> bool:
        store = self._store
        if store is None:
            store = build_rate_limit_store(settings)
            self._store = store
        return await store.check_and_consume(key, limit)

    def _resolve_limit_and_key(self, request: Request, settings: Settings) -> tuple[str, int]:
        path = request.url.path
        ip = _client_ip(request)
        if _is_webhook_path(path):
            return f"wh:{ip}", int(settings.partner_api_rate_limit_webhook_per_minute)
        if path.startswith("/v1"):
            raw = (request.headers.get("X-API-KEY") or "").strip()
            if raw:
                h = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]
                return f"api:{h}:{ip}", int(settings.partner_api_rate_limit_api_per_minute)
            return f"v1n:{ip}", int(settings.partner_api_rate_limit_api_per_minute)
        return f"pub:{ip}", int(settings.partner_api_rate_limit_public_per_minute)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        settings: Settings | None = getattr(request.app.state, "settings", None)
        if settings is None:
            return await call_next(request)
        key, limit = self._resolve_limit_and_key(request, settings)
        if not await self._allow(key, limit, settings):
            _log.warning("partner_api_rate_limit key=%s path=%s", key, request.url.path)
            return JSONResponse(
                {"code": "rate_limited", "message": "Too many requests. Retry later."},
                status_code=429,
            )
        response = await call_next(request)
        if _is_webhook_path(request.url.path) and response.status_code >= 400:
            _log.warning(
                "partner_api_webhook_error status=%s path=%s",
                response.status_code,
                request.url.path,
            )
            if settings.alerts_enabled:
                asyncio.create_task(
                    send_alert(
                        settings=settings,
                        severity="warning",
                        title="partner api webhook error",
                        body=f"status={response.status_code} path={request.url.path}",
                        dedupe_key=f"partner_api_webhook_error:{request.url.path}:{response.status_code}",
                    )
                )
        return response
