"""Единый блок статуса VPN для профиля, главной VPN и управления."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from zoneinfo import ZoneInfo

from bot.config import Settings
from bot.services.vpn_subscription_dates import parse_paid_until_utc
from bot.util_html import esc

InactiveVariant = Literal["profile", "vpn_section"]

ACTIVE_STATUS_MARKER = "Активен"
CLOSED_STATUS_MARKER = "Доступ закрыт"

_VPN_CARD_RULE = "━━━━━━━━━━━━━━"


def format_remaining_dhm(end: datetime, *, now: datetime | None = None) -> str:
    """Полные дни + остаток часов + минут: «3 дня 5 часов 12 минут»."""
    now_u = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0)
    end_u = end.astimezone(timezone.utc).replace(microsecond=0)
    secs = int((end_u - now_u).total_seconds())
    if secs <= 0:
        return "0 дней 0 часов 0 минут"
    days = secs // 86400
    hours = (secs % 86400) // 3600
    minutes = (secs % 3600) // 60
    day_word = "день" if days == 1 else ("дня" if 2 <= days % 10 <= 4 and not 11 <= days % 100 <= 14 else "дней")
    hour_word = (
        "час"
        if hours == 1
        else ("часа" if 2 <= hours % 10 <= 4 and not 11 <= hours % 100 <= 14 else "часов")
    )
    min_word = (
        "минута"
        if minutes == 1
        else ("минуты" if 2 <= minutes % 10 <= 4 and not 11 <= minutes % 100 <= 14 else "минут")
    )
    return f"{days} {day_word} {hours} {hour_word} {minutes} {min_word}"


def format_remaining_days_short(end: datetime, *, now: datetime | None = None) -> str:
    """Короткий остаток для карточки VPN: «388 дней» или «5 часов»."""
    now_u = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0)
    end_u = end.astimezone(timezone.utc).replace(microsecond=0)
    secs = int((end_u - now_u).total_seconds())
    if secs <= 0:
        return "0 дней"
    days = secs // 86400
    if days >= 1:
        day_word = (
            "день"
            if days == 1
            else ("дня" if 2 <= days % 10 <= 4 and not 11 <= days % 100 <= 14 else "дней")
        )
        return f"{days} {day_word}"
    hours = max(1, secs // 3600)
    hour_word = (
        "час"
        if hours == 1
        else ("часа" if 2 <= hours % 10 <= 4 and not 11 <= hours % 100 <= 14 else "часов")
    )
    return f"{hours} {hour_word}"


def format_until_ddmmyyyy_hhmm(paid_raw: str) -> str:
    dt = parse_paid_until_utc(paid_raw)
    if dt is None:
        return "—"
    local = dt.astimezone(ZoneInfo("Europe/Moscow"))
    return local.strftime("%d.%m.%Y %H:%M")


def format_until_ddmmyyyy(paid_raw: str) -> str:
    dt = parse_paid_until_utc(paid_raw)
    if dt is None:
        return "—"
    local = dt.astimezone(ZoneInfo("Europe/Moscow"))
    return local.strftime("%d.%m.%Y")


def _tariff_label(row: dict[str, str]) -> str:
    kind = (row.get("account_kind") or "").strip().lower()
    if kind == "trial":
        return "Пробный"
    status = (row.get("status") or "").strip()
    if status == "vpn_expired":
        return "Закончился"
    return "Платный"


def _inactive_line(_variant: InactiveVariant = "profile") -> str:
    _ = _variant
    return f"🔴 <b>{CLOSED_STATUS_MARKER}</b>\nТариф: нет активной подписки"


def _vpn_section_active_card_html(*, remaining: str, until_disp: str) -> str:
    """Главный экран VPN после покупки: статус + мягкие плюсы, без техтерминов."""
    return (
        f"🟢 <b>{ACTIVE_STATUS_MARKER}</b>\n"
        f"⏳ Осталось: {esc(remaining)}\n"
        f"📅 До: {esc(until_disp)}\n"
        f"{_VPN_CARD_RULE}\n"
        "⚡ Высокая скорость\n"
        "🛡 Безопасное соединение\n"
        "📱 Все устройства\n"
        "🇷🇺 Стабильно работает в России\n\n"
        "💬 Всё управление — кнопками ниже."
    )


def vpn_user_status_block_html_from_row(
    row: dict[str, str] | None,
    *,
    inactive_variant: InactiveVariant = "profile",
    now: datetime | None = None,
) -> str:
    if not row:
        return _inactive_line(inactive_variant)

    status = (row.get("status") or "").strip()
    paid_raw = (row.get("paid_until") or "").strip()

    if status == "vpn_provisioning":
        return (
            "⏳ <b>Оформляется</b>\n"
            "<i>Обычно 2–5 минут. Ссылка и QR придут в чат.</i>"
        )

    end = parse_paid_until_utc(paid_raw) if paid_raw else None
    now_u = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    active = status == "vpn_active" and end is not None and end > now_u
    tariff = esc(_tariff_label(row))

    if not active:
        # Экран раздела VPN: коротко, как на витрине (без «действовала до»).
        if inactive_variant == "vpn_section":
            return _inactive_line(inactive_variant)
        until_disp = format_until_ddmmyyyy_hhmm(paid_raw) if paid_raw else "—"
        return (
            f"🔴 <b>{CLOSED_STATUS_MARKER}</b>\n"
            f"Тариф: {tariff}\n"
            f"Действовала до: {esc(until_disp)}"
        )

    if inactive_variant == "vpn_section":
        return _vpn_section_active_card_html(
            remaining=format_remaining_days_short(end, now=now_u),
            until_disp=format_until_ddmmyyyy(paid_raw),
        )

    remaining = format_remaining_dhm(end, now=now_u)
    until_disp = format_until_ddmmyyyy_hhmm(paid_raw)
    return (
        f"🟢 <b>{ACTIVE_STATUS_MARKER}</b>\n"
        f"Тариф: {tariff}\n"
        f"📅 Действует до: {esc(until_disp)}\n"
        f"⏳ Осталось: {esc(remaining)}"
    )


async def vpn_user_status_block_html(
    settings: Settings,
    telegram_user_id: int,
    *,
    inactive_variant: InactiveVariant = "profile",
    now: datetime | None = None,
) -> str:
    from bot.services import vpn_admin_support_repo

    vpath = settings.resolved_vpn_db_path()
    if vpath is None:
        return _inactive_line(inactive_variant)
    row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, telegram_user_id)
    return vpn_user_status_block_html_from_row(
        row,
        inactive_variant=inactive_variant,
        now=now,
    )


def vpn_soft_expiry_nudge_needed(row: dict[str, str] | None, *, now: datetime | None = None) -> bool:
    """Подсветить статус при ≤1 дне или expired — на существующем экране Управление VPN."""
    if not row:
        return False
    status = (row.get("status") or "").strip()
    if status == "vpn_expired":
        return True
    end = parse_paid_until_utc((row.get("paid_until") or "").strip())
    if end is None:
        return False
    now_u = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    return (end - now_u).total_seconds() <= 86400
