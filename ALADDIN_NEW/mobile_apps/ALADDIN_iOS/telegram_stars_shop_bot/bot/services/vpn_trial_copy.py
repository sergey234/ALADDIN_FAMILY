"""Тексты пробного периода VPN из settings.vpn_trial_hours."""

from __future__ import annotations

from bot.config import Settings


def vpn_trial_period_phrase(settings: Settings | None) -> str:
    hours = max(1, int((settings.vpn_trial_hours if settings else 72) or 72))
    if hours == 72:
        return "72 часа (трое суток)"
    if hours % 24 == 0:
        d = hours // 24
        if d % 10 == 1 and d % 100 != 11:
            return f"{d} день"
        if d % 10 in (2, 3, 4) and d % 100 not in (12, 13, 14):
            return f"{d} дня"
        return f"{d} дней"
    return f"{hours} ч."


def vpn_trial_button_text(settings: Settings) -> str:
    hours = max(1, int(settings.vpn_trial_hours or 72))
    if hours == 72:
        return "🎁 Активировать 3 суток бесплатно"
    return f"🎁 Активировать {vpn_trial_period_phrase(settings)} бесплатно"


def vpn_trial_period_title(settings: Settings) -> str:
    return f"Пробный период: {vpn_trial_period_phrase(settings)}"