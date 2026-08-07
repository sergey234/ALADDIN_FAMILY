from __future__ import annotations

from bot.services.wg_conf_validate import wg_conf_validate, wg_conf_validate_summary_html

GOOD_CONF = """[Interface]
PrivateKey = abc
Address = 10.8.0.10/32
MTU = 1280
DNS = 10.8.0.1

[Peer]
PublicKey = xyz
Endpoint = 185.225.233.150:443
AllowedIPs = 0.0.0.0/0
PersistentKeepalive = 25
"""

OLD_CONF = GOOD_CONF.replace(":443", ":51820").replace(
    "AllowedIPs = 0.0.0.0/0", "AllowedIPs = 0.0.0.0/0, ::/0"
)


def test_wg_conf_validate_ok() -> None:
    ok, issues = wg_conf_validate(GOOD_CONF)
    assert ok is True
    assert issues == []


def test_wg_conf_validate_rejects_legacy() -> None:
    ok, issues = wg_conf_validate(OLD_CONF)
    assert ok is False
    assert any("51820" in i for i in issues)
    assert any("::/0" in i for i in issues)


def test_wg_conf_validate_summary_ok() -> None:
    html = wg_conf_validate_summary_html(GOOD_CONF)
    assert "актуален" in html
    assert ":443" in html


def test_wg_conf_import_rules_mention_port_and_ios() -> None:
    from bot.services.vpn_connect_copy import vpn_wireguard_import_rules_html

    html = vpn_wireguard_import_rules_html()
    assert ":443" in html
    assert "::/0" in html
    assert "Private Relay" in html
    assert "100 KB" in html
