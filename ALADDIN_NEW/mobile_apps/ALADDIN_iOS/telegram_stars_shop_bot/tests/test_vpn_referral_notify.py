"""Тесты текстов начисления VPN-рефбонусов (ТЗ п.6)."""

from __future__ import annotations

from bot.services.vpn_referral_notify import (
    message_paid_friend,
    message_paid_referrer,
    message_trial_friend,
    message_trial_referrer,
)


def test_paid_bonus_messages() -> None:
    ref = message_paid_referrer(3)
    assert "впервые подключил VPN" in ref
    assert "+3 дня VPN" in ref

    friend = message_paid_friend(7)
    assert "Спасибо за подключение" in friend
    assert "+7 дней VPN в подарок" in friend


def test_trial_bonus_messages() -> None:
    ref = message_trial_referrer(1)
    assert "активировал пробный период" in ref
    assert "+1 день VPN" in ref

    friend = message_trial_friend(3)
    assert "Добро пожаловать" in friend
    assert "3 дня VPN бесплатно" in friend
