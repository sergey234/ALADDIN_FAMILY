"""Регрессия навигации VPN UX: колбэки «Назад» по уровням."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VPN_PY = (ROOT / "bot" / "handlers" / "vpn.py").read_text(encoding="utf-8")
SCREEN_NAV = (ROOT / "bot" / "services" / "vpn_screen_nav.py").read_text(encoding="utf-8")


def test_marketing_cards_back_to_nav_vpn() -> None:
    assert "await _vpn_edit_or_answer(cb.message, text, kb_back_marketing())" in VPN_PY
    assert 'callback_data=VPN_NAV_MARKETING' in SCREEN_NAV or 'callback_data="nav:vpn"' in SCREEN_NAV


def test_help_subpages_back_to_help_menu() -> None:
    for needle in (
        "vpn_file_import_html(), kb_back_help_menu()",
        "vpn_qr_import_html(), kb_back_help_menu()",
        "_os_steps_html(slug, settings), kb_back_help_menu()",
    ):
        assert needle in VPN_PY


def test_marketing_kb_no_instruction_or_policy_buttons() -> None:
    start = VPN_PY.index("def _vpn_marketing_kb")
    end = VPN_PY.index("def _vpn_root_kb_base", start)
    block = VPN_PY[start:end]
    assert "vpn:instr:menu" not in block
    assert "vpn:instr:guide" not in block
    assert "Политика конфиденциальности" not in block
    assert "vpn:y:speed" in block


def test_root_kb_has_help_not_duplicate_instruction() -> None:
    start = VPN_PY.index("def _vpn_root_kb_base")
    end = VPN_PY.index("async def build_vpn_root_kb", start)
    block = VPN_PY[start:end]
    assert "VPN_HELP_MENU_BTN" in block
    assert "VPN_FALLBACK_MENU_BTN" in block
    assert "VPN_CHECKLIST_BTN" in block
    assert "VPN_NAV_CHECKLIST" in block
    assert "vpn:os:ios" not in block
    assert "Политика конфиденциальности" not in block
    qr_pos = block.index("vpn:wg:qr")
    checklist_pos = block.index("VPN_NAV_CHECKLIST")
    check_pos = block.index("vpn:check")
    assert qr_pos < checklist_pos < check_pos


def test_no_subpage_back_to_main_on_marketing_why() -> None:
    fn = VPN_PY.index("async def vpn_why_detail")
    chunk = VPN_PY[fn : fn + 2000]
    assert "kb_back_marketing()" in chunk
    assert "_vpn_subpage_back_kb" not in chunk
