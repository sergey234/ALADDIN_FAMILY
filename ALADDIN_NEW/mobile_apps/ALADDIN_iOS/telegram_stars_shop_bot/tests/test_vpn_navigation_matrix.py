"""Регрессия навигации VPN UX: колбэки «Назад» по уровням."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VPN_PY = (ROOT / "bot" / "handlers" / "vpn.py").read_text(encoding="utf-8")
SCREEN_NAV = (ROOT / "bot" / "services" / "vpn_screen_nav.py").read_text(encoding="utf-8")
LINKS_PY = (ROOT / "bot" / "services" / "vpn_user_links.py").read_text(encoding="utf-8")
TARIFFS_PY = (ROOT / "bot" / "services" / "vpn_tariffs.py").read_text(encoding="utf-8")
STATUS_PY = (ROOT / "bot" / "services" / "vpn_user_status.py").read_text(encoding="utf-8")
CONNECT_PY = (ROOT / "bot" / "services" / "vpn_connect_copy.py").read_text(encoding="utf-8")


def test_marketing_cards_back_to_nav_vpn() -> None:
    assert "await _vpn_edit_or_answer(cb.message, text, kb_back_marketing())" in VPN_PY
    assert 'callback_data=VPN_NAV_MARKETING' in SCREEN_NAV or 'callback_data="nav:vpn"' in SCREEN_NAV


def test_help_subpages_back_to_help_menu() -> None:
    assert "_os_steps_html(slug, settings), kb_back_help_menu()" not in VPN_PY
    assert "vpn:instr:guide" in VPN_PY


def test_marketing_kb_no_instruction_or_policy_buttons() -> None:
    start = VPN_PY.index("def _vpn_marketing_kb")
    end = VPN_PY.index("def _vpn_root_kb_nav_rows", start)
    block = VPN_PY[start:end]
    assert "vpn:instr:menu" not in block
    assert "vpn:instr:guide" not in block
    assert "Политика конфиденциальности" not in block
    assert "vpn:y:speed" in block


def test_root_kb_card_has_instruction_and_settings() -> None:
    start = VPN_PY.index("def _vpn_root_kb_nav_rows")
    end = VPN_PY.index("async def _vpn_root_user_active", start)
    block = VPN_PY[start:end]
    assert "VPN_CHECKLIST_BTN" in block
    assert "VPN_EXTRA_MENU_BTN" in block
    assert "VPN_NAV_CHECKLIST" in block
    assert "VPN_NAV_EXTRA_MENU" in block
    assert "VPN_LOCATIONS_BTN" not in block
    assert "VPN_HELP_MENU_BTN" not in block


def test_build_vpn_root_kb_post_purchase_blocks() -> None:
    start = VPN_PY.index("async def build_vpn_root_kb")
    end = VPN_PY.index("def _vpn_root_kb(", start)
    block = VPN_PY[start:end]
    assert block.count("append_vpn_tariff_buy_rows") == 1
    assert "append_vpn_trial_row" in block
    assert "VPN_GET_VPN_BTN" in block
    assert "VPN_CHECKLIST_BTN" in block
    assert "VPN_EXTRA_MENU_BTN" in block
    assert "VPN_CHECK_BTN" in block
    assert "HAPP_DOWNLOAD_BTN" in block
    assert "VPN_HELP_MENU_BTN" in block
    assert "VPN_DEVICES" in block
    assert "vpn:check" in block
    assert "VPN_BUY_BTN" in block
    assert "VPN_TRIAL_GET_BTN" in block
    assert "TrialEligibility.OK" in block
    assert "active" in block
    # Дубль «Продлить» убран — тарифы сами продлевают.
    assert "Продлить подписку" not in block


def test_inactive_copy_exact() -> None:
    start = VPN_PY.index("def _vpn_manage_inactive_copy_html")
    end = VPN_PY.index("def _vpn_manage_active_hint_html", start)
    block = VPN_PY[start:end]
    assert "тариф" in block.lower() or "Тариф" in block
    assert "/sub" not in block


def test_main_screen_no_tech_hint() -> None:
    start = VPN_PY.index("def _vpn_manage_active_hint_html")
    end = VPN_PY.index("def _location_bodies_from_local_env", start)
    block = VPN_PY[start:end]
    assert "/sub" not in block
    assert "VLESS" not in block


def test_button_labels_post_purchase_tz() -> None:
    assert 'VPN_GET_VPN_BTN = "🔑 Получить ключ VPN"' in SCREEN_NAV
    assert 'VPN_CHECKLIST_BTN = "📖 Инструкция"' in SCREEN_NAV
    assert 'HAPP_DOWNLOAD_BTN = "🎬 Скачать Happ"' in SCREEN_NAV
    assert 'VPN_HELP_MENU_BTN = "❓ Помощь"' in SCREEN_NAV
    assert 'VPN_CHECK_BTN = "⚡ Проверить подключение"' in SCREEN_NAV
    assert 'VPN_QR_CONNECT_BTN = "📷 QR-код подключения VPN"' in LINKS_PY
    assert 'VPN_QR_CONNECT_BTN = "📷 QR-код подключения VPN"' in SCREEN_NAV
    assert 'COPY_SUB_LINK_BTN = "🔗 Скопировать ссылку VPN"' in LINKS_PY
    assert 'XRAY_SUBSCRIPTION_BTN = "📡 Открыть ссылку"' in LINKS_PY
    assert "старт" not in TARIFFS_PY or '"⭐ старт"' not in TARIFFS_PY
    # Кнопки: только смайлик-акцент, без маркетинговых названий.
    assert '30: "⭐"' in TARIFFS_PY
    assert '365: "👑"' in TARIFFS_PY
    assert "лучшая цена" not in TARIFFS_PY
    assert "Активен" in STATUS_PY
    assert "VLESS" not in CONNECT_PY[CONNECT_PY.index("def vpn_extra_menu_html") :][
        :400
    ]


def test_no_subpage_back_to_main_on_marketing_why() -> None:
    fn = VPN_PY.index("async def vpn_why_detail")
    chunk = VPN_PY[fn : fn + 3500]
    assert "kb_back_marketing()" in chunk
    assert "_vpn_subpage_back_kb" not in chunk
    assert "devices_hub_kb" in chunk
    assert "_render_device_card" in chunk
    assert "vpn_devices_platform_card" in VPN_PY
    assert "vpn:y:dev:iphone" in VPN_PY


def test_devices_hybrid_canon_in_hub_module() -> None:
    hub = (ROOT / "bot" / "services" / "vpn_devices_platform_hub.py").read_text(encoding="utf-8")
    assert "в планах" in hub
    assert "happ://add/" in hub
    assert "/sub/…" not in hub and "код /sub" not in hub
    assert "VPN_Y_DEV_IPHONE" in hub
    assert "VPN_Y_DEV_ANDROID" in hub
    assert "VPN_Y_DEV_IPAD" in hub
