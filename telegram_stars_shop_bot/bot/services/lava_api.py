from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
from typing import Any

import httpx

from bot.config import Settings

_log = logging.getLogger(__name__)

DEFAULT_LAVA_API_BASE = "https://api.lava.ru/business/"


def lava_invoice_signing_payload(
    *,
    shop_id: str,
    order_id: str,
    sum_rub: float,
    expire_minutes: int,
    hook_url: str | None,
    success_url: str | None,
    fail_url: str | None,
    comment: str | None,
    include_service: list[str] | None,
) -> dict[str, Any]:
    """
    Тело для invoice/create. Порядок ключей сохраняется (важно для HMAC по правилам LAVA).
    См. https://dev.lava.ru/api-invoice-sign
    """
    payload: dict[str, Any] = {}
    if comment:
        payload["comment"] = comment
    payload["expire"] = int(expire_minutes)
    if fail_url:
        payload["failUrl"] = fail_url
    if hook_url:
        payload["hookUrl"] = hook_url
    if include_service:
        payload["includeService"] = include_service
    payload["orderId"] = str(order_id)
    payload["shopId"] = str(shop_id).strip()
    if success_url:
        payload["successUrl"] = success_url
    payload["sum"] = round(float(sum_rub), 2)
    return payload


def sign_lava_request_body(secret: str, payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).hexdigest()


def lava_checkout_configured(settings: Settings) -> bool:
    """True, если заданы все три параметра для создания счёта LAVA (invoice/create)."""
    shop = (settings.lava_shop_id or "").strip()
    secret = (settings.lava_secret_key or "").strip()
    hook = (settings.lava_hook_url or "").strip()
    return bool(shop and secret and hook)


def _lava_pick_qr_url(inner: dict[str, Any]) -> str | None:
    """QR СБП в ответе invoice/create (если LAVA отдаёт — зависит от тарифа/метода)."""
    for key in (
        "qr",
        "qrUrl",
        "qr_url",
        "qrCode",
        "qr_code",
        "sbpQr",
        "sbp_qr",
        "nspkQr",
        "nspk_qr",
        "paymentQr",
        "payment_qr",
    ):
        raw = inner.get(key)
        if isinstance(raw, str) and raw.strip().startswith(("http://", "https://")):
            return raw.strip()
    return None


def _lava_log_unknown_invoice_fields(inner: dict[str, Any], *, order_id: int, include_service: list[str] | None) -> None:
    known = {
        "url",
        "id",
        "invoice_id",
        "invoiceId",
        "amount",
        "sum",
        "status",
        "expire",
        "orderId",
        "shopId",
    }
    extra = sorted(k for k in inner if k not in known)
    if extra:
        _log.info(
            "lava_invoice_create_extra_fields order_id=%s include=%s keys=%s",
            order_id,
            include_service,
            extra,
        )


async def create_invoice_payment_url(
    settings: Settings,
    *,
    order_id: int,
    sum_rub: float,
    comment: str | None = None,
) -> str | None:
    url, _, _ = await create_invoice_payment_meta(
        settings,
        order_id=order_id,
        sum_rub=sum_rub,
        comment=comment,
    )
    return url


async def create_invoice_payment_meta(
    settings: Settings,
    *,
    order_id: int,
    sum_rub: float,
    comment: str | None = None,
    include_service: list[str] | None = None,
) -> tuple[str | None, str | None, str | None]:
    """
    Создаёт счёт в LAVA Business.
    Возвращает (url страницы оплаты, external_id, qr_url или None).
    https://api.lava.ru/business/invoice/create
    """
    if not lava_checkout_configured(settings):
        return None, None, None
    shop = (settings.lava_shop_id or "").strip()
    secret = (settings.lava_secret_key or "").strip()
    hook = (settings.lava_hook_url or "").strip()

    base = (settings.lava_api_base or DEFAULT_LAVA_API_BASE).rstrip("/") + "/"
    expire = max(1, min(int(settings.lava_invoice_expire_minutes), 43200))
    include = include_service if include_service else settings.lava_include_services_list()
    payload = lava_invoice_signing_payload(
        shop_id=shop,
        order_id=str(order_id),
        sum_rub=sum_rub,
        expire_minutes=expire,
        hook_url=hook,
        success_url=(settings.lava_success_url or "").strip() or None,
        fail_url=(settings.lava_fail_url or "").strip() or None,
        comment=comment,
        include_service=include or None,
    )
    signature = sign_lava_request_body(secret, payload)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Signature": signature,
    }
    url = f"{base}invoice/create"
    body_bytes = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.post(url, content=body_bytes, headers=headers)
        except Exception:
            _log.exception("lava_invoice_create_http_error order_id=%s attempt=%s", order_id, attempt)
            if attempt == 2:
                return None, None, None
            await asyncio.sleep(0.4 * (attempt + 1))
            continue
        if r.status_code == 200:
            try:
                data = r.json()
            except Exception:
                _log.warning("lava_invoice_create_invalid_json order_id=%s", order_id)
                return None, None, None
            inner = data.get("data") if isinstance(data, dict) else None
            if not isinstance(inner, dict):
                _log.warning("lava_invoice_create_no_data order_id=%s raw=%s", order_id, str(data)[:300])
                return None, None, None
            _lava_log_unknown_invoice_fields(inner, order_id=order_id, include_service=include)
            pay_url = inner.get("url")
            if not pay_url or not isinstance(pay_url, str):
                _log.warning("lava_invoice_create_no_url order_id=%s", order_id)
                return None, None, None
            ext = (
                inner.get("id")
                or inner.get("invoice_id")
                or inner.get("invoiceId")
                or data.get("id")
                if isinstance(data, dict)
                else None
            )
            ext_s = str(ext).strip() if ext is not None else None
            qr_url = _lava_pick_qr_url(inner)
            if qr_url and include_service == ["sbp"]:
                _log.info("lava_invoice_sbp_qr_url order_id=%s present=1", order_id)
            return pay_url, (ext_s or None), qr_url
        if r.status_code in (429, 502, 503, 504) or r.status_code >= 500:
            _log.warning(
                "lava_invoice_create_retryable status=%s order_id=%s attempt=%s",
                r.status_code,
                order_id,
                attempt,
            )
            if attempt < 2:
                await asyncio.sleep(0.5 * (attempt + 1))
                continue
        _log.warning("lava_invoice_create_bad_status %s body=%s", r.status_code, r.text[:500])
        return None, None, None
