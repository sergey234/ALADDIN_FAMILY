from __future__ import annotations

from bot.config import load_settings
from bot.services.marketing import referral_faq_html
from bot.services.vpn_connect_copy import vpn_happ_android_steps_html, vpn_happ_android_wip_html
from bot.services.vpn_happ_constants import HAPP_ANDROID_PLAY_URL


def test_referral_faq_spend_all_copy(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:faq")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("REF_BONUS_VPN_ONLY", "false")
    html = referral_faq_html(load_settings())
    assert "VPN, Stars и Premium" in html
    assert "1000" in html
    assert "Реферальный баланс" in html
    assert "только на VPN" not in html
    assert "Бонусный баланс" not in html
    assert "из профиля" not in html
    assert "любые покупки" not in html.lower()


def test_android_happ_steps_html() -> None:
    html = vpn_happ_android_steps_html()
    assert HAPP_ANDROID_PLAY_URL in html
    assert "HWID" in html
    assert "/sub/" in html
    assert "Вход RU" in html
    assert "в разработке" not in html.lower()
    assert vpn_happ_android_wip_html() == html
