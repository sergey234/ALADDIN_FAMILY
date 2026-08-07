"""Пуши о начислении VPN-рефбонусов (платный + trial)."""

from __future__ import annotations

from bot.config import Settings
from bot.services.buyer_order_notify import schedule_buyer_html


def _days_word(n: int) -> str:
    n = abs(int(n))
    mod10 = n % 10
    mod100 = n % 100
    if mod10 == 1 and mod100 != 11:
        return "день"
    if mod10 in (2, 3, 4) and mod100 not in (12, 13, 14):
        return "дня"
    return "дней"


def message_paid_referrer(days: int) -> str:
    d = max(0, int(days))
    return (
        "🎉 По вашей рекомендации пользователь впервые подключил VPN.\n\n"
        f"🎁 Вам начислено +{d} {_days_word(d)} VPN."
    )


def message_paid_friend(days: int) -> str:
    d = max(0, int(days))
    return (
        "🎉 Спасибо за подключение!\n\n"
        f"🎁 Вам начислено +{d} {_days_word(d)} VPN в подарок."
    )


def message_trial_referrer(days: int) -> str:
    d = max(0, int(days))
    return (
        "🎉 Ваш друг активировал пробный период.\n\n"
        f"🎁 Вам начислен +{d} {_days_word(d)} VPN."
    )


def message_trial_friend(days: int) -> str:
    d = max(0, int(days))
    return (
        "🎉 Добро пожаловать!\n\n"
        f"🎁 Вам доступно {d} {_days_word(d)} VPN бесплатно."
    )


def schedule_paid_referral_bonus_messages(settings: Settings, grant: dict) -> None:
    friend_d = int(grant.get("friend_days") or 0)
    ref_d = int(grant.get("referrer_days") or 0)
    referred = int(grant["referred_user_id"])
    referrer = int(grant["referrer_user_id"])
    if ref_d > 0:
        schedule_buyer_html(settings, referrer, message_paid_referrer(ref_d))
    if friend_d > 0:
        schedule_buyer_html(settings, referred, message_paid_friend(friend_d))


def schedule_trial_referral_bonus_messages(settings: Settings, grant: dict) -> None:
    """Другу — дни из VPN_TRIAL_REFERRAL_FRIEND_DAYS (уже в trial); пригласившему — из grant."""
    ref_d = int(grant.get("referrer_days") or 0)
    friend_d = max(0, int(settings.vpn_trial_referral_friend_days or 0))
    referred = int(grant["referred_user_id"])
    referrer = int(grant["referrer_user_id"])
    if ref_d > 0:
        schedule_buyer_html(settings, referrer, message_trial_referrer(ref_d))
    if friend_d > 0:
        schedule_buyer_html(settings, referred, message_trial_friend(friend_d))
