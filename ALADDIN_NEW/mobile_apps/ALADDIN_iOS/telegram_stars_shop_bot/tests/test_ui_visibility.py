from __future__ import annotations

from bot.config import load_settings
from bot.keyboards.shop_kb import hub_menu_kb
from bot.services.ui_visibility import gifts_menu_visible, vpn_menu_visible


def _flat_labels(settings, user_id: int) -> list[str]:
    kb = hub_menu_kb(settings, user_id=user_id)
    return [b.text for row in kb.inline_keyboard for b in row]


def test_vpn_visible_for_admin_only_when_flag_off(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:vpn")
    monkeypatch.setenv("USD_RUB_RATE", "100")
    monkeypatch.setenv("UI_SHOW_VPN", "false")
    monkeypatch.setenv("UI_SHOW_GIFTS", "false")
    monkeypatch.setenv("ADMIN_IDS", "12345")
    settings = load_settings()
    admin = _flat_labels(settings, 12345)
    user = _flat_labels(settings, 99999)
    assert "🌐 VPN" in admin
    assert "🌐 VPN" not in user
    assert "🎁 Подарки" not in admin
    assert "🎁 Подарки" not in user
    assert vpn_menu_visible(12345, settings) is True
    assert vpn_menu_visible(99999, settings) is False
    assert gifts_menu_visible(settings) is False


def test_vpn_and_gifts_for_all_when_flags_on(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "1:vpn")
    monkeypatch.setenv("USD_RUB_RATE", "100")
    monkeypatch.setenv("UI_SHOW_VPN", "true")
    monkeypatch.setenv("UI_SHOW_GIFTS", "true")
    settings = load_settings()
    labels = _flat_labels(settings, 99999)
    kb = hub_menu_kb(settings, user_id=99999)
    first_row = [b.callback_data for b in kb.inline_keyboard[0]]
    assert first_row == ["nav:vpn", "nav:buy_stars"]
    assert kb.inline_keyboard[1][0].callback_data == "nav:premium"
    assert "🌐 VPN" in labels
    assert "🎁 Подарки" in labels
