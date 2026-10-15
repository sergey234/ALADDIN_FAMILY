"""fws-01: PBKDF2 hashing for family safe-word (never store plaintext)."""
from __future__ import annotations

import hashlib
import re
import secrets
from typing import Optional, Tuple

_ITERATIONS = 100_000
_SALT_BYTES = 16
_HASH_BYTES = 32


def normalize_phrase(phrase: str) -> str:
    """Collapse whitespace; case-insensitive compare."""
    collapsed = re.sub(r"\s+", " ", (phrase or "").strip().lower())
    return collapsed


def validate_phrase(phrase: str) -> Optional[str]:
    """Return error code or None when valid."""
    normalized = normalize_phrase(phrase)
    if len(normalized) < 4:
        return "phrase_too_short"
    if len(normalized) > 120:
        return "phrase_too_long"
    # Product: one word is OK (min 4 chars). Multi-word phrases still allowed.
    return None


def hash_phrase(phrase: str, salt_hex: Optional[str] = None) -> Tuple[str, str]:
    """Return (salt_hex, hash_hex) for normalized phrase."""
    normalized = normalize_phrase(phrase)
    if salt_hex:
        salt = bytes.fromhex(salt_hex)
    else:
        salt = secrets.token_bytes(_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        normalized.encode("utf-8"),
        salt,
        _ITERATIONS,
        dklen=_HASH_BYTES,
    )
    return salt.hex(), digest.hex()


def verify_phrase(phrase: str, salt_hex: str, hash_hex: str) -> bool:
    if not salt_hex or not hash_hex:
        return False
    try:
        _, candidate = hash_phrase(phrase, salt_hex=salt_hex)
    except ValueError:
        return False
    return secrets.compare_digest(candidate, hash_hex.lower())
