from __future__ import annotations

from datetime import datetime, timedelta, timezone

from bot.services.vpn_expiry_notify import kind_for_days_left
from bot.services.vpn_subscription_dates import compute_paid_until_after_purchase, days_until_expiry


def test_compute_paid_until_stacks_on_remaining_days() -> None:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    future = (now + timedelta(days=10)).isoformat()
    out = compute_paid_until_after_purchase(current_paid_until=future, days=30)
    end = datetime.fromisoformat(out.replace("Z", "+00:00"))
    assert end >= now + timedelta(days=39)


def test_kind_for_reminder_windows() -> None:
    assert kind_for_days_left(7) == "d7"
    assert kind_for_days_left(3) == "d3"
    assert kind_for_days_left(1) == "d1"
    assert kind_for_days_left(0) == "d0"
    assert kind_for_days_left(5) is None


def test_days_until_expiry() -> None:
    now = datetime(2026, 5, 16, 12, 0, 0, tzinfo=timezone.utc)
    pu = "2026-05-23T12:00:00+00:00"
    assert days_until_expiry(pu, now=now) == 7
