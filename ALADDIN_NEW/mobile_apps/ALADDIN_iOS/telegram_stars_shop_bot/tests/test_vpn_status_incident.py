from __future__ import annotations

from bot.services.vpn_status_incident import PRESET_4G, resolve_preset, vpn_incident_status_html


def test_preset_4g() -> None:
    assert "4G" in PRESET_4G
    assert "🇷🇺 Вход RU" in PRESET_4G
    assert "Авто WiFi" not in PRESET_4G
    assert resolve_preset("lte") == PRESET_4G


def test_incident_banner_html() -> None:
    html = vpn_incident_status_html("Тест инцидента")
    assert "Статус VPN" in html
    assert "Тест инцидента" in html
    assert vpn_incident_status_html("") == ""
