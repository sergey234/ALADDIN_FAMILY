from __future__ import annotations

import hashlib
import hmac


def hmac_sha256_hex(secret: str, message: bytes) -> str:
    return hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()


def verify_hmac_sha256_hex(secret: str, message: bytes, signature_hex: str) -> bool:
    try:
        expected = hmac_sha256_hex(secret, message)
        return hmac.compare_digest(expected, signature_hex.strip().lower())
    except Exception:
        return False
