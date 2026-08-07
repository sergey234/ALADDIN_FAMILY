from bot.services.vpn_connect_copy import vpn_happ_tunnel_report_html


def test_happ_tunnel_report_html() -> None:
    html = vpn_happ_tunnel_report_html()
    assert "tunnel.log" in html or "Логи" in html
    assert "HWID" in html
    assert "🇷🇺 Вход RU" in html
    assert "Авто WiFi" not in html
