from __future__ import annotations

from aiogram.types import CopyTextButton

from bot.services.vpn_connect_copy import (
    vpn_backup_apps_one_method_html,
    vpn_backup_link_explainer_html,
    vpn_friend_link_blurb_html,
    vpn_wg_vs_backup_table_html,
)
from bot.services.vpn_user_links import copy_text_button


def test_copy_text_button_wraps_url() -> None:
    btn = copy_text_button(label="📋 Скопировать запасную", text="https://example.com/sub/abc")
    assert btn.copy_text is not None
    assert isinstance(btn.copy_text, CopyTextButton)
    assert btn.copy_text.text.startswith("https://")


def test_backup_explainer_mentions_wireguard_and_apps() -> None:
    html = vpn_backup_link_explainer_html()
    assert "WireGuard" in html
    assert "Streisand" in html
    assert vpn_wg_vs_backup_table_html() in html


def test_backup_one_method_blurb() -> None:
    t = vpn_backup_apps_one_method_html()
    assert "Happ" in t
    assert "один" in t.lower()
    assert "v2rayNG" in t


def test_compare_table_covers_both_paths() -> None:
    t = vpn_wg_vs_backup_table_html()
    assert ".conf" in t
    assert "/sub/" in t
    assert "Happ" in t
    assert "Streisand" in t
    assert "App Store" in t
    assert "Не путать" not in t


def test_friend_blurb_not_confused_with_backup() -> None:
    html = vpn_friend_link_blurb_html()
    assert "друг" in html.lower()
    assert "Скопировать приглашение" in html


def test_invite_ref_telegram_url_uses_ref_prefix() -> None:
    from bot.services.vpn_user_links import invite_ref_telegram_url

    url = invite_ref_telegram_url("aimonkey_bot", 4242)
    assert url == "https://t.me/aimonkey_bot?start=ref_4242"
    assert "r-" not in url.split("start=")[-1]
