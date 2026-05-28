from __future__ import annotations

from bot.services.vpn_connect_copy import (
    vpn_after_payment_expect_html,
    vpn_conf_qr_glossary_html,
    vpn_what_are_keys_html,
)


def test_vpn_what_are_keys_mentions_private_and_qr_same_conf() -> None:
    html = vpn_what_are_keys_html()
    assert "QR" in html
    assert ".conf" in html
    assert "WireGuard" in html


def test_vpn_after_payment_expect_plain_language() -> None:
    html = vpn_after_payment_expect_html()
    assert "этот чат" in html
    assert ".conf" in html
    assert "QR" in html
    gloss = vpn_conf_qr_glossary_html()
    assert "личный ключ" in gloss
    assert "WireGuard" in gloss
