from __future__ import annotations

import asyncio
import json
import time
from typing import Any

import httpx

from bot.config import Settings

_DEFAULT_APIFRAGMENT_BASE = "https://apifragment.online"
_MIN_INTERVAL_SEC = 1.1
# Оплата выдачи Stars/Premium с баланса ApiFragment в USDT (сеть TON).
_APIFRAGMENT_PAYMENT_METHOD = "usdt_ton"


class IstarFulfillError(Exception):
    """Ошибка HTTP/контракта ApiFragment (имя класса сохранено для совместимости импортов)."""

    def __init__(self, message: str, *, status_code: int | None = None, body: str | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body


class IstarFulfillClient:
    """HTTP-клиент автовыдачи Stars/Premium через ApiFragment (apifragment.online)."""

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
        if raw:
            return raw.rstrip("/")
        return _DEFAULT_APIFRAGMENT_BASE

    def _headers(self) -> dict[str, str]:
        key = (self._settings.istar_api_key or "").strip()
        return {"Authorization": f"Bearer {key}"}

    def _apifragment_webhook_url(self) -> str:
        url = (self._settings.apifragment_webhook_public_url or "").strip()
        if url:
            return url
        return "https://aladdin-ai.ru/v1/payments/apifragment-webhook"

    def _payment_method(self) -> str:
        raw = (getattr(self._settings, "apifragment_payment_method", None) or "").strip().lower()
        if raw in ("ton", "usdt_ton"):
            return raw
        return _APIFRAGMENT_PAYMENT_METHOD

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
            raise IstarFulfillError(f"apifragment_http_error:{exc}") from exc

        text = resp.text
        if resp.status_code >= 400:
            detail = text[:2000]
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict) and parsed.get("detail"):
                    detail = str(parsed["detail"])[:2000]
            except json.JSONDecodeError:
                pass
            raise IstarFulfillError(
                f"apifragment_http_{resp.status_code}",
                status_code=resp.status_code,
                body=detail,
            )

        try:
            return json.loads(text) if text else {}
        except json.JSONDecodeError as exc:
            raise IstarFulfillError(
                "apifragment_invalid_json", status_code=resp.status_code, body=text[:500]
            ) from exc

    async def search_star_recipient(self, *, username: str, quantity: int) -> str:
        _ = quantity
        uname = (username or "").strip().lstrip("@")
        data = await self._request_json("GET", f"/resolve_user/{uname}")
        if not isinstance(data, dict):
            raise IstarFulfillError("apifragment_resolve_bad_shape")
        return uname

    async def create_star_order(
        self,
        *,
        username: str,
        recipient_hash: str,
        quantity: int,
        order_id: int | None = None,
    ) -> str:
        uname = (username or recipient_hash or "").strip().lstrip("@")
        body: dict[str, Any] = {
            "username": uname,
            "quantity": int(quantity),
            "payment_method": self._payment_method(),
            "webhook_url": self._apifragment_webhook_url(),
        }
        if order_id is not None:
            body["idempotency_key"] = f"shop-{int(order_id)}"
        data = await self._request_json("POST", "/stars", json_body=body)
        if not isinstance(data, dict):
            raise IstarFulfillError("apifragment_star_order_bad_shape")
        task_id = data.get("task_id") or data.get("order_id")
        if task_id is None:
            raise IstarFulfillError(f"apifragment_star_order_no_task:{data!r}"[:500])
        return str(task_id).strip()

    async def search_premium_recipient(self, *, username: str, months: int) -> str:
        _ = months
        uname = (username or "").strip().lstrip("@")
        data = await self._request_json("GET", f"/resolve_user/{uname}")
        if not isinstance(data, dict):
            raise IstarFulfillError("apifragment_resolve_bad_shape")
        return uname

    async def create_premium_order(
        self,
        *,
        username: str,
        recipient_hash: str,
        months: int,
        order_id: int | None = None,
    ) -> str:
        uname = (username or recipient_hash or "").strip().lstrip("@")
        body: dict[str, Any] = {
            "username": uname,
            "months": int(months),
            "payment_method": self._payment_method(),
            "webhook_url": self._apifragment_webhook_url(),
        }
        if order_id is not None:
            body["idempotency_key"] = f"shop-{int(order_id)}"
        data = await self._request_json("POST", "/premium", json_body=body)
        if not isinstance(data, dict):
            raise IstarFulfillError("apifragment_premium_order_bad_shape")
        task_id = data.get("task_id") or data.get("order_id")
        if task_id is None:
            raise IstarFulfillError(f"apifragment_premium_order_no_task:{data!r}"[:500])
        return str(task_id).strip()

    async def get_partner_order(self, external_order_id: str) -> dict[str, Any]:
        ext = (external_order_id or "").strip()
        if not ext:
            raise IstarFulfillError("apifragment_task_id_empty")
        data = await self._request_json("GET", f"/task/{ext}")
        if not isinstance(data, dict):
            raise IstarFulfillError("apifragment_task_bad_shape")
        return data

    @staticmethod
    def partner_order_status(data: dict[str, Any]) -> str:
        raw = data.get("status")
        if raw is None and isinstance(data.get("order"), dict):
            raw = data["order"].get("status")
        st = str(raw or "").strip().lower()
        if st in ("completed", "success", "done", "ok", "finished"):
            return "completed"
        if st in ("failed", "error", "cancelled", "canceled", "fail"):
            return "failed"
        return st

    async def get_wallet_balance_ton(self) -> float:
        data = await self._request_json("GET", "/balance")
        if not isinstance(data, dict):
            raise IstarFulfillError("apifragment_wallet_balance_bad_shape")
        raw = data.get("balance_ton")
        try:
            return float(raw)
        except (TypeError, ValueError) as exc:
            raise IstarFulfillError(f"apifragment_wallet_balance_invalid:{raw!r}"[:200]) from exc

    async def register_webhook_url(self, webhook_url: str) -> None:
        await self._request_json(
            "POST",
            "/webhook",
            json_body={"webhook_url": (webhook_url or "").strip()},
        )
