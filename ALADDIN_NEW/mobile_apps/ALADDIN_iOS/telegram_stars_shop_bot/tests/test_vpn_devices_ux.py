"""Экран «Мои устройства» — карточки, без слова «слот»."""

from bot.services.vpn_devices_ux import (
    device_card_html,
    device_card_keyboard,
    devices_panel_url,
    devices_progress_bar,
    devices_revoke_confirm_html,
    devices_screen_html,
    format_connected_ru,
)


def _sample_payload() -> dict:
    return {
        "used": 1,
        "max": 1,
        "can_add": False,
        "devices": [
            {
                "id": 1,
                "display_name": "Телефон жены",
                "device_kind": "iphone",
                "status": "online",
                "first_connected_at": "2026-06-12T10:00:00+00:00",
                "subscription_url": "https://aladdin-ai.ru/sub/abc123",
            },
        ],
    }


def test_devices_copy_has_no_slot_word() -> None:
    html = devices_screen_html(_sample_payload())
    assert "слот" not in html.lower()
    assert "Мои устройства" in html
    assert "Телефон жены" in html
    assert "1 из 1" in html


def test_card_shows_one_device() -> None:
    html = device_card_html(_sample_payload(), 0)
    assert "Телефон жены" in html
    assert "Устройство <b>1 из 1</b>" in html


def test_progress_colors() -> None:
    # max=1: one free place → warn (yellow); full → red
    assert "🟡" in devices_progress_bar(0, 1)
    assert "🔴" in devices_progress_bar(1, 1)
    assert "🟢" in devices_progress_bar(1, 5)


def test_revoke_confirm_matches_tz() -> None:
    t = devices_revoke_confirm_html(display_name="Телефон жены")
    assert "заменить" in t.lower() or "отвяж" in t.lower()
    assert "недействительной" in t.lower()
    assert "Телефон жены" in t
    assert "слот" not in t.lower()
    assert "1 из 1" in t


def test_connected_date_ru() -> None:
    assert format_connected_ru("2026-06-12T10:00:00+00:00") == "Подключен 12 июня 2026"
    assert format_connected_ru(None) == ""


def test_keyboard_no_add_when_full_has_panel() -> None:
    kb = device_card_keyboard(
        _sample_payload(), 0, panel_url=devices_panel_url("https://get.aladdin-ai.ru")
    )
    raw = kb.model_dump_json()
    assert "vpn:devices:qr:1" in raw
    assert "vpn:devices:ren:1" in raw
    assert "Подключить устройство" not in raw
    assert "Заменить" in raw
    assert "Открыть в Happ" in raw
    assert "vpn:devices:openhapp:1" in raw
    assert "happ://add/" not in raw
    assert "Полная панель в браузере" in raw
    assert "/devices" in raw
    assert "слот" not in raw.lower()


def test_card_mentions_plans_not_multi() -> None:
    html = device_card_html(_sample_payload(), 0)
    assert "в планах" in html
    assert "5 устройств" not in html
    assert "/sub" not in html


def test_keyboard_add_when_empty() -> None:
    empty = {"used": 0, "max": 1, "can_add": True, "devices": []}
    kb = device_card_keyboard(empty, 0, panel_url="")
    raw = kb.model_dump_json()
    assert "Подключить устройство" in raw
    assert "vpn:devices:add" in raw


def test_panel_url() -> None:
    assert devices_panel_url("https://get.aladdin-ai.ru/") == "https://get.aladdin-ai.ru/devices"
