from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from bot.services.vpn_subscription_notify_ux import KIND_TRIAL_H6
from bot.services.vpn_trial_reminder import (
    KIND_TRIAL_EXPIRED,
    KIND_TRIAL_H4,
    hours_until_expiry,
    message_for_trial_kind,
    trial_kind_for_hours_left,
)


def test_trial_kind_for_hours_left_window() -> None:
    assert trial_kind_for_hours_left(24.0) == "trial_d1"
    assert trial_kind_for_hours_left(5.5) == KIND_TRIAL_H6
    assert trial_kind_for_hours_left(3.0) is None
    assert trial_kind_for_hours_left(5.0) == KIND_TRIAL_H6
    assert trial_kind_for_hours_left(7.1) is None
    assert trial_kind_for_hours_left(10.0) is None


def test_hours_until_expiry() -> None:
    now = datetime(2026, 7, 8, 12, 0, tzinfo=timezone.utc)
    paid = (now + timedelta(hours=4)).isoformat()
    assert hours_until_expiry(paid, now=now) == pytest.approx(4.0, abs=0.01)


def test_message_for_trial_h6() -> None:
    text = message_for_trial_kind(
        kind=KIND_TRIAL_H6,
        paid_until="2026-07-09T12:00:00+00:00",
        hours_left=6.0,
    )
    assert "скоро закончится" in text.lower()
    assert "Ваш VPN закончится сегодня" in text
    assert "👥" in text
    assert "+1 день VPN" in text


def test_message_for_trial_expired() -> None:
    text = message_for_trial_kind(
        kind=KIND_TRIAL_EXPIRED,
        paid_until="2026-07-08T12:00:00+00:00",
    )
    assert "заверш" in text.lower()
    assert "отключён" in text.lower()
    assert "Happ" in text or "happ" in text.lower()
    assert "обновите подписку" in text.lower()
    assert "👥" in text or "друг" in text.lower()


def test_legacy_h4_message_still_renders() -> None:
    text = message_for_trial_kind(
        kind=KIND_TRIAL_H4,
        paid_until="2026-07-09T12:00:00+00:00",
        hours_left=4.1,
    )
    assert "скоро закончится" in text.lower()
    assert "Ваш VPN закончится сегодня" in text
