"""Gap tests T11 checkout conflict helpers + media copy."""

from __future__ import annotations

from bot.assistant.keyboards import CHECKOUT_BLOCK_HTML, MEDIA_REJECT_HTML
from bot.handlers.assistant import _is_blocking_shop_fsm


def test_checkout_fsm_blocks_assistant_text_path() -> None:
    assert _is_blocking_shop_fsm("CheckoutStates:waiting_confirm") is True
    assert _is_blocking_shop_fsm("CheckoutStates:waiting_recipient") is True
    assert _is_blocking_shop_fsm("BuyStarsCustomStates:waiting_qty") is True
    assert _is_blocking_shop_fsm("AssistantStates:active") is False
    assert _is_blocking_shop_fsm(None) is False
    assert "завершите" in CHECKOUT_BLOCK_HTML.lower() or "оплат" in CHECKOUT_BLOCK_HTML.lower()


def test_media_reject_copy() -> None:
    assert "текст" in MEDIA_REJECT_HTML.lower()
    assert "Человек" in MEDIA_REJECT_HTML
