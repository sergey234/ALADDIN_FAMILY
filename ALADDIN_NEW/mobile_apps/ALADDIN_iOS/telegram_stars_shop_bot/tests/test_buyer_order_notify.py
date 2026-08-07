from __future__ import annotations

from bot.config import Settings
from bot.services.buyer_order_notify import (
    buyer_message_admin_status_change,
    buyer_message_auto_create_failed,
    buyer_message_auto_submitted,
    buyer_message_istar_completed,
)


def _s() -> Settings:
    return Settings(  # type: ignore[call-arg]
        BOT_TOKEN="9:t",
        ADMIN_IDS="1",
        API_KEY_PEPPER="k" * 32,
        SUPPORT_USERNAME="support_test_user",
    )


def test_admin_messages_non_empty_for_main_statuses() -> None:
    assert buyer_message_admin_status_change(order_id=42, new_status="paid") is not None
    assert buyer_message_admin_status_change(order_id=42, new_status="processing") is not None
    assert buyer_message_admin_status_change(order_id=42, new_status="completed") is not None
    assert buyer_message_admin_status_change(order_id=42, new_status="cancelled") is None


def test_auto_submitted_contains_order_id() -> None:
    t = buyer_message_auto_submitted(order_id=7)
    assert "#7" in t or ">7<" in t


def test_istar_completed_contains_order_id() -> None:
    t = buyer_message_istar_completed(order_id=9)
    assert "9" in t


def test_auto_create_failed_has_support_hint() -> None:
    t = buyer_message_auto_create_failed(order_id=3, settings=_s())
    assert "3" in t
    assert "t.me" in t or "support" in t.lower()
