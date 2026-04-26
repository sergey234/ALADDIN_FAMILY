from __future__ import annotations

import asyncio
import json
import time
from typing import Any

import httpx

from bot.config import Settings

_DEFAULT_BASE = "https://v1.fragmentapi.com/api/v1/partner"
_MIN_INTERVAL_SEC = 1.1


class IstarFulfillError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None, body: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class IstarFulfillClient:
    """
    HTTP-клиент iStar (partner API): Stars / Premium, лимит ~1 req/s на ключ.
    Документация: https://istar.fragmentapi.com/docs
    """

    def __init__(self, settings: Settings, http: httpx.AsyncClient) -> None:
        self._settings = settings
        self._http = http
        self._throttle_lock = asyncio.Lock()
        self._last_request_mono: float = 0.0

    @staticmethod
    def is_configured(settings: Settings) -> bool:
        return bool((settings.istar_api_key or "").strip())

    @property
    def _base(self) -> str:
        raw = (self._settings.istar_api_base or "").strip()
        return (raw or _DEFAULT_BASE).rstrip("/")

    def _headers(self) -> dict[str, str]:
        key = (self._settings.istar_api_key or "").strip()
        return {"API-Key": key}

    def _wallet_type(self) -> str:
        w = (self._settings.istar_wallet_type or "TON").strip().upper()
        return w or "TON"

    async def _throttle(self) -> None:
        async with self._throttle_lock:
            now = time.monotonic()
            wait = _MIN_INTERVAL_SEC - (now - self._last_request_mono)
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_request_mono = time.monotonic()

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any:
        await self._throttle()
        url = f"{self._base}{path}" if path.startswith("/") else f"{self._base}/{path}"
        try:
            resp = await self._http.request(
                method,
                url,
                headers=self._headers(),
                params=params,
                json=json_body,
            )
        except httpx.RequestError as exc:
            raise IstarFulfillError(f"istar_http_error:{exc}") from exc

        text = resp.text
        if resp.status_code >= 400:
            raise IstarFulfillError(
                f"istar_http_{resp.status_code}",
                status_code=resp.status_code,
                body=text[:2000],
            )

        try:
            return json.loads(text) if text else {}
        except json.JSONDecodeError as exc:
            raise IstarFulfillError("istar_invalid_json", status_code=resp.status_code, body=text[:500]) from exc

    async def search_star_recipient(self, *, username: str, quantity: int) -> str:
        data = await self._request_json(
            "GET",
            "/star/recipient/search",
            params={"username": username, "quantity": int(quantity)},
        )
        if not isinstance(data, dict):
            raise IstarFulfillError("istar_star_search_bad_shape")
        if not data.get("success"):
            raise IstarFulfillError(f"istar_star_search_failed:{data!r}"[:500])
        h = data.get("recipient")
        if not isinstance(h, str) or not h.strip():
            raise IstarFulfillError("istar_star_search_no_recipient")
        return h.strip()

    async def create_star_order(self, *, username: str, recipient_hash: str, quantity: int) -> str:
        body = {
            "username": username,
            "recipient_hash": recipient_hash,
            "quantity": int(quantity),
            "wallet_type": self._wallet_type(),
        }
        data = await self._request_json("POST", "/orders/star", json_body=body)
        if not isinstance(data, dict):
            raise IstarFulfillError("istar_star_order_bad_shape")
        oid = data.get("order_id")
        if not isinstance(oid, str) or not oid.strip():
            raise IstarFulfillError(f"istar_star_order_no_id:{data!r}"[:500])
        return oid.strip()

    async def search_premium_recipient(self, *, username: str, months: int) -> str:
        data = await self._request_json(
            "GET",
            "/premium/recipient/search",
            params={"username": username, "months": int(months)},
        )
        if not isinstance(data, dict):
            raise IstarFulfillError("istar_premium_search_bad_shape")
        if not data.get("success"):
            raise IstarFulfillError(f"istar_premium_search_failed:{data!r}"[:500])
        h = data.get("recipient")
        if not isinstance(h, str) or not h.strip():
            raise IstarFulfillError("istar_premium_search_no_recipient")
        return h.strip()

    async def create_premium_order(self, *, username: str, recipient_hash: str, months: int) -> str:
        body = {
            "username": username,
            "recipient_hash": recipient_hash,
            "months": int(months),
            "wallet_type": self._wallet_type(),
        }
        data = await self._request_json("POST", "/orders/premium", json_body=body)
        if not isinstance(data, dict):
            raise IstarFulfillError("istar_premium_order_bad_shape")
        oid = data.get("order_id")
        if not isinstance(oid, str) or not oid.strip():
            raise IstarFulfillError(f"istar_premium_order_no_id:{data!r}"[:500])
        return oid.strip()
