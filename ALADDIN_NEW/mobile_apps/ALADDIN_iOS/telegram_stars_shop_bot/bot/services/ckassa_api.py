from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
from typing import Any

import httpx

from bot.config import Settings

_log = logging.getLogger(__name__)

# Эндпоинты как в официальном WooCommerce-модуле Ckassa (includes/class-wc-ckassa-gateway.php).
CKASSA_DO_PAY_PROD = "https://api2.ckassa.ru/api-shop/rs/wordpress/do-pay/anonymous"
CKASSA_DO_PAY_DEMO = "https://demo-api2.ckassa.ru/api-shop/rs/wordpress/do-pay/anonymous"

# Демо shop/secret с тем же плагином; используются ТОЛЬКО если CKASSA_TEST_MODE=true (не для прода, не для реальных ₽).
CKASSA_DEMO_SHOP = "183bdddf-6a50-4942-bc93-a0c4f06af759"
CKASSA_DEMO_SECRET = "6746a6d9-41d2-448d-9c64-8f38d98af368"


def ckassa_hmac_signature_b64(secret: str, shop: str, components: list[Any]) -> str:
    """
    Совпадает с WC_Gateway_Ckassa::create_signature:
    data = [shop] + components + [secret]; str = join(|); hex = HMAC-SHA256(str, key=secret); return base64(upper(hex)).
    """
    parts: list[str] = [str(shop)] + [str(x) for x in components] + [str(secret)]
    s = "|".join(parts)
    hex_digest = hmac.new(secret.encode("utf-8"), s.encode("utf-8"), hashlib.sha256).hexdigest().upper()
    return base64.b64encode(hex_digest.encode("ascii")).decode("ascii")


def ckassa_request_signature(secret: str, shop: str, *, order_id: int, amount_kopecks: int) -> str:
    """Подпись тела do-pay/anonymous: shop | orderId | amount | secret."""
    return ckassa_hmac_signature_b64(secret, shop, [int(order_id), int(amount_kopecks)])


def ckassa_callback_signature(
    secret: str, shop: str, *, order_id: int, reg_pay_num: str, amount_kopecks: int, result: str
) -> str:
    """Подпись callback: shop | orderId | regPayNum | amount | result | secret."""
    return ckassa_hmac_signature_b64(secret, shop, [int(order_id), str(reg_pay_num), int(amount_kopecks), str(result)])


def rub_to_kopecks(rub: float) -> int:
    return int(round(float(rub) * 100.0))


def ckassa_checkout_configured(settings: Settings) -> bool:
    if not bool(getattr(settings, "ckassa_enabled", False)):
        return False
    if bool(getattr(settings, "ckassa_test_mode", False)):
        return True
    shop = (getattr(settings, "ckassa_shop_token", "") or "").strip()
    sec = (getattr(settings, "ckassa_secret_key", "") or "").strip()
    cb = (getattr(settings, "ckassa_callback_public_url", "") or "").strip()
    # Без cbUrl Ckassa не пришлёт callback - заказ не перейдёт в paid автоматически.
    return bool(shop and sec and cb)


def _ckassa_shop_secret(settings: Settings) -> tuple[str, str]:
    if bool(getattr(settings, "ckassa_test_mode", False)):
        return CKASSA_DEMO_SHOP, CKASSA_DEMO_SECRET
    return (settings.ckassa_shop_token or "").strip(), (settings.ckassa_secret_key or "").strip()


def _do_pay_url(settings: Settings) -> str:
    raw = (getattr(settings, "ckassa_do_pay_url", "") or "").strip()
    if raw:
        return raw.rstrip("/")
    if bool(getattr(settings, "ckassa_test_mode", False)):
        return CKASSA_DO_PAY_DEMO
    return CKASSA_DO_PAY_PROD


def _receipt_b64(settings: Settings, *, product_title: str, rub_due: float) -> str | None:
    """Чек для РФ (как в плагине WooCommerce): base64(JSON)."""
    if (getattr(settings, "ckassa_country", "") or "RU").strip().upper() != "RU":
        return None
    tax = (settings.ckassa_receipt_tax or "none").strip()
    pm = (settings.ckassa_receipt_payment_method or "full_prepayment").strip()
    po = (settings.ckassa_receipt_payment_object or "service").strip()
    taxation = (settings.ckassa_receipt_taxation or "usn_income").strip()
    price = f"{float(rub_due):.2f}"
    item_name = (product_title or "Оплата заказа").strip()[:512] or "Оплата заказа"
    payload = {
        "items": [
            {
                "num": 0,
                "name": item_name,
                "quantity": 1,
                "price": price,
                "sum": price,
                "tax": tax,
                "payment_method": pm,
                "payment_object": po,
            }
        ],
        "taxation": taxation,
    }
    raw = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(raw).decode("ascii")


async def create_ckassa_payment_meta(
    settings: Settings,
    *,
    order_id: int,
    rub_due: float,
    product_title: str,
    payer_email: str,
    payer_phone: str,
    payer_fio: str,
) -> tuple[str | None, str | None]:
    """
    Создаёт анонимный платёж в Ckassa, возвращает (payUrl, regPayNum_заглушка).
    regPayNum приходит только в callback; в метаданные заказа пишем ckassa:order:{id}.
    """
    if not ckassa_checkout_configured(settings):
        return None, None
    shop, secret = _ckassa_shop_secret(settings)
    amount_kopecks = rub_to_kopecks(rub_due)
    if amount_kopecks <= 0:
        return None, None

    url = _do_pay_url(settings)
    sig = ckassa_request_signature(secret, shop, order_id=int(order_id), amount_kopecks=amount_kopecks)

    body: dict[str, Any] = {
        "currency": "RUB",
        "language": (settings.ckassa_language or "RU").strip() or "RU",
        "country": (settings.ckassa_country or "RU").strip() or "RU",
        "orderId": int(order_id),
        "amount": amount_kopecks,
        "email": (payer_email or "").strip() or (settings.ckassa_default_email or "").strip(),
        "phone": (payer_phone or "").strip() or (settings.ckassa_default_phone or "").strip(),
        "fio": (payer_fio or "").strip() or (settings.ckassa_default_fio or "").strip(),
        "shop": shop,
        "signature": sig,
    }
    if bool(getattr(settings, "ckassa_test_mode", False)):
        body["invUnic"] = "NONE"

    cb = (settings.ckassa_callback_public_url or "").strip()
    if cb:
        body["cbUrl"] = cb
    su = (settings.ckassa_success_url or "").strip()
    if su:
        body["successUrl"] = su
    fu = (settings.ckassa_fail_url or "").strip()
    if fu:
        body["failUrl"] = fu

    receipt = _receipt_b64(settings, product_title=product_title, rub_due=float(rub_due))
    if receipt:
        body["Receipt"] = receipt

    timeout = max(5.0, float(getattr(settings, "ckassa_http_timeout_seconds", 15.0) or 15.0))
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, data=body)
    except Exception:
        _log.exception("ckassa_do_pay_http_error order_id=%s", order_id)
        return None, None
    if resp.status_code >= 400:
        _log.warning(
            "ckassa_do_pay_bad_status order_id=%s status=%s body=%s",
            order_id,
            resp.status_code,
            resp.text[:500],
        )
        return None, None
    try:
        data = resp.json()
    except Exception:
        _log.warning("ckassa_do_pay_invalid_json order_id=%s text=%s", order_id, resp.text[:300])
        return None, None
    pay_url = data.get("payUrl") if isinstance(data, dict) else None
    if not pay_url or not isinstance(pay_url, str):
        msg = data.get("message") if isinstance(data, dict) else None
        _log.warning("ckassa_do_pay_no_payUrl order_id=%s message=%s raw=%s", order_id, msg, str(data)[:400])
        return None, None
    ext = f"ckassa:order:{int(order_id)}"
    return pay_url.strip(), ext
