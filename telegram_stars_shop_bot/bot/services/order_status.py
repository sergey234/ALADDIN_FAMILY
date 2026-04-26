"""
Допустимые переходы статусов заказа (orders.status).

Инвариант: completed только из paid или processing (не из pending_payment).
Терминальные completed / expired / refunded; payment_disputed — только через paid или refunded.
"""

from __future__ import annotations

# Статусы, которые встречаются в прод-коде сегодня
KNOWN_STATUSES = frozenset(
    {
        "pending_payment",
        "paid",
        "processing",
        "completed",
        "expired",
        "refunded",
        "payment_disputed",
    }
)


def can_transition(from_status: str, to_status: str) -> bool:
    """True если переход разрешён; одинаковый статус — no-op, кроме терминального `completed`."""
    old = (from_status or "").strip()
    new = (to_status or "").strip()
    if old == new:
        if old in ("completed", "expired", "refunded", "payment_disputed"):
            return False
        return True
    if new not in KNOWN_STATUSES or old not in KNOWN_STATUSES:
        return False
    if old == "completed":
        return False
    if old == "expired":
        return new == "refunded"
    if old == "refunded":
        return False
    if old == "payment_disputed" and new in ("paid", "refunded"):
        return True
    if old == "pending_payment" and new == "paid":
        return True
    if old == "pending_payment" and new == "expired":
        return True
    if old == "pending_payment" and new == "refunded":
        return True
    if old == "paid" and new in ("processing", "completed", "refunded", "payment_disputed"):
        return True
    # Откат после сбоя create у iStar (воркер) или коррекция супер-админом; без авто-refund.
    if old == "processing" and new == "paid":
        return True
    if old == "processing" and new == "completed":
        return True
    if old == "processing" and new in ("refunded", "payment_disputed"):
        return True
    return False


def require_transition(from_status: str, to_status: str) -> None:
    if not can_transition(from_status, to_status):
        raise ValueError(f"invalid_order_transition:{from_status!r}->{to_status!r}")
