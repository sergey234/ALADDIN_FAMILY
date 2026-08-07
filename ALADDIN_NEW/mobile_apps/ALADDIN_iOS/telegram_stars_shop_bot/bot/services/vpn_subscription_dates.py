"""Расчёт paid_until при покупке и для напоминаний."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo


def parse_paid_until_utc(raw: str | None) -> datetime | None:
    if not raw or not str(raw).strip():
        return None
    s = str(raw).strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.replace(microsecond=0)
    except ValueError:
        return None


def compute_paid_until_after_purchase(*, current_paid_until: str | None, days: int) -> str:
    """max(now, текущий paid_until) + days — без потери оставшихся дней при продлении."""
    now = datetime.now(timezone.utc).replace(microsecond=0)
    base = now
    cur = parse_paid_until_utc(current_paid_until)
    if cur is not None and cur > base:
        base = cur
    return (base + timedelta(days=int(days))).replace(microsecond=0).isoformat()


async def preview_paid_until_iso(settings, telegram_user_id: int) -> str | None:
    """Текущий paid_until из vpn.db для расчёта «подписка до» на экране счёта."""
    from bot.services import vpn_admin_support_repo

    vpath = settings.resolved_vpn_db_path()
    if vpath is None:
        return None
    row = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, telegram_user_id)
    if not row:
        return None
    raw = str(row["paid_until"] or "").strip()
    return raw or None


def format_paid_until_display_msk(paid_until_iso: str) -> str:
    return format_datetime_display_msk(paid_until_iso, date_only=True)


def format_datetime_display_msk(iso: str, *, date_only: bool = False) -> str:
    dt = parse_paid_until_utc(iso)
    if dt is None:
        return iso[:10] if iso else "—"
    local = dt.astimezone(ZoneInfo("Europe/Moscow"))
    if date_only:
        return local.strftime("%d.%m.%Y")
    return local.strftime("%d.%m.%Y %H:%M") + " МСК"


def vpn_subscription_period_user_html(
    *,
    created_at: str = "",
    paid_until: str = "",
) -> str:
    """Срок подписки для экрана «Управление VPN»."""
    from bot.util_html import esc

    lines: list[str] = []
    start = format_datetime_display_msk(created_at) if (created_at or "").strip() else ""
    end = format_paid_until_display_msk(paid_until) if (paid_until or "").strip() else ""
    if start:
        lines.append(f"🕐 <b>Начало:</b> {esc(start)}")
    if end:
        lines.append(f"🕘 <b>Окончание:</b> {esc(end)}")
    days = days_until_expiry(paid_until)
    if days is not None:
        if days < 0:
            lines.append("⏳ <b>Осталось:</b> срок истёк")
        else:
            lines.append(f"⏳ <b>Осталось:</b> {days} дн.")
    if not lines:
        return ""
    return "\n".join(lines)


def days_until_expiry(paid_until: str | None, *, now: datetime | None = None) -> int | None:
    end = parse_paid_until_utc(paid_until)
    if end is None:
        return None
    ref = now or datetime.now(timezone.utc).replace(microsecond=0)
    delta = (end.date() - ref.date()).days
    return int(delta)
