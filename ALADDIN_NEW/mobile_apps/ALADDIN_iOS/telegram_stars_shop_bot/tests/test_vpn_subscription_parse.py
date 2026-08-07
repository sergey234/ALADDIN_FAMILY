from __future__ import annotations

import base64

from bot.services.vpn_user_links import (
    VLESS_MOBILE_RF_BTN,
    parse_subscription_vless_lines,
    pick_vless_profile_line,
)


def test_parse_plain_vless_lines() -> None:
    body = (
        "vless://uuid@host:8443?encryption=none#wifi-direct\n"
        "vless://uuid@host:8443?encryption=none#mobile-xhttp\n"
    )
    lines = parse_subscription_vless_lines(body)
    assert len(lines) == 2
    assert pick_vless_profile_line(lines) == lines[1]


def test_parse_base64_vless_lines() -> None:
    plain = "vless://uuid@host:8443?encryption=none#mobile-xhttp\n"
    encoded = base64.b64encode(plain.encode("utf-8")).decode("ascii")
    lines = parse_subscription_vless_lines(encoded)
    assert len(lines) == 1
    assert lines[0].endswith("#mobile-xhttp")


def test_pick_legacy_mobile_rf_alias() -> None:
    lines = ["vless://uuid@host:8443#mobile-rf"]
    assert pick_vless_profile_line(lines).endswith("#mobile-rf")


def test_mobile_button_label() -> None:
    assert VLESS_MOBILE_RF_BTN == "📋 4G-профиль"
