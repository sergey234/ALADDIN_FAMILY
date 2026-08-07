"""Гибрид витрины «Все устройства» — Platform Hub (гость)."""

from bot.services.vpn_devices_platform_hub import (
    DEVICE_LIMIT_FOOTER_HTML,
    devices_hub_html,
    devices_hub_kb,
    happ_add_deeplink,
    happ_open_url_button,
    platform_android_html,
    platform_card_html,
    platform_ipad_html,
    platform_iphone_html,
    replace_device_button_label,
)


def test_hub_no_sub_tech() -> None:
    html = devices_hub_html()
    assert "Мои устройства" in html
    assert "/sub" not in html
    assert "Happ" not in html or "в планах" in html.lower()
    assert "в планах" in html
    assert "одно устройство" in html.lower() or "Одно устройство" in html
    assert "5 устройств" not in html
    assert DEVICE_LIMIT_FOOTER_HTML.split("\n")[0] in html


def test_hub_kb_platforms() -> None:
    raw = devices_hub_kb().model_dump_json()
    assert "vpn:y:dev:iphone" in raw
    assert "vpn:y:dev:android" in raw
    assert "vpn:y:dev:ipad" in raw
    assert "nav:vpn" in raw


def test_platform_cards_short_and_honest() -> None:
    for fn in (platform_iphone_html, platform_android_html, platform_ipad_html):
        html = fn()
        assert "HWID" in html
        assert "/sub" not in html
        assert "в планах" in html
        assert "слот" not in html.lower()
    assert "iPad" in platform_ipad_html()
    assert platform_card_html("iphone") == platform_iphone_html()
    assert platform_card_html("unknown") == devices_hub_html()


def test_happ_deeplink_plain_url() -> None:
    sub = "https://aladdin-ai.ru/sub/abc123"
    assert happ_add_deeplink(sub) == f"happ://add/{sub}"
    assert happ_add_deeplink("") == ""
    # Telegram не принимает happ:// в url= — кнопка только через callback.
    assert happ_open_url_button(sub) is None
    from bot.services.vpn_devices_platform_hub import (
        happ_open_callback_button,
        happ_open_message_html,
    )

    btn = happ_open_callback_button(7)
    assert btn is not None
    assert btn.callback_data == "vpn:devices:openhapp:7"
    html = happ_open_message_html(sub)
    assert "happ://add/" in html
    assert sub in html


def test_replace_label() -> None:
    assert "Заменить" in replace_device_button_label("iPhone жены")
    assert len(replace_device_button_label("x" * 80)) <= 64
