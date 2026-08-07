"""Web nickname + access code (no email/password)."""

from __future__ import annotations

import hashlib
import re
import secrets
from typing import Optional

# Latin letter start; then letters/digits/underscore. 3–24 chars total.
_NICK_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{2,23}$")
_EMAILISH = re.compile(r".+@.+\..+")
_PHONEISH = re.compile(r"^\+?[0-9]{7,}$")


def normalize_nickname(raw: str) -> str:
    return (raw or "").strip()


def validate_nickname(raw: str) -> Optional[str]:
    """Return error code or None if ok."""
    nick = normalize_nickname(raw)
    if len(nick) < 3:
        return "too_short"
    if len(nick) > 24:
        return "too_long"
    if _EMAILISH.match(nick) or "@" in nick:
        return "looks_like_email"
    if _PHONEISH.match(nick) or (nick.isdigit() and len(nick) >= 7):
        return "looks_like_phone"
    if not _NICK_RE.match(nick):
        return "bad_chars"
    return None


def new_access_code() -> str:
    # Shown once; AIM- prefix for support recognition.
    return "AIM-" + secrets.token_urlsafe(9).replace("-", "").replace("_", "")[:12].upper()


def hash_access_code(raw: str) -> str:
    return hashlib.sha256((raw or "").strip().encode("utf-8")).hexdigest()


def access_code_matches(raw: str, stored_hash: str | None) -> bool:
    if not stored_hash:
        return False
    return hash_access_code(raw) == str(stored_hash)
