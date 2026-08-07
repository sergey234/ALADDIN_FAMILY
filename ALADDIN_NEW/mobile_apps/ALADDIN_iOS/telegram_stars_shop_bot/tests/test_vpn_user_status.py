from __future__ import annotations

from datetime import datetime, timedelta, timezone

from bot.services.vpn_user_status import (
    ACTIVE_STATUS_MARKER,
    CLOSED_STATUS_MARKER,
    format_remaining_days_short,
    format_remaining_dhm,
    format_until_ddmmyyyy,
    format_until_ddmmyyyy_hhmm,
    vpn_soft_expiry_nudge_needed,
    vpn_user_status_block_html_from_row,
)


def test_format_remaining_dhm() -> None:
    now = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)
    end = now + timedelta(days=12, hours=5, minutes=12)
    assert format_remaining_dhm(end, now=now) == "12 дней 5 часов 12 минут"


def test_format_remaining_days_short() -> None:
    now = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)
    end = now + timedelta(days=388)
    assert format_remaining_days_short(end, now=now) == "388 дней"
    soon = now + timedelta(hours=5)
    assert format_remaining_days_short(soon, now=now) == "5 часов"


def test_status_active_block() -> None:
    now = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)
    end = now + timedelta(days=2, hours=3, minutes=0)
    html = vpn_user_status_block_html_from_row(
        {"status": "vpn_active", "paid_until": end.isoformat(), "account_kind": "paid"},
        inactive_variant="profile",
        now=now,
    )
    assert "🟢" in html
    assert ACTIVE_STATUS_MARKER in html
    assert "Тариф: Платный" in html
    assert "⏳ Осталось:" in html
    assert "2 дня 3 часа" in html
    assert "📅 Действует до:" in html
    until = format_until_ddmmyyyy_hhmm(end.isoformat())
    assert until in html


def test_status_inactive_unified() -> None:
    for variant in ("profile", "vpn_section"):
        html = vpn_user_status_block_html_from_row(None, inactive_variant=variant)
        assert "🔴" in html
        assert CLOSED_STATUS_MARKER in html
        assert "нет активной подписки" in html
    expired = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    html_section = vpn_user_status_block_html_from_row(
        {"status": "vpn_active", "paid_until": expired, "account_kind": "paid"},
        inactive_variant="vpn_section",
    )
    assert "🔴" in html_section
    assert "нет активной подписки" in html_section
    html_profile = vpn_user_status_block_html_from_row(
        {"status": "vpn_active", "paid_until": expired, "account_kind": "paid"},
        inactive_variant="profile",
    )
    assert CLOSED_STATUS_MARKER in html_profile
    assert "Действовала до:" in html_profile


def test_vpn_section_active_showcase_card() -> None:
    """Главный экран VPN после покупки — статус + плюсы, без техтерминов."""
    now = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)
    end = now + timedelta(days=393, hours=0, minutes=0)
    html = vpn_user_status_block_html_from_row(
        {"status": "vpn_active", "paid_until": end.isoformat(), "account_kind": "paid"},
        inactive_variant="vpn_section",
        now=now,
    )
    assert html.startswith("🟢")
    assert ACTIVE_STATUS_MARKER in html
    assert "⏳ Осталось:" in html
    assert "393 дня" in html
    assert "📅 До:" in html
    assert format_until_ddmmyyyy(end.isoformat()) in html
    assert "Высокая скорость" in html
    assert "Стабильно работает в России" in html
    assert "кнопками ниже" in html
    assert "Тариф:" not in html
    assert "/sub" not in html
    assert "VLESS" not in html
    assert "Happ" not in html


def test_soft_nudge() -> None:
    now = datetime(2026, 7, 14, 12, 0, tzinfo=timezone.utc)
    soon = (now + timedelta(hours=12)).isoformat()
    assert vpn_soft_expiry_nudge_needed(
        {"status": "vpn_active", "paid_until": soon}, now=now
    )
    assert vpn_soft_expiry_nudge_needed({"status": "vpn_expired", "paid_until": soon})
    far = (now + timedelta(days=10)).isoformat()
    assert not vpn_soft_expiry_nudge_needed(
        {"status": "vpn_active", "paid_until": far}, now=now
    )
