"""Каталог админ-команд — целостность разделов."""

from __future__ import annotations

from bot.services.admin_command_catalog import (
    ADMIN_HELP_SECTIONS,
    admin_help_hub_html,
    admin_help_section_html,
    section_by_key,
)


def test_admin_help_sections_unique_keys() -> None:
    keys = [s.key for s in ADMIN_HELP_SECTIONS]
    assert len(keys) == len(set(keys))
    assert section_by_key("vpn") is not None
    assert section_by_key("nope") is None


def test_admin_help_html_mentions_commands() -> None:
    hub = admin_help_hub_html()
    assert "Справка" in hub
    vpn = section_by_key("vpn")
    assert vpn is not None
    body = admin_help_section_html(vpn)
    assert "/admin_vpn_status" in body
    assert len(body) < 3500
