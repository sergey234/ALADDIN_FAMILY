"""Проверка подписи вебхука xRocket Pay — как в xrocket-pay-api-sdk (webhook-utils)."""

from __future__ import annotations

import hashlib
import hmac


def verify_xrocket_webhook_signature(body_str: str, signature_header: str | None, api_key: str) -> bool:
    """
    Заголовок: rocket-pay-signature.
    Алгоритм: hex(HMAC-SHA256(SHA256(api_key utf-8), body utf-8 bytes)).
    Тело — та же строка, что пришла в HTTP (как JSON.stringify после express.json).
    """
    sig = (signature_header or "").strip()
    key = (api_key or "").strip()
    if not sig or not key:
        return False
    secret = hashlib.sha256(key.encode("utf-8")).digest()
    try:
        raw = body_str.encode("utf-8")
    except Exception:
        return False
    expected = hmac.new(secret, raw, hashlib.sha256).hexdigest()
    try:
        return hmac.compare_digest(expected, sig)
    except Exception:
        return False
