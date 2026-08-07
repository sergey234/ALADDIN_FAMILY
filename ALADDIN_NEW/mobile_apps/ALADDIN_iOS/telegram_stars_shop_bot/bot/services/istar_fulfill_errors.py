"""Классификация ошибок iStar для автовыдачи (попытки vs retry)."""

from __future__ import annotations

import re

from bot.services.istar_fulfill_client import IstarFulfillError

# Пауза перед повтором при временных сбоях (минуты).
TRANSIENT_BACKOFF_MINUTES: tuple[int, ...] = (2, 5, 15, 30)


def backoff_minutes_for_transient_count(transient_count: int) -> int:
    """transient_count после инкремента (1 → 2 мин, 2 → 5 мин, …)."""
    n = max(1, int(transient_count))
    idx = min(n - 1, len(TRANSIENT_BACKOFF_MINUTES) - 1)
    return TRANSIENT_BACKOFF_MINUTES[idx]


def istar_error_is_server_http(exc: BaseException) -> bool:
    """5xx от iStar — внешний сбой API, не ошибка получателя."""
    if isinstance(exc, IstarFulfillError):
        sc = exc.status_code
        if sc is not None and sc >= 500:
            return True
    return bool(re.search(r"istar_http_5\d\d", str(exc)))


def istar_error_is_transient(exc: BaseException) -> bool:
    """
    Временная ошибка: не тратим fulfillment_attempt_count, ставим retry_after.
    """
    if istar_error_is_server_http(exc):
        return True
    msg = str(exc)
    if msg.startswith("istar_http_error:"):
        return True
    if isinstance(exc, IstarFulfillError):
        sc = exc.status_code
        if sc in (408, 429):
            return True
    if re.search(r"\b(low_ton|batch_skipped_low_ton)\b", msg, re.I):
        return True
    return False


def istar_error_counts_as_fulfill_attempt(exc: BaseException) -> bool:
    """
    Постоянная ошибка получателя/товара — увеличиваем счётчик попыток.
    """
    if istar_error_is_transient(exc):
        return False
    if isinstance(exc, IstarFulfillError):
        sc = exc.status_code
        if sc is not None and 400 <= sc < 500:
            return True
    msg = str(exc)
    if "missing_recipient" in msg or msg.startswith("internal_"):
        return True
    if "istar_star_search_failed" in msg or "istar_premium_search_failed" in msg:
        return True
    if "istar_star_search_no_recipient" in msg or "istar_premium_search_no_recipient" in msg:
        return True
    if "unsupported_product_kind" in msg:
        return True
    return True
