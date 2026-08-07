from __future__ import annotations

import pytest

from bot.config import Settings
from bot.services.lava_api import _lava_pick_qr_url
from bot.services.vpn_payment_copy import (
    VPN_SBP_INVOICE_BTN,
    vpn_invoice_pay_url_button_label,
    vpn_invoice_sbp_checkout_html,
)


def test_lava_pick_qr_url() -> None:
    assert _lava_pick_qr_url({"url": "https://pay.example/x"}) is None
    assert _lava_pick_qr_url({"qrUrl": "https://cdn.example/qr.png"}) == "https://cdn.example/qr.png"


def test_sbp_checkout_html_steps() -> None:
    html = vpn_invoice_sbp_checkout_html(order_id=42, rub_due=290.0, qr_in_chat=False)
    assert "QR" in html
    assert "банка" in html
    assert "WireGuard" not in html
    assert "290" in html


def test_sbp_button_label_length() -> None:
    assert len(VPN_SBP_INVOICE_BTN) <= 64


def test_pay_url_button_sbp() -> None:
    assert "СБП" in vpn_invoice_pay_url_button_label(channel="sbp")


def test_pay_url_qr_png() -> None:
    from bot.services.wg_qr_util import pay_url_qr_png_bytes

    png = pay_url_qr_png_bytes("https://pay.example/invoice/1")
    assert png[:8] == b"\x89PNG\r\n\x1a\n"


def test_invoice_hint_mentions_vpn_qr_not_payment(monkeypatch: pytest.MonkeyPatch) -> None:
    from bot.config import load_settings
    from bot.services.vpn_payment_copy import vpn_invoice_fiat_methods_hint_html

    monkeypatch.setenv("BOT_TOKEN", "9:vpn-pay")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "g" * 32)
    monkeypatch.setenv("USD_RUB_RATE", "80")
    monkeypatch.setenv("LAVA_SHOP_ID", "shop")
    monkeypatch.setenv("LAVA_SECRET_KEY", "secret")
    monkeypatch.setenv("LAVA_HOOK_URL", "https://example.com/hook")
    s = load_settings()
    html = vpn_invoice_fiat_methods_hint_html(s, payment_method="fiat")
    assert "Happ" in html or "/sub/" in html
    assert "НСПК" in html or "QR" in html
