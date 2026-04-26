from __future__ import annotations

import pytest

from bot.services.order_status import can_transition, require_transition


@pytest.mark.parametrize(
    ("old", "new", "ok"),
    [
        ("pending_payment", "paid", True),
        ("pending_payment", "processing", False),
        ("pending_payment", "completed", False),
        ("pending_payment", "expired", True),
        ("pending_payment", "refunded", True),
        ("pending_payment", "payment_disputed", False),
        ("expired", "paid", False),
        ("expired", "pending_payment", False),
        ("expired", "refunded", True),
        ("paid", "processing", True),
        ("paid", "completed", True),
        ("paid", "refunded", True),
        ("paid", "payment_disputed", True),
        ("processing", "completed", True),
        ("processing", "paid", True),
        ("processing", "refunded", True),
        ("processing", "payment_disputed", True),
        ("payment_disputed", "paid", True),
        ("payment_disputed", "refunded", True),
        ("payment_disputed", "completed", False),
        ("payment_disputed", "processing", False),
        ("completed", "paid", False),
        ("completed", "processing", False),
        ("completed", "refunded", False),
        ("paid", "pending_payment", False),
        ("paid", "paid", True),
        ("completed", "completed", False),
        ("expired", "expired", False),
        ("refunded", "paid", False),
        ("refunded", "refunded", False),
    ],
)
def test_can_transition(old: str, new: str, ok: bool) -> None:
    assert can_transition(old, new) is ok


def test_require_transition_raises() -> None:
    with pytest.raises(ValueError, match="invalid_order_transition"):
        require_transition("pending_payment", "completed")
