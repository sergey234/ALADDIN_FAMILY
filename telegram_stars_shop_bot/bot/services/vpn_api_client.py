from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import secrets
import time
from typing import Any

import httpx

from bot.config import Settings
from bot.services import vpn_api_circuit
from bot.services.alerts import send_alert

_log = logging.getLogger(__name__)


def _signing_base(*, method: str, path: str, timestamp: str, nonce: str, body: bytes) -> bytes:
    body_hash = hashlib.sha256(body or b"").hexdigest()
    msg = f"{method.upper()}\n{path}\n{timestamp}\n{nonce}\n{body_hash}"
    return msg.encode("utf-8")


def _compute_signature(secret: str, *, method: str, path: str, timestamp: str, nonce: str, body: bytes) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        _signing_base(method=method, path=path, timestamp=timestamp, nonce=nonce, body=body),
        hashlib.sha256,
    ).hexdigest()
    return digest


def _breaker_for(settings: Settings) -> vpn_api_circuit.VpnApiCircuitBreaker:
    return vpn_api_circuit.get_breaker(
        failure_threshold=settings.vpn_api_circuit_failure_threshold,
        failure_window_seconds=float(settings.vpn_api_circuit_failure_window_seconds),
        open_seconds=float(settings.vpn_api_circuit_open_seconds),
    )


def _is_retryable_status(code: int) -> bool:
    return code in (429, 502, 503, 504) or code >= 500


def _counts_toward_circuit(code: int) -> bool:
    return _is_retryable_status(code)


def _base_secret(settings: Settings) -> tuple[str, str] | None:
    base = (settings.vpn_api_base_url or "").strip().rstrip("/")
    secret = (settings.vpn_api_hmac_secret or "").strip()
    if not base or not secret:
        return None
    return base, secret


async def _maybe_alert_circuit_open(settings: Settings) -> None:
    await send_alert(
        settings,
        severity="warning",
        title="VPN API circuit open",
        body=(
            "Бот временно не вызывает aladdin-shop-vpn-api (серия ошибок). "
            "Проверьте systemctl aladdin-shop-vpn-api, /ready и очередь jobs."
        ),
        dedupe_key="vpn_api_circuit_open",
    )


async def _request_vpn_api(
    settings: Settings,
    *,
    method: str,
    path: str,
    body: bytes,
    timeout: float,
    idempotency_key: str | None = None,
    accept: str | None = None,
) -> tuple[bool, httpx.Response | None, str]:
    """
    Единая точка HTTP к vpn-api: circuit breaker + ретраи на 429/5xx и сеть.
  """
    creds = _base_secret(settings)
    if creds is None:
        return False, None, "VPN_API_BASE_URL or VPN_API_HMAC_SECRET not set"

    base, secret = creds
    breaker = _breaker_for(settings)
    allowed, deny_reason = breaker.allow_request()
    if not allowed:
        return False, None, deny_reason

    if breaker.snapshot().state == vpn_api_circuit.CircuitState.HALF_OPEN:
        breaker.mark_probe_started()

    url = f"{base}{path}"
    max_retries = max(0, min(int(settings.vpn_api_http_max_retries), 5))
    last_err = "unknown error"

    for attempt in range(max_retries + 1):
        ts = str(int(time.time()))
        nonce = secrets.token_hex(16)
        sig = _compute_signature(secret, method=method, path=path, timestamp=ts, nonce=nonce, body=body)
        headers: dict[str, str] = {
            "X-Timestamp": ts,
            "X-Nonce": nonce,
            "X-Signature": sig,
        }
        if body:
            headers["Content-Type"] = "application/json"
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key[:200]
        if accept:
            headers["Accept"] = accept

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if method.upper() == "GET":
                    r = await client.get(url, headers=headers)
                else:
                    r = await client.post(url, content=body, headers=headers)
        except httpx.HTTPError as e:
            last_err = str(e)[:500]
            if attempt < max_retries:
                await asyncio.sleep(0.4 * (attempt + 1))
                continue
            opened = breaker.record_failure()
            if opened:
                await _maybe_alert_circuit_open(settings)
            return False, None, last_err

        if r.status_code in (200, 202):
            breaker.record_success()
            return True, r, r.text[:500]

        last_err = f"HTTP {r.status_code}: {r.text[:500]}"
        if _counts_toward_circuit(r.status_code):
            if attempt < max_retries:
                await asyncio.sleep(0.5 * (attempt + 1))
                continue
            opened = breaker.record_failure()
            if opened:
                await _maybe_alert_circuit_open(settings)
            return False, None, last_err

        # 4xx (кроме 429) — не ретраим и не открываем circuit
        return False, None, last_err

    opened = breaker.record_failure()
    if opened:
        await _maybe_alert_circuit_open(settings)
    return False, None, last_err


async def get_public_health(settings: Settings) -> tuple[bool, str]:
    """GET /health без HMAC (liveness vpn-api)."""
    base = (settings.vpn_api_base_url or "").strip().rstrip("/")
    if not base:
        return False, "VPN_API_BASE_URL not set"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{base}/health")
        if r.status_code == 200:
            return True, r.text[:200]
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except httpx.HTTPError as e:
        return False, str(e)[:200]


async def get_public_ready(settings: Settings) -> tuple[bool, dict[str, str] | str, int]:
    """GET /ready — WireGuard-интерфейс на ноде. Код 0 = не вызывали (нет base URL)."""
    base = (settings.vpn_api_base_url or "").strip().rstrip("/")
    if not base:
        return False, "VPN_API_BASE_URL not set", 0
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            r = await client.get(f"{base}/ready")
        if r.status_code == 200:
            try:
                data = r.json()
                if isinstance(data, dict):
                    return True, data, r.status_code
            except Exception:
                pass
            return True, r.text[:200], r.status_code
        return False, f"HTTP {r.status_code}: {r.text[:200]}", r.status_code
    except httpx.HTTPError as e:
        return False, str(e)[:200], 0


async def post_provision(
    settings: Settings,
    *,
    telegram_user_id: int,
    order_id: int,
    paid_until: str,
    idempotency_key: str,
) -> tuple[bool, str]:
    path = "/internal/v1/provision"
    body_obj: dict[str, Any] = {
        "telegram_user_id": int(telegram_user_id),
        "order_id": int(order_id),
        "paid_until": str(paid_until),
    }
    body = json.dumps(body_obj, separators=(",", ":")).encode("utf-8")
    ok, _r, msg = await _request_vpn_api(
        settings,
        method="POST",
        path=path,
        body=body,
        timeout=25.0,
        idempotency_key=idempotency_key,
    )
    return ok, msg


async def post_extend(
    settings: Settings,
    *,
    telegram_user_id: int,
    order_id: int,
    paid_until: str,
    idempotency_key: str,
) -> tuple[bool, str]:
    path = "/internal/v1/extend"
    body_obj: dict[str, Any] = {
        "telegram_user_id": int(telegram_user_id),
        "order_id": int(order_id),
        "paid_until": str(paid_until),
    }
    body = json.dumps(body_obj, separators=(",", ":")).encode("utf-8")
    ok, _r, msg = await _request_vpn_api(
        settings,
        method="POST",
        path=path,
        body=body,
        timeout=25.0,
        idempotency_key=idempotency_key,
    )
    return ok, msg


async def post_revoke(
    settings: Settings,
    *,
    telegram_user_id: int,
    reason: str,
    idempotency_key: str,
) -> tuple[bool, str]:
    path = "/internal/v1/revoke"
    body_obj: dict[str, Any] = {
        "telegram_user_id": int(telegram_user_id),
        "reason": str(reason)[:256],
    }
    body = json.dumps(body_obj, separators=(",", ":")).encode("utf-8")
    ok, _r, msg = await _request_vpn_api(
        settings,
        method="POST",
        path=path,
        body=body,
        timeout=20.0,
        idempotency_key=idempotency_key,
    )
    return ok, msg


async def post_add_subscription_days(
    settings: Settings,
    *,
    telegram_user_id: int,
    order_id: int,
    days: int,
    reason: str,
    idempotency_key: str,
) -> tuple[bool, str]:
    path = "/internal/v1/add-subscription-days"
    body_obj: dict[str, Any] = {
        "telegram_user_id": int(telegram_user_id),
        "order_id": int(order_id),
        "days": int(days),
        "reason": str(reason)[:128],
    }
    body = json.dumps(body_obj, separators=(",", ":")).encode("utf-8")
    ok, _r, msg = await _request_vpn_api(
        settings,
        method="POST",
        path=path,
        body=body,
        timeout=20.0,
        idempotency_key=idempotency_key,
    )
    return ok, msg


async def post_wg_conf(
    settings: Settings,
    *,
    telegram_user_id: int,
) -> tuple[bool, str | None, str]:
    """
    POST /internal/v1/wg/conf — текст WireGuard .conf.
    Возвращает (ok, conf_text_or_none, error_message).
    """
    path = "/internal/v1/wg/conf"
    body_obj: dict[str, Any] = {"telegram_user_id": int(telegram_user_id)}
    body = json.dumps(body_obj, separators=(",", ":")).encode("utf-8")
    ok, resp, msg = await _request_vpn_api(
        settings,
        method="POST",
        path=path,
        body=body,
        timeout=20.0,
        accept="text/plain",
    )
    if not ok or resp is None:
        return False, None, msg
    text = (resp.text or "").strip()
    if not text or "[Interface]" not in text:
        return False, None, "invalid WireGuard config from API"
    return True, text, ""


async def post_location_select(
    settings: Settings,
    *,
    telegram_user_id: int,
    location_slug: str,
) -> tuple[bool, str]:
    path = "/internal/v1/locations/select"
    body_obj: dict[str, Any] = {
        "telegram_user_id": int(telegram_user_id),
        "location_slug": str(location_slug)[:48],
    }
    body = json.dumps(body_obj, separators=(",", ":")).encode("utf-8")
    ok, resp, msg = await _request_vpn_api(
        settings,
        method="POST",
        path=path,
        body=body,
        timeout=15.0,
    )
    if not ok or resp is None:
        return False, msg
    return True, resp.text[:500]


async def post_ovpn_conf(
    settings: Settings,
    *,
    telegram_user_id: int,
) -> tuple[bool, str | None, str]:
    path = "/internal/v1/ovpn/conf"
    body_obj: dict[str, Any] = {"telegram_user_id": int(telegram_user_id)}
    body = json.dumps(body_obj, separators=(",", ":")).encode("utf-8")
    ok, resp, msg = await _request_vpn_api(
        settings,
        method="POST",
        path=path,
        body=body,
        timeout=20.0,
        accept="*/*",
    )
    if not ok or resp is None:
        return False, None, msg
    text = (resp.text or "").strip()
    if not text or "client" not in text.lower():
        return False, None, "invalid OpenVPN profile from API"
    return True, text, ""


async def get_locations_catalog(
    settings: Settings,
) -> tuple[bool, list[str] | None, int | None, list[dict[str, str]] | None]:
    """GET /internal/v1/locations/catalog — HMAC + nonce, без тела."""
    creds = _base_secret(settings)
    if creds is None:
        return False, None, None, None
    path = "/internal/v1/locations/catalog"
    ok, resp, _msg = await _request_vpn_api(
        settings,
        method="GET",
        path=path,
        body=b"",
        timeout=12.0,
    )
    if not ok or resp is None or resp.status_code != 200:
        return False, None, None, None
    try:
        data = resp.json()
    except Exception:
        return False, None, None, None
    lines = data.get("lines")
    if not isinstance(lines, list) or not lines:
        return False, None, None, None
    out_lines = [str(x).strip() for x in lines if str(x).strip()]
    if not out_lines:
        return False, None, None, None
    pn = data.get("preview_n", 3)
    try:
        preview_n = int(pn)
    except (TypeError, ValueError):
        preview_n = 3
    items_raw = data.get("items")
    items: list[dict[str, str]] | None = None
    if isinstance(items_raw, list):
        items = []
        for x in items_raw:
            if isinstance(x, dict) and x.get("slug") and x.get("label"):
                items.append(
                    {
                        "slug": str(x["slug"])[:48],
                        "label": str(x["label"])[:120],
                    }
                )
    return True, out_lines, preview_n, items
