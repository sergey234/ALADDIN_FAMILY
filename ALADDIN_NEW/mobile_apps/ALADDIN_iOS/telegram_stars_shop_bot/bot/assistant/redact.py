"""Маскирование секретов в логах и контексте LLM (R4, R14)."""

from __future__ import annotations

import re

_SUB_RE = re.compile(r"(https?://[^\s<>\"']+/sub/)([A-Za-z0-9_\-]{6,})", re.I)
_SUB_PATH_RE = re.compile(r"(/sub/)([A-Za-z0-9_\-]{6,})", re.I)
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")
_PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d\-\s()]{8,}\d)")
_CARD_RE = re.compile(r"(?<!\d)(?:\d[ \-]*){13,19}(?!\d)")


def mask_sub_urls(text: str) -> str:
    if not text:
        return ""
    out = _SUB_RE.sub(r"\1•••", text)
    return _SUB_PATH_RE.sub(r"\1•••", out)


def redact_for_log(text: str, *, max_len: int = 4000) -> str:
    t = mask_sub_urls(text or "")
    t = _EMAIL_RE.sub("[email]", t)
    t = _CARD_RE.sub("[card]", t)
    t = _PHONE_RE.sub("[phone]", t)
    if len(t) > max_len:
        return t[: max_len - 1] + "…"
    return t


def redact_for_llm(text: str, *, max_len: int = 3500) -> str:
    return redact_for_log(text, max_len=max_len)
