from __future__ import annotations

from bot.services.vpn_subscription_notify_ux import (
    KIND_D3,
    KIND_EXPIRED,
    KIND_H6,
    KIND_TRIAL_D1,
    KIND_TRIAL_EXPIRED,
    KIND_TRIAL_H6,
    EXTEND_BTN_ENDED,
    EXTEND_BTN_SOON,
    INVITE_BTN,
    format_until_msk,
    message_for_paid_kind,
    message_for_trial_kind,
    paid_kind_for_timing,
    subscription_notify_kb,
    trial_kind_for_hours_left,
)


def test_paid_kind_windows() -> None:
    assert paid_kind_for_timing(days_left=7, hours_left=200) == "d7"
    assert paid_kind_for_timing(days_left=3, hours_left=80) == KIND_D3
    assert paid_kind_for_timing(days_left=1, hours_left=20) == "d1"
    assert paid_kind_for_timing(days_left=0, hours_left=5.5) == KIND_H6
    assert paid_kind_for_timing(days_left=0, hours_left=12) is None
    assert paid_kind_for_timing(days_left=0, hours_left=3) is None


def test_trial_kind_windows() -> None:
    assert trial_kind_for_hours_left(24.0) == KIND_TRIAL_D1
    assert trial_kind_for_hours_left(5.0) == KIND_TRIAL_H6
    assert trial_kind_for_hours_left(3.0) is None
    assert trial_kind_for_hours_left(12.0) is None


def test_paid_copy_soon_and_ended() -> None:
    soon = message_for_paid_kind(kind=KIND_H6, paid_until="2026-07-30T20:59:00+00:00")
    assert "скоро закончится" in soon.lower()
    assert "ваш vpn закончится сегодня" in soon.lower()
    assert "меньше минуты" not in soon.lower()
    assert "продлить можно оплатой" not in soon.lower()
    assert "👥" in soon
    assert "+1 день VPN" in soon
    assert "+3 дня бесплатно" in soon
    assert "пробн" not in soon.lower()

    ended = message_for_paid_kind(kind=KIND_EXPIRED, paid_until="2026-07-30T20:59:00+00:00")
    assert "завершилась" in ended.lower()
    assert "отключён" in ended.lower()
    assert "👥" in ended
    assert "+1 день VPN" in ended
    assert "+3 дня бесплатно" in ended


def test_trial_copy_soon_and_ended() -> None:
    soon = message_for_trial_kind(
        kind=KIND_TRIAL_H6,
        paid_until="2026-07-30T20:59:00+00:00",
        hours_left=6.0,
    )
    assert "скоро закончится" in soon.lower()
    assert "ваш vpn закончится сегодня" in soon.lower()
    assert "меньше минуты" not in soon.lower()
    assert "+1 день VPN" in soon
    assert "+3 дня бесплатно" in soon

    ended = message_for_trial_kind(
        kind=KIND_TRIAL_EXPIRED,
        paid_until="2026-07-30T20:59:00+00:00",
    )
    assert "завершилась" in ended.lower()
    assert "отключён" in ended.lower()
    assert "+1 день VPN" in ended


def test_referral_invite_benefit_line_uses_trial_settings(monkeypatch) -> None:
    from bot.config import load_settings
    from bot.services.vpn_subscription_notify_ux import referral_invite_benefit_line

    monkeypatch.setenv("BOT_TOKEN", "9:ref-line")
    monkeypatch.setenv("ADMIN_IDS", "1")
    monkeypatch.setenv("API_KEY_PEPPER", "r" * 32)
    # Платные 3/7 не должны попасть в строку пуша — только trial 1/3.
    monkeypatch.setenv("VPN_REFERRAL_REFERRER_DAYS", "3")
    monkeypatch.setenv("VPN_REFERRAL_FRIEND_DAYS", "7")
    monkeypatch.setenv("VPN_TRIAL_REFERRAL_REFERRER_DAYS", "1")
    monkeypatch.setenv("VPN_TRIAL_REFERRAL_FRIEND_DAYS", "3")
    s = load_settings()
    line = referral_invite_benefit_line(s)
    assert line.startswith("👥")
    assert "+1 день VPN" in line
    assert "+3 дня бесплатно" in line
    assert "+7" not in line
    assert "оплатой" not in line



def test_notify_kb_buttons() -> None:
    soon = [btn.text for row in subscription_notify_kb().inline_keyboard for btn in row]
    assert EXTEND_BTN_SOON in soon
    assert INVITE_BTN in soon
    ended = [btn.text for row in subscription_notify_kb(ended=True).inline_keyboard for btn in row]
    assert EXTEND_BTN_ENDED in ended
    assert INVITE_BTN in ended


def test_format_until_msk() -> None:
    s = format_until_msk("2026-07-30T20:59:00+00:00")
    assert "2026" in s
    assert "по Москве" in s
