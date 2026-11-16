"""Policy A: free + active trial_end grants antifake; expired/free deny; premium allow."""
from __future__ import annotations

from datetime import datetime, timedelta

from app.services.antifake_premium import (
    effective_level_from_parts,
    trial_end_is_active,
    user_has_antifake_access,
)


def test_trial_end_is_active_future():
    assert trial_end_is_active(datetime.utcnow() + timedelta(days=3)) is True


def test_trial_end_is_active_past():
    assert trial_end_is_active(datetime.utcnow() - timedelta(days=3)) is False


def test_effective_level_free_with_active_trial():
    end = datetime.utcnow() + timedelta(days=7)
    assert effective_level_from_parts("free", "free", end) == "trial"


def test_effective_level_free_with_expired_trial():
    end = datetime.utcnow() - timedelta(days=7)
    assert effective_level_from_parts("free", "free", end) == "free"


def test_effective_level_paid_wins():
    end = datetime.utcnow() + timedelta(days=7)
    assert effective_level_from_parts("premium", "free", end) == "premium"
    assert effective_level_from_parts("free", "family", end) == "family"


def test_user_has_antifake_access_jwt_trial_end():
    end = (datetime.utcnow() + timedelta(days=5)).isoformat() + "Z"
    user = {"id": "1", "subscription_level": "free", "trial_end": end}
    assert user_has_antifake_access(user) is True


def test_user_has_antifake_access_free_no_trial():
    user = {"id": "1", "subscription_level": "free"}
    assert user_has_antifake_access(user) is False


def test_user_has_antifake_access_premium_level():
    user = {"id": "1", "subscription_level": "premium"}
    assert user_has_antifake_access(user) is True
