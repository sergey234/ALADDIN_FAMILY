from __future__ import annotations

from bot.services.vpn_post_purchase_delivery import (
    _post_payment_copy_kb,
    vpn_paid_ack_html,
)
from bot.services.vpn_user_links import COPY_SUB_LINK_BTN, XRAY_SUBSCRIPTION_BTN


def test_vpn_paid_ack_html_contains_order() -> None:
    html = vpn_paid_ack_html(order_id=99)
    assert "99" in html
    assert "AiMonkeyVPN" in html
    assert "Happ" in html
    assert "этот чат" in html


def test_post_payment_kb_has_sub_copy_button_vpn72() -> None:
    kb = _post_payment_copy_kb(sub_url="https://aladdin-ai.ru/sub/test-token")
    assert kb.inline_keyboard
    labels = [row[0].text for row in kb.inline_keyboard if row]
    assert XRAY_SUBSCRIPTION_BTN not in labels
    assert COPY_SUB_LINK_BTN in labels
    assert any("Скопировать" in label for label in labels)
