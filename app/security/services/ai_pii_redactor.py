# -*- coding: utf-8 -*-
"""
E2.2 — серверное маскирование PII (паритет с iOS AIPIIRedactor.swift).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Tuple

_MAX_INPUT_LEN = 16_000

# (compiled_pattern, placeholder)
_RULES: List[Tuple[re.Pattern[str], str]] = [
    (
        re.compile(
            r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}",
            re.IGNORECASE,
        ),
        "[REDACTED_JWT]",
    ),
    (
        re.compile(
            r"(?i)\b(?:bearer|api[_-]?key|client[_-]?secret|access[_-]?token)\s*[:=]\s*[A-Za-z0-9._\-]{8,}\b"
        ),
        "[REDACTED_SECRET]",
    ),
    (
        re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"),
        "[REDACTED_EMAIL]",
    ),
    (
        re.compile(
            r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b"
        ),
        "[REDACTED_CARD]",
    ),
    (
        re.compile(r"\b(?:\d{4}[\s\-]?){3}\d{4}\b"),
        "[REDACTED_CARD]",
    ),
    (
        re.compile(r"\b\d{3}-\d{3}-\d{3}[\s-]\d{2}\b"),
        "[REDACTED_SNILS]",
    ),
    (
        re.compile(r"\b\d{4}[\s-]\d{6}\b"),
        "[REDACTED_PASSPORT]",
    ),
    (
        re.compile(r"(?i)\b(?:инн|inn)\s*[:#]?\s*\d{10}(?:\d{2})?\b"),
        "[REDACTED_INN]",
    ),
    (
        re.compile(r"(?:\+7|8)[\s\-\(]?(?:\d[\s\-\(]?){10}"),
        "[REDACTED_PHONE]",
    ),
    (
        re.compile(r"\+\d{1,3}[\s\-\(]?(?:\d[\s\-\(]?){7,14}\d"),
        "[REDACTED_PHONE]",
    ),
    (
        re.compile(
            r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\b"
        ),
        "[REDACTED_IP]",
    ),
    (
        re.compile(r"(?i)\b(?:password|passwd|pwd|pin|cvv|secret)\s*[:=]\s*\S+"),
        "[REDACTED_PASSWORD]",
    ),
    (
        re.compile(r"\b[a-fA-F0-9]{32,}\b"),
        "[REDACTED_KEY]",
    ),
]

# High-confidence patterns — если остаются после redact, блокируем LLM-промпт.
_BLOCK_PATTERNS: List[re.Pattern[str]] = [
    re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}"),
    re.compile(
        r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}",
        re.IGNORECASE,
    ),
    re.compile(r"(?:\+7|8)[\s\-\(]?(?:\d[\s\-\(]?){10}"),
    re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14})\b"),
]


@dataclass(frozen=True)
class RedactResult:
    text: str
    replacement_count: int


def redact(text: str) -> RedactResult:
    """Маскирует известные классы PII. Порядок правил важен."""
    if not text:
        return RedactResult(text="", replacement_count=0)

    capped = text[:_MAX_INPUT_LEN]
    result = capped
    count = 0

    for pattern, placeholder in _RULES:
        matches = list(pattern.finditer(result))
        if not matches:
            continue
        count += len(matches)
        # replace from end to keep offsets valid
        for match in reversed(matches):
            start, end = match.span()
            result = result[:start] + placeholder + result[end:]

    return RedactResult(text=result, replacement_count=count)


def contains_blocked_pii(text: str) -> bool:
    """True если в тексте ещё есть high-confidence PII (email, JWT, phone, card)."""
    if not text:
        return False
    return any(p.search(text) for p in _BLOCK_PATTERNS)


def redact_dict_fields(data: dict, fields: Iterable[str]) -> Tuple[dict, int]:
    """Redact selected string fields in-place copy; returns (copy, total_replacements)."""
    out = dict(data)
    total = 0
    for key in fields:
        value = out.get(key)
        if isinstance(value, str) and value.strip():
            rr = redact(value)
            out[key] = rr.text
            total += rr.replacement_count
    return out, total
