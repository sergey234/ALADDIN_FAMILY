"""Общие тексты/кнопки напоминаний подписки (paid + trial). Без нового экрана."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot.brand_constants import VPN_PRODUCT_NAME
from bot.config import Settings
from bot.services.vpn_connect_copy import vpn_payment_button_label
from bot.services.vpn_legal_gate import VPN_LEGAL_GATE_CALLBACK
from bot.services.vpn_subscription_dates import format_datetime_display_msk, parse_paid_until_utc
from bot.util_html import esc

KIND_WELCOME = "welcome"
KIND_D7 = "d7"
KIND_D3 = "d3"
KIND_D1 = "d1"
KIND_H6 = "h6"
KIND_EXPIRED = "expired"
# legacy — не слать снова, если уже ушёл
KIND_D0_LEGACY = "d0"

KIND_TRIAL_WELCOME = "trial_welcome"
KIND_TRIAL_D1 = "trial_d1"
KIND_TRIAL_H6 = "trial_h6"
KIND_TRIAL_H3 = "trial_h3"  # legacy
KIND_TRIAL_H4 = "trial_h4"  # legacy
KIND_TRIAL_EXPIRED = "trial_expired"

EXTEND_BTN_SOON = "💎 Продлить VPN"
EXTEND_BTN_ENDED = "🚀 Продлить VPN"
EXTEND_BTN = EXTEND_BTN_SOON  # legacy alias
INVITE_BTN = "👥 Пригласить друга"


def referral_bonus_days(settings: Settings | None) -> int:
    """Платный реф: дни пригласившему (для welcome/d7/d3 и т.п.)."""
    if settings is None:
        return 3
    return max(0, int(settings.vpn_referral_referrer_days or 0))


def referral_friend_bonus_days(settings: Settings | None) -> int:
    """Платный реф: дни другу."""
    if settings is None:
        return 7
    return max(0, int(settings.vpn_referral_friend_days or 0))


def trial_referral_bonus_days(settings: Settings | None) -> int:
    """Trial-реф: дни пригласившему (+1) — для строки в пушах скоро/закончилась."""
    if settings is None:
        return 1
    return max(0, int(settings.vpn_trial_referral_referrer_days or 0))


def trial_referral_friend_bonus_days(settings: Settings | None) -> int:
    """Trial-реф: дни другу (3 дня trial) — для строки в пушах скоро/закончилась."""
    if settings is None:
        return 3
    return max(0, int(settings.vpn_trial_referral_friend_days or 0))


def _day_word_ru(n: int) -> str:
    n = abs(int(n))
    mod10 = n % 10
    mod100 = n % 100
    if mod10 == 1 and mod100 != 11:
        return "день"
    if mod10 in (2, 3, 4) and mod100 not in (12, 13, 14):
        return "дня"
    return "дней"


def referral_invite_benefit_line(settings: Settings | None) -> str:
    """
    Короткая строка выгоды для пушей «скоро / закончилась» (вариант 4 ТЗ).
    Дни — из trial-реф настроек (+1 вам / +3 другу), не из платной 3/7.
    """
    you = trial_referral_bonus_days(settings)
    friend = trial_referral_friend_bonus_days(settings)
    if you <= 0 and friend <= 0:
        return ""
    if you > 0 and friend > 0:
        return (
            f"👥 Приглашайте друзей: вам +{you} {_day_word_ru(you)} VPN, "
            f"другу +{friend} {_day_word_ru(friend)} бесплатно."
        )
    if you > 0:
        return f"👥 Приглашайте друзей: вам +{you} {_day_word_ru(you)} VPN."
    return f"👥 Приглашайте друзей: другу +{friend} {_day_word_ru(friend)} бесплатно."


def format_until_msk(paid_until: str) -> str:
    """«30 июля 2026, 23:59 по Москве» или fallback через format_datetime_display_msk."""
    dt = parse_paid_until_utc(paid_until)
    if dt is None:
        return format_datetime_display_msk(paid_until) if paid_until else "—"
    from zoneinfo import ZoneInfo

    local = dt.astimezone(ZoneInfo("Europe/Moscow"))
    months = (
        "",
        "января",
        "февраля",
        "марта",
        "апреля",
        "мая",
        "июня",
        "июля",
        "августа",
        "сентября",
        "октября",
        "ноября",
        "декабря",
    )
    return f"{local.day} {months[local.month]} {local.year}, {local.strftime('%H:%M')} по Москве"


def subscription_notify_kb(*, ended: bool = False) -> InlineKeyboardMarkup:
    """Кнопки по моменту: скоро — 💎, уже закончилась — 🚀."""
    extend = EXTEND_BTN_ENDED if ended else EXTEND_BTN_SOON
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=extend, callback_data=VPN_LEGAL_GATE_CALLBACK)],
            [InlineKeyboardButton(text=INVITE_BTN, callback_data="nav:ref")],
        ]
    )


_HAPP_AFTER_EXPIRE = (
    "Если в Happ VPN ещё «зелёный» — <b>обновите подписку</b> (потяните список вниз) "
    "или удалите профиль и добавьте ссылку заново."
)


def message_for_paid_kind(
    *,
    kind: str,
    paid_until: str,
    settings: Settings | None = None,
) -> str:
    p = esc(VPN_PRODUCT_NAME)
    until = esc(format_until_msk(paid_until))
    days = referral_bonus_days(settings)
    ref_hint = (
        f"Можно продлить оплату или пригласить друга (+{days} дн. к подписке)."
        if days > 0
        else "Можно продлить оплату в боте."
    )

    if kind == KIND_WELCOME:
        return (
            f"<b>✅ Подписка {p} оформлена</b>\n\n"
            f"Активна до <b>{until}</b>.\n"
            "Напомним за 3 дня до окончания.\n\n"
            f"{ref_hint}"
        )
    if kind == KIND_D7:
        return (
            f"<b>⏳ {p}</b>\n\n"
            f"Подписка активна до <b>{until}</b> (осталось около 7 дней).\n"
            f"{ref_hint}"
        )
    if kind == KIND_D3:
        return (
            f"<b>⏳ {p}</b>\n\n"
            f"Ваша подписка истекает через <b>3 дня</b> (до {until}).\n"
            "Продлите сейчас, чтобы не потерять доступ.\n\n"
            f"{ref_hint}"
        )
    if kind == KIND_D1:
        return (
            f"<b>⏳ {p}</b>\n\n"
            f"Завтра доступ закроется (до {until}).\n"
            "Оплатите или пригласите друга.\n\n"
            f"{ref_hint}"
        )
    if kind == KIND_H6:
        ref_line = referral_invite_benefit_line(settings)
        body = (
            "<b>⏳ Подписка скоро закончится</b>\n\n"
            "Ваш VPN закончится сегодня."
        )
        if ref_line:
            body += f"\n\n{ref_line}"
        return body
    if kind in (KIND_EXPIRED, KIND_D0_LEGACY):
        ref_line = referral_invite_benefit_line(settings)
        body = (
            "<b>🔴 Подписка завершилась</b>\n\n"
            "Доступ к VPN отключён.\n"
            f"{_HAPP_AFTER_EXPIRE}"
        )
        if ref_line:
            body += f"\n\n{ref_line}"
        return body
    return ""


def message_for_trial_kind(
    *,
    kind: str,
    paid_until: str,
    hours_left: float | None = None,
    settings: Settings | None = None,
) -> str:
    from bot.services.vpn_trial_copy import vpn_trial_period_phrase, vpn_trial_period_title

    until = esc(format_until_msk(paid_until))
    period = esc(vpn_trial_period_phrase(settings))
    title = esc(vpn_trial_period_title(settings) if settings else f"Пробный период: {period}")
    days = referral_bonus_days(settings)
    ref_hint = (
        f"Оформите тариф или пригласите друга (+{days} дн.)."
        if days > 0
        else "Оформите тариф, чтобы доступ продолжился."
    )
    ref_line = referral_invite_benefit_line(settings)

    if kind == KIND_TRIAL_WELCOME:
        return (
            f"<b>💛 {title}</b>\n\n"
            f"Тариф: <b>Пробный</b>. Активен до <b>{until}</b> "
            f"({period}).\n"
            "Напомним ближе к окончанию.\n\n"
            f"{ref_hint}"
        )
    if kind == KIND_TRIAL_D1:
        body = (
            "<b>⏳ Пробный период скоро закончится</b>\n\n"
            f"Ваш VPN закончится примерно через 1 день (до {until})."
        )
        if ref_line:
            body += f"\n\n{ref_line}"
        return body
    if kind in (KIND_TRIAL_H6, KIND_TRIAL_H3, KIND_TRIAL_H4):
        body = (
            "<b>⏳ Пробный период скоро закончится</b>\n\n"
            "Ваш VPN закончится сегодня."
        )
        if ref_line:
            body += f"\n\n{ref_line}"
        return body
    if kind == KIND_TRIAL_EXPIRED:
        body = (
            "<b>🔴 Пробный период завершился</b>\n\n"
            "Доступ к VPN отключён.\n"
            f"{_HAPP_AFTER_EXPIRE}"
        )
        if ref_line:
            body += f"\n\n{ref_line}"
        return body
    return ""


def hours_until_expiry(paid_until: str | None, *, now=None) -> float | None:
    from datetime import datetime, timezone

    end = parse_paid_until_utc(paid_until)
    if end is None:
        return None
    ref = now or datetime.now(timezone.utc).replace(microsecond=0)
    return (end - ref).total_seconds() / 3600.0


def paid_kind_for_timing(
    *,
    days_left: int | None,
    hours_left: float | None,
) -> str | None:
    """d7/d3/d1 по календарным дням; h6 вместо d0 в последние часы."""
    if days_left == 7:
        return KIND_D7
    if days_left == 3:
        return KIND_D3
    if days_left == 1:
        return KIND_D1
    if hours_left is not None and 4.0 < hours_left <= 7.0:
        return KIND_H6
    return None


def trial_kind_for_hours_left(hours_left: float | None) -> str | None:
    """~1 день: 20–28 ч; ~6 часов: 4–7 ч."""
    if hours_left is None:
        return None
    if 20.0 < hours_left <= 28.0:
        return KIND_TRIAL_D1
    if 4.0 < hours_left <= 7.0:
        return KIND_TRIAL_H6
    return None
