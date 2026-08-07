from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import httpx

from bot.config import Settings

_log = logging.getLogger(__name__)

DEFAULT_LAVA_API_BASE = "https://api.lava.ru/business/"
DEFAULT_LAVA_PAY_BASE = "https://pay.lava.ru"
_LAVA_REISSUE_SUFFIX = re.compile(r"^(\d+)-r\d+$")
_MAX_LAVA_REISSUE_ATTEMPTS = 8


@dataclass(frozen=True)
class LavaInvoiceResult:
    pay_url: str | None
    external_id: str | None
    qr_url: str | None
    lava_attempt: int = 1
    error: str | None = None


def parse_lava_shop_order_id(raw: object) -> int | None:
    """order_id из LAVA webhook: «59» или «59-r2» → 59."""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    m = _LAVA_REISSUE_SUFFIX.match(s)
    if m:
        return int(m.group(1))
    try:
        return int(s)
    except ValueError:
        return None


def lava_provider_order_id(shop_order_id: int, attempt: int) -> str:
    """Уникальный orderId для LAVA (повтор после expired: 59-r2, 59-r3, …)."""
    att = max(1, int(attempt))
    if att <= 1:
        return str(int(shop_order_id))
    return f"{int(shop_order_id)}-r{att}"


def normalize_lava_pay_url(url: str | None, *, lang: str = "ru") -> str | None:
    if not url or not isinstance(url, str):
        return None
    u = url.strip()
    if not u.startswith(("http://", "https://")):
        return None
    parsed = urlparse(u)
    q = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if q.get("lang") != lang:
        q["lang"] = lang
    return urlunparse(parsed._replace(query=urlencode(q)))


def lava_invoice_pay_url_from_id(invoice_id: str, *, pay_base: str | None = None) -> str | None:
    """Собрать URL страницы оплаты по invoice id (status API url не отдаёт)."""
    inv = (invoice_id or "").strip()
    if not inv:
        return None
    base = (pay_base or DEFAULT_LAVA_PAY_BASE).rstrip("/")
    return normalize_lava_pay_url(f"{base}/invoice/{inv}")


def lava_invoice_user_message(error: str | None) -> str:
    return {
        "lava_misconfigured": "Оплата LAVA не настроена. Напишите в поддержку.",
        "lava_invoice_expired_reissued": (
            "Предыдущий счёт истёк — открыт новый. Нажмите кнопку оплаты ещё раз."
        ),
        "lava_invoice_unavailable": (
            "Счёт LAVA недоступен. Создайте новый заказ или напишите в поддержку с номером заказа."
        ),
    }.get(error or "", "Не удалось открыть оплату. Попробуйте позже или создайте новый заказ.")


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
    res = await create_invoice_payment_meta(
        settings,
        order_id=order_id,
        sum_rub=sum_rub,
        comment=comment,
    )
    return res.pay_url


async def create_invoice_payment_meta(
    settings: Settings,
    *,
    order_id: int,
    sum_rub: float,
    comment: str | None = None,
    include_service: list[str] | None = None,
    existing_invoice_id: str | None = None,
    stored_pay_url: str | None = None,
    lava_attempt: int = 1,
    success_url: str | None = None,
    fail_url: str | None = None,
) -> LavaInvoiceResult:
    """
    Создаёт или переиспользует счёт LAVA Business.
    При expired счёте — новый orderId {id}-r2 (LAVA не отдаёт orderId повторно).

    success_url/fail_url: если заданы — перекрывают LAVA_SUCCESS_URL / LAVA_FAIL_URL
    (web-checkout передаёт get…/o/{token}).
    """
    if not lava_checkout_configured(settings):
        return LavaInvoiceResult(None, None, None, error="lava_misconfigured")

    ext_in = (existing_invoice_id or "").strip() or None
    attempt = max(1, int(lava_attempt or 1))
    stored = normalize_lava_pay_url(stored_pay_url)
    ok_url = (success_url if success_url is not None else (settings.lava_success_url or "")).strip() or None
    bad_url = (fail_url if fail_url is not None else (settings.lava_fail_url or "")).strip() or None

    reused = await _try_reuse_open_lava_invoice(
        settings,
        order_id=order_id,
        invoice_id=ext_in,
        stored_pay_url=stored,
    )
    if reused is not None:
        return LavaInvoiceResult(
            reused[0], reused[1], reused[2], lava_attempt=attempt, error=None
        )

    if ext_in:
        closed = await _lava_invoice_is_closed(settings, order_id=order_id, invoice_id=ext_in)
        if closed:
            attempt = min(attempt + 1, _MAX_LAVA_REISSUE_ATTEMPTS)
            ext_in = None
            _log.info("lava_invoice_reissue order_id=%s attempt=%s reason=closed", order_id, attempt)

    return await _create_lava_invoice_once(
        settings,
        shop_order_id=order_id,
        sum_rub=sum_rub,
        comment=comment,
        include_service=include_service,
        lava_attempt=attempt,
        existing_invoice_id=ext_in,
        success_url=ok_url,
        fail_url=bad_url,
    )


async def create_topup_invoice_payment_meta(
    settings: Settings,
    *,
    topup_id: int,
    sum_rub: float,
    existing_invoice_id: str | None = None,
    stored_pay_url: str | None = None,
    lava_attempt: int = 1,
) -> LavaInvoiceResult:
    """Счёт LAVA для пополнения баланса (orderId = TOPUP{id})."""
    from bot.services.payment_reference import lava_topup_provider_order_id

    if not lava_checkout_configured(settings):
        return LavaInvoiceResult(None, None, None, error="lava_misconfigured")

    ext_in = (existing_invoice_id or "").strip() or None
    attempt = max(1, int(lava_attempt or 1))
    stored = normalize_lava_pay_url(stored_pay_url)
    lava_oid = lava_topup_provider_order_id(topup_id, attempt)

    if ext_in and stored:
        data = await fetch_invoice_status(settings, invoice_id=ext_in)
        if data and str(data.get("status") or "").strip().lower() not in _CLOSED_LAVA_STATUSES:
            return LavaInvoiceResult(stored, ext_in, None, lava_attempt=attempt)

    if ext_in:
        closed = await _lava_invoice_is_closed(settings, order_id=None, invoice_id=ext_in)
        if closed:
            attempt = min(attempt + 1, _MAX_LAVA_REISSUE_ATTEMPTS)
            ext_in = None
            lava_oid = lava_topup_provider_order_id(topup_id, attempt)

    return await _create_lava_invoice_once(
        settings,
        shop_order_id=topup_id,
        sum_rub=sum_rub,
        comment=f"TOPUP{topup_id}",
        include_service=settings.lava_include_services_list(),
        lava_attempt=attempt,
        existing_invoice_id=ext_in,
        lava_order_id=lava_oid,
    )


async def _lava_invoice_is_closed(
    settings: Settings,
    *,
    order_id: int | None,
    invoice_id: str,
) -> bool:
    data = await fetch_invoice_status(settings, order_id=order_id, invoice_id=invoice_id)
    if not data:
        return False
    st = str(data.get("status") or "").strip().lower()
    return st in _PAID_LAVA_STATUSES or st in _CLOSED_LAVA_STATUSES


async def _create_lava_invoice_once(
    settings: Settings,
    *,
    shop_order_id: int,
    sum_rub: float,
    comment: str | None,
    include_service: list[str] | None,
    lava_attempt: int,
    existing_invoice_id: str | None,
    lava_order_id: str | None = None,
    success_url: str | None = None,
    fail_url: str | None = None,
) -> LavaInvoiceResult:
    shop = (settings.lava_shop_id or "").strip()
    secret = (settings.lava_secret_key or "").strip()
    hook = (settings.lava_hook_url or "").strip()
    lava_oid = (lava_order_id or "").strip() or lava_provider_order_id(shop_order_id, lava_attempt)

    base = (settings.lava_api_base or DEFAULT_LAVA_API_BASE).rstrip("/") + "/"
    expire = max(1, min(int(settings.lava_invoice_expire_minutes), 43200))
    include = include_service if include_service else settings.lava_include_services_list()
    ok_url = (
        success_url
        if success_url is not None
        else ((settings.lava_success_url or "").strip() or None)
    )
    bad_url = (
        fail_url if fail_url is not None else ((settings.lava_fail_url or "").strip() or None)
    )
    payload = lava_invoice_signing_payload(
        shop_id=shop,
        order_id=lava_oid,
        sum_rub=sum_rub,
        expire_minutes=expire,
        hook_url=hook,
        success_url=ok_url,
        fail_url=bad_url,
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
    for post_attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                r = await client.post(url, content=body_bytes, headers=headers)
        except Exception:
            _log.exception(
                "lava_invoice_create_http_error order_id=%s lava_oid=%s attempt=%s",
                shop_order_id,
                lava_oid,
                post_attempt,
            )
            if post_attempt == 2:
                return LavaInvoiceResult(None, None, None, lava_attempt=lava_attempt, error="lava_invoice_unavailable")
            await asyncio.sleep(0.4 * (post_attempt + 1))
            continue
        if r.status_code == 200:
            return _parse_create_response(
                r, shop_order_id=shop_order_id, include=include, lava_attempt=lava_attempt
            )
        if r.status_code == 422:
            reused = await _try_reuse_open_lava_invoice(
                settings,
                order_id=shop_order_id,
                invoice_id=existing_invoice_id,
                stored_pay_url=None,
            )
            if reused is not None:
                return LavaInvoiceResult(
                    reused[0], reused[1], reused[2], lava_attempt=lava_attempt, error=None
                )
            if lava_attempt < _MAX_LAVA_REISSUE_ATTEMPTS:
                _log.info(
                    "lava_invoice_create_422_reissue order_id=%s lava_oid=%s next_attempt=%s",
                    shop_order_id,
                    lava_oid,
                    lava_attempt + 1,
                )
                return await _create_lava_invoice_once(
                    settings,
                    shop_order_id=shop_order_id,
                    sum_rub=sum_rub,
                    comment=comment,
                    include_service=include_service,
                    lava_attempt=lava_attempt + 1,
                    existing_invoice_id=None,
                    success_url=ok_url,
                    fail_url=bad_url,
                )
        if r.status_code in (429, 502, 503, 504) or r.status_code >= 500:
            _log.warning(
                "lava_invoice_create_retryable status=%s order_id=%s attempt=%s",
                r.status_code,
                shop_order_id,
                post_attempt,
            )
            if post_attempt < 2:
                await asyncio.sleep(0.5 * (post_attempt + 1))
                continue
        _log.warning("lava_invoice_create_bad_status %s body=%s", r.status_code, r.text[:500])
        return LavaInvoiceResult(None, None, None, lava_attempt=lava_attempt, error="lava_invoice_unavailable")
    return LavaInvoiceResult(None, None, None, lava_attempt=lava_attempt, error="lava_invoice_unavailable")


def _parse_create_response(
    r: httpx.Response,
    *,
    shop_order_id: int,
    include: list[str] | None,
    lava_attempt: int,
) -> LavaInvoiceResult:
    try:
        data = r.json()
    except Exception:
        _log.warning("lava_invoice_create_invalid_json order_id=%s", shop_order_id)
        return LavaInvoiceResult(None, None, None, lava_attempt=lava_attempt, error="lava_invoice_unavailable")
    inner = data.get("data") if isinstance(data, dict) else None
    if not isinstance(inner, dict):
        _log.warning("lava_invoice_create_no_data order_id=%s raw=%s", shop_order_id, str(data)[:300])
        return LavaInvoiceResult(None, None, None, lava_attempt=lava_attempt, error="lava_invoice_unavailable")
    _lava_log_unknown_invoice_fields(inner, order_id=shop_order_id, include_service=include)
    pay_url = normalize_lava_pay_url(inner.get("url") if isinstance(inner.get("url"), str) else None)
    if not pay_url:
        _log.warning("lava_invoice_create_no_url order_id=%s", shop_order_id)
        return LavaInvoiceResult(None, None, None, lava_attempt=lava_attempt, error="lava_invoice_unavailable")
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
    if qr_url and include == ["sbp"]:
        _log.info("lava_invoice_sbp_qr_url order_id=%s present=1", shop_order_id)
    reissued = lava_attempt > 1
    if reissued:
        _log.info("lava_invoice_created_reissue order_id=%s attempt=%s invoice_id=%s", shop_order_id, lava_attempt, ext_s)
    return LavaInvoiceResult(
        pay_url,
        ext_s,
        qr_url,
        lava_attempt=lava_attempt,
        error="lava_invoice_expired_reissued" if reissued else None,
    )


async def fetch_invoice_status(
    settings: Settings,
    *,
    order_id: int | None = None,
    invoice_id: str | None = None,
) -> dict[str, Any] | None:
    """
    POST invoice/status — статус счёта LAVA (fallback, если webhook не пришёл).
    https://dev.lava.ru/api-invoice-status
    """
    if not lava_checkout_configured(settings):
        return None
    shop = (settings.lava_shop_id or "").strip()
    secret = (settings.lava_secret_key or "").strip()
    oid = str(order_id).strip() if order_id is not None else ""
    inv = (invoice_id or "").strip()
    if not oid and not inv:
        return None
    payload: dict[str, Any] = {"shopId": shop}
    if inv:
        payload["invoiceId"] = inv
    elif oid:
        payload["orderId"] = oid
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    signature = sign_lava_request_body(secret, payload)
    base = (settings.lava_api_base or DEFAULT_LAVA_API_BASE).rstrip("/") + "/"
    url = f"{base}invoice/status"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Signature": signature,
        "User-Agent": "ALADDIN-Shop/1.0",
    }
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(url, content=raw, headers=headers)
    except Exception:
        _log.exception("lava_invoice_status_http_error order_id=%s invoice_id=%s", order_id, invoice_id)
        return None
    if r.status_code == 404:
        if inv:
            _log.warning(
                "lava_invoice_status_not_found order_id=%s invoice_id=%s",
                order_id,
                invoice_id,
            )
        else:
            _log.debug("lava_invoice_status_no_invoice_yet order_id=%s", order_id)
        return None
    if r.status_code != 200:
        _log.warning(
            "lava_invoice_status_bad_status status=%s order_id=%s body=%s",
            r.status_code,
            order_id,
            r.text[:300],
        )
        return None
    try:
        body = r.json()
    except Exception:
        _log.warning("lava_invoice_status_invalid_json order_id=%s", order_id)
        return None
    data = body.get("data") if isinstance(body, dict) else None
    return data if isinstance(data, dict) else None


_PAID_LAVA_STATUSES = frozenset({"success", "paid", "completed"})
_CLOSED_LAVA_STATUSES = frozenset({"expired", "cancelled", "canceled", "failed", "refunded"})


def _lava_invoice_id_from_data(data: dict[str, Any]) -> str | None:
    ext = data.get("id") or data.get("invoice_id") or data.get("invoiceId")
    ext_s = str(ext).strip() if ext is not None else None
    return ext_s or None


def _meta_from_lava_status_data(
    data: dict[str, Any],
    *,
    fallback_invoice_id: str | None = None,
    stored_pay_url: str | None = None,
    pay_base: str | None = None,
) -> tuple[str | None, str | None, str | None]:
    ext_s = _lava_invoice_id_from_data(data) or (fallback_invoice_id or "").strip() or None
    if stored_pay_url and ext_s and _lava_invoice_id_from_data(data) == ext_s:
        url = normalize_lava_pay_url(stored_pay_url)
        if url:
            return url, ext_s, _lava_pick_qr_url(data)
    pay_url = data.get("url")
    if isinstance(pay_url, str) and pay_url.strip():
        return normalize_lava_pay_url(pay_url.strip()), ext_s, _lava_pick_qr_url(data)
    if ext_s:
        built = lava_invoice_pay_url_from_id(ext_s, pay_base=pay_base)
        if built:
            return built, ext_s, _lava_pick_qr_url(data)
    return None, None, None


async def _try_reuse_open_lava_invoice(
    settings: Settings,
    *,
    order_id: int,
    invoice_id: str | None,
    stored_pay_url: str | None = None,
) -> tuple[str | None, str | None, str | None] | None:
    """Вернуть URL существующего неоплаченного счёта LAVA."""
    if not invoice_id:
        return None
    data = await fetch_invoice_status(settings, order_id=order_id, invoice_id=invoice_id)
    if not data:
        return None
    st = str(data.get("status") or "").strip().lower()
    if st in _PAID_LAVA_STATUSES or st in _CLOSED_LAVA_STATUSES:
        return None
    pay_base = DEFAULT_LAVA_PAY_BASE
    meta = _meta_from_lava_status_data(
        data,
        fallback_invoice_id=invoice_id,
        stored_pay_url=stored_pay_url,
        pay_base=pay_base,
    )
    if meta[0]:
        _log.info("lava_invoice_reuse order_id=%s invoice_id=%s status=%s", order_id, invoice_id or meta[1], st)
        return meta
    return None
