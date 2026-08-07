"""d10: текст пуша о первом подключении устройства."""

from bot.services.vpn_device_first_notify import device_first_connect_html


def test_device_first_connect_copy() -> None:
    html = device_first_connect_html(display_name="iPhone")
    assert "Новое устройство подключилось" in html
    assert "iPhone" in html
    assert "слот" not in html.lower()


def test_device_first_connect_escapes_html() -> None:
    html = device_first_connect_html(display_name="<script>")
    assert "<script>" not in html
    assert "&lt;script&gt;" in html
