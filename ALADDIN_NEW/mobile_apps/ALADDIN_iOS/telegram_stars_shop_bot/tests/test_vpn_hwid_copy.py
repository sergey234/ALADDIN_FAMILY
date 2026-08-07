from __future__ import annotations

from bot.services.vpn_connect_copy import vpn_happ_hwid_prereq_html, vpn_happ_plus_steps_html


def test_hwid_prereq_in_happ_steps() -> None:
    assert "HWID" in vpn_happ_hwid_prereq_html()
    assert "HWID" in vpn_happ_plus_steps_html()
    assert "Настройки" in vpn_happ_hwid_prereq_html()
