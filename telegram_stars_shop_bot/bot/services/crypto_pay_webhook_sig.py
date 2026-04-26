"""Проверка подписи вебхука Crypto Pay (@CryptoBot) — как в pycryptopay-sdk (raw body)."""

from __future__ import annotations

import hashlib
import hmac


def verify_crypto_pay_webhook_signature(raw_body: bytes, signature_header: str | None, api_token: str) -> bool:
    """
    Заголовок: crypto-pay-api-signature (регистр не важен).
    Алгоритм: hex(HMAC-SHA256(SHA256(api_token utf-8), raw_body)).
    """
    sig = (signature_header or "").strip()
    token = (api_token or "").strip()
    if not sig or not token or not raw_body:
        return False
    secret = hashlib.sha256(token.encode("utf-8")).digest()
    expected = hmac.new(secret, raw_body, hashlib.sha256).hexdigest()
    try:
        return hmac.compare_digest(expected.lower(), sig.lower())
    except Exception:
        return False
