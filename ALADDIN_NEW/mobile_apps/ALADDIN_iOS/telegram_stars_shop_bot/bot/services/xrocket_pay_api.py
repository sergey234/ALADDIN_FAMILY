"""
xRocket Pay API - счета Telegram (/tg-invoices).

Документация: https://docs.xrocket.tg/api/pay/pay-api-overview
Base (prod): https://pay.xrocket.exchange - заголовок Rocket-Pay-Key (см. OpenAPI pay.xrocket.tg).

В магазине только USDT (Crypto Pay / xRocket); сумма счёта в USDT считается так же, как для Crypto Pay (₽ → USDT).
"""

from __future__ import annotations

import asyncio
import logging
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

import httpx

from bot.config import Settings
from bot.services.crypto_pay_api import resolve_rub_per_usdt
from bot.services.crypto_pay_payload import crypto_invoice_expires_in_seconds, encode_crypto_invoice_payload

_log = logging.getLogger(__name__)


def xrocket_invoice_api_ready(settings: Settings) -> bool:
    if not settings.xrocket_pay_enabled:
        return False
    return bool((settings.xrocket_pay_api_key or "").strip())


def _xrocket_base(settings: Settings) -> str:
    return (settings.xrocket_pay_api_base or "https://pay.xrocket.exchange").rstrip("/")


async def _xrocket_post_json(
    settings: Settings,
    path: str,
    body: dict[str, Any],
) -> dict[str, Any] | None:
    key = (settings.xrocket_pay_api_key or "").strip()
    if not key:
        return None
    url = f"{_xrocket_base(settings)}{path}"
    headers = {
        "Rocket-Pay-Key": key,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.post(url, json=body, headers=headers)
        except Exception:
            _log.exception("xrocket_http_error path=%s attempt=%s", path, attempt)
            if attempt == 2:
                return None
            await asyncio.sleep(0.4 * (attempt + 1))
            continue
        if r.status_code == 201:
            try:
                return r.json()
            except Exception:
                _log.warning("xrocket_invalid_json path=%s", path)
                return None
        if r.status_code in (429, 502, 503, 504) or r.status_code >= 500:
            _log.warning(
                "xrocket_retryable path=%s status=%s attempt=%s",
                path,
                r.status_code,
                attempt,
            )
            if attempt < 2:
                await asyncio.sleep(0.5 * (attempt + 1))
                continue
        _log.warning("xrocket_bad_status path=%s status=%s body=%s", path, r.status_code, r.text[:500])
        return None
    return None


async def create_xrocket_invoice_checkout_url(
    settings: Settings,
    *,
    order_id: int,
    due_rub: float,
    description: str | None = None,
) -> str | None:
    url, _ = await create_xrocket_invoice_checkout_meta(
        settings,
        order_id=order_id,
        due_rub=due_rub,
        description=description,
    )
    return url


async def create_xrocket_invoice_checkout_meta(
    settings: Settings,
    *,
    order_id: int,
    due_rub: float,
    description: str | None = None,
) -> tuple[str | None, str | None]:
    """POST /tg-invoices → ссылка на оплату в Telegram (поле data.link)."""
    if not xrocket_invoice_api_ready(settings):
        return None, None
    rub_per = await resolve_rub_per_usdt(settings)
    if rub_per is None or rub_per <= 0:
        _log.warning("xrocket_no_rub_per_usdt order_id=%s", order_id)
        return None, None
    due_dec = Decimal(str(round(float(due_rub), 2)))
    rpu = Decimal(str(rub_per))
    raw_amt = due_dec / rpu
    amt = float(raw_amt.quantize(Decimal("0.000000001"), rounding=ROUND_HALF_UP))
    if amt <= 0:
        return None, None
    desc = (description or f"Заказ #{order_id}").strip()
    if len(desc) > 1000:
        desc = desc[:997] + "..."
    exp = min(86400, int(crypto_invoice_expires_in_seconds(settings)))
    payload = encode_crypto_invoice_payload(order_id=order_id, due_rub=due_rub)
    body: dict[str, Any] = {
        "amount": amt,
        "numPayments": 1,
        "currency": "USDT",
        "description": desc,
        "payload": payload,
        "expiredIn": exp,
        "commentsEnabled": False,
    }
    paid = (settings.crypto_pay_paid_btn_url or "").strip()
    if paid.startswith("http://") or paid.startswith("https://"):
        body["callbackUrl"] = paid[:500]
    raw = await _xrocket_post_json(settings, "/tg-invoices", body)
    if not raw or raw.get("success") is not True:
        _log.warning("xrocket_create_invoice_not_success order_id=%s raw=%s", order_id, str(raw)[:400])
        return None, None
    data = raw.get("data")
    if not isinstance(data, dict):
        return None, None
    link = data.get("link")
    if isinstance(link, str) and link.startswith(("http://", "https://", "tg://")):
        ext = data.get("id")
        ext_s = str(ext).strip() if ext is not None else None
        return link, (ext_s or None)
    _log.warning("xrocket_create_invoice_no_link order_id=%s keys=%s", order_id, list(data.keys()))
    return None, None
