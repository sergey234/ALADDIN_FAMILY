from bot.services.vpn_screen_nav import VPN_HAPP_INSTALL_VIDEO, VPN_SUB_LINK
from bot.services.vpn_user_links import COPY_SUB_LINK_BTN, XRAY_SUBSCRIPTION_BTN
from bot.services.vpn_xray_delivery import xray_import_reply_kb


def test_xray_import_reply_kb_happ_plus() -> None:
    kb = xray_import_reply_kb(
        sub_url="https://aladdin-ai.ru/sub/token123",
        vless_line="",
    ).as_markup()
    callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    assert VPN_SUB_LINK not in callbacks
    assert VPN_HAPP_INSTALL_VIDEO in callbacks
    labels = [btn.text for row in kb.inline_keyboard for btn in row]
    assert XRAY_SUBSCRIPTION_BTN not in labels
    assert COPY_SUB_LINK_BTN in labels
    assert any("Happ" in t for t in labels)


def test_xray_import_reply_kb_has_copy_text() -> None:
    kb = xray_import_reply_kb(
        sub_url="https://aladdin-ai.ru/sub/token123",
        vless_line="",
    ).as_markup()
    copy_rows = [
        btn
        for row in kb.inline_keyboard
        for btn in row
        if btn.copy_text is not None
    ]
    assert len(copy_rows) == 1
    assert copy_rows[0].copy_text.text.startswith("https://")
