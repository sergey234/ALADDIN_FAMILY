from __future__ import annotations

from bot.services.vpn_connect_copy import (
    vpn_after_payment_expect_html,
    vpn_connect_methods_table_html,
    vpn_happ_plus_steps_html,
    vpn_happ_scam_warning_html,
    vpn_what_are_keys_html,
)
from bot.services.vpn_happ_constants import HAPP_APP_NAME, HAPP_IOS_APP_STORE_GLOBAL_URL


def test_vpn_what_are_keys_mentions_sub_and_happ() -> None:
    html = vpn_what_are_keys_html()
    assert "/sub/" in html
    assert HAPP_APP_NAME.split()[0] in html or "Happ" in html


def test_happ_app_store_url_official() -> None:
    from bot.services.vpn_connect_copy import vpn_happ_appstore_region_guide_html

    html = vpn_happ_appstore_region_guide_html()
    assert HAPP_IOS_APP_STORE_GLOBAL_URL in html
    assert "6783623643" in HAPP_IOS_APP_STORE_GLOBAL_URL


def test_vpn_after_payment_expect_plain_language() -> None:
    html = vpn_after_payment_expect_html()
    assert "этот чат" in html
    assert "QR" in html
    assert "/sub/" in html
    assert "Happ" in html
    assert vpn_happ_scam_warning_html() in html


def test_connect_methods_table_happ_plus() -> None:
    html = vpn_connect_methods_table_html()
    assert "Happ" in html
    assert "HWID" in html or "hwid" in html.lower()
    assert "🇷🇺 Вход RU" in html
    assert "Авто WiFi" not in html
    assert html == vpn_happ_plus_steps_html()


def test_vpn_appstore_region_guide() -> None:
    from bot.services.vpn_connect_copy import (
        vpn_happ_appstore_region_guide_html,
        vpn_happ_install_screen_html,
        vpn_happ_region_detailed_steps_html,
        vpn_happ_region_short_steps_html,
        vpn_happ_region_video_caption_html,
    )

    canon = vpn_happ_region_detailed_steps_html()
    for n in ("1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"):
        assert n in canon
    assert "Payment Method" in canon
    assert "Billing Address" in canon
    assert "Street" in canon
    assert "City/Town" in canon
    assert "Postcode" in canon
    assert "без способа оплаты" not in canon
    assert canon == vpn_happ_region_short_steps_html()
    assert canon == vpn_happ_install_screen_html()

    cap = vpn_happ_region_video_caption_html()
    assert canon in cap
    assert "Избранное" in cap
    assert "1️⃣" in cap
    assert "Payment Method" in cap
    assert len(cap) <= 1024, f"caption too long: {len(cap)}"

    html = vpn_happ_appstore_region_guide_html()
    assert canon in html
    assert "App Store" in html
