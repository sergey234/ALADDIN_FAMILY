from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Any

import httpx

from bot.config import Settings

_log = logging.getLogger(__name__)

DEFAULT_CARDLINK_API_BASE = "https://cardlink.link"


def cardlink_payment_signature(api_token: str, out_sum: str, inv_id: str) -> str:
    """Postback / redirect: md5(OutSum:InvId:apiToken) uppercase hex."""
    raw = f"{out_sum}:{inv_id}:{api_token}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest().upper()


def verify_cardlink_payment_signature(
    api_token: str, *, out_sum: str, inv_id: str, signature_value: str
) -> bool:
    expected = cardlink_payment_signature(api_token, out_sum, inv_id)
    got = (signature_value or "").strip().upper()
    if not got:
        return False
    return hmac.compare_digest(expected, got)


def cardlink_refund_signature(
    api_token: str, *, amount: str, currency: str, bill_id: str, payment_id: str, refund_id: str
) -> str:
    raw = f"{amount}:{currency}:{bill_id}:{payment_id}:{refund_id}:{api_token}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest().upper()


def verify_cardlink_refund_signature(
    api_token: str,
    *,
    amount: str,
    currency: str,
    bill_id: str,
    payment_id: str,
    refund_id: str,
    signature_value: str,
) -> bool:
    expected = cardlink_refund_signature(
        api_token,
        amount=amount,
        currency=currency,
        bill_id=bill_id,
        payment_id=payment_id,
        refund_id=refund_id,
    )
    got = (signature_value or "").strip().upper()
    if not got:
        return False
    return hmac.compare_digest(expected, got)


def cardlink_chargeback_signature(
    api_token: str, *, bill_id: str, payment_id: str, chargeback_id: str
) -> str:
    raw = f"{bill_id}:{payment_id}:{chargeback_id}:{api_token}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest().upper()


def verify_cardlink_chargeback_signature(
    api_token: str,
    *,
    bill_id: str,
    payment_id: str,
    chargeback_id: str,
    signature_value: str,
) -> bool:
    expected = cardlink_chargeback_signature(
        api_token, bill_id=bill_id, payment_id=payment_id, chargeback_id=chargeback_id
    )
    got = (signature_value or "").strip().upper()
    if not got:
        return False
    return hmac.compare_digest(expected, got)


def cardlink_checkout_configured(settings: Settings) -> bool:
    if not bool(getattr(settings, "cardlink_enabled", False)):
        return False
    shop = (settings.cardlink_shop_id or "").strip()
    token = (settings.cardlink_api_token or "").strip()
    return bool(shop and token)


def _api_origin(settings: Settings) -> str:
    raw = (settings.cardlink_api_base or DEFAULT_CARDLINK_API_BASE).strip().rstrip("/")
    if raw.startswith("http://") or raw.startswith("https://"):
        return raw
    return f"https://{raw}"


def parse_cardlink_order_id(inv_id: str) -> int | None:
    s = (inv_id or "").strip()
    if not s:
        return None
    if s.upper().startswith("ORDER"):
        s = s[5:].strip()
    try:
        oid = int(s)
    except ValueError:
        return None
    return oid if oid > 0 else None


async def create_cardlink_bill_meta(
    settings: Settings,
    *,
    order_id: int,
    sum_rub: float,
    description: str | None = None,
    telegram_user_id: int | None = None,
    telegram_username: str | None = None,
) -> tuple[str | None, str | None]:
    """
    Создаёт счёт Cardlink (POST /api/v1/bill/create).
    Возвращает (link_page_url, bill_id).
    https://cardlink.link/reference/api
    """
    if not cardlink_checkout_configured(settings):
        return None, None

    shop = (settings.cardlink_shop_id or "").strip()
    token = (settings.cardlink_api_token or "").strip()
    amount = f"{float(sum_rub):.2f}"
    oid_s = str(int(order_id))
    desc = (description or f"Заказ #{order_id}").strip()[:500]

    data: dict[str, Any] = {
        "amount": amount,
        "shop_id": shop,
        "order_id": oid_s,
        "description": desc,
        "type": "normal",
        "currency_in": (settings.cardlink_currency_in or "RUB").strip().upper() or "RUB",
        "locale": (settings.cardlink_locale or "ru").strip().lower() or "ru",
        "name": (settings.cardlink_payment_name or "AIMonkey Stars | Premium").strip()[:200],
        "payer_pays_commission": str(int(settings.cardlink_payer_pays_commission)),
        "custom": oid_s,
    }
    ttl = int(getattr(settings, "cardlink_bill_ttl_seconds", 0) or 0)
    if ttl > 0:
        data["ttl"] = str(ttl)
    success = (settings.cardlink_success_url or "").strip()
    fail = (settings.cardlink_fail_url or "").strip()
    if success:
        data["success_url"] = success
    if fail:
        data["fail_url"] = fail
    pm = (settings.cardlink_payment_method or "").strip().upper()
    if pm in ("BANK_CARD", "SBP"):
        data["payment_method"] = pm

    if telegram_user_id is not None and telegram_user_id > 0:
        data["payer_data[email]"] = f"tg{telegram_user_id}@telegram.invalid"

    url = f"{_api_origin(settings)}/api/v1/bill/create"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            r = await client.post(url, data=data, headers=headers)
    except Exception:
        _log.exception("cardlink_bill_create_http_error order_id=%s", order_id)
        return None, None

    if r.status_code != 200:
        _log.warning(
            "cardlink_bill_create_bad_status order_id=%s status=%s body=%s",
            order_id,
            r.status_code,
            r.text[:500],
        )
        return None, None

    try:
        payload = r.json()
    except Exception:
        _log.warning("cardlink_bill_create_invalid_json order_id=%s", order_id)
        return None, None

    if not isinstance(payload, dict):
        return None, None
    success_flag = str(payload.get("success", "")).lower()
    if success_flag not in ("true", "1"):
        _log.warning("cardlink_bill_create_not_success order_id=%s raw=%s", order_id, str(payload)[:300])
        return None, None

    pay_url = payload.get("link_page_url") or payload.get("link_url")
    if not isinstance(pay_url, str) or not pay_url.strip().startswith("http"):
        _log.warning("cardlink_bill_create_no_url order_id=%s", order_id)
        return None, None

    bill_id = payload.get("bill_id")
    ext = str(bill_id).strip() if bill_id is not None else None
    return pay_url.strip(), (ext or None)
