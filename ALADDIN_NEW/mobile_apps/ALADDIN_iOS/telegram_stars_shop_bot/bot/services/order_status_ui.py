"""Только UI: подписи статусов и карточки списка заказов (без смены БД/API)."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from bot.util_html import esc

_CARD_RULE = "━━━━━━━━━━━━━━"

# (эмодзи+лейбл без слова «Статус», полный «Статус: …»)
_STATUS_UI: dict[str, tuple[str, str]] = {
    "completed": ("🟢", "Выполнен"),
    "processing": ("🟡", "В обработке"),
    "paid": ("⏳", "Ожидает выдачи"),
    "pending_payment": ("🔵", "Ожидает оплаты"),
    "expired": ("🔴", "Отменён"),
    "refunded": ("🔴", "Отменён"),
    "payment_disputed": ("🟡", "В обработке"),
    "cancelled": ("🔴", "Отменён"),
    "canceled": ("🔴", "Отменён"),
}


def order_status_ui_label(status: str | None) -> str:
    """Например: «🟢 Выполнен»."""
    key = (status or "").strip().lower()
    emoji, label = _STATUS_UI.get(key, ("⚪", key or "неизвестно"))
    return f"{emoji} {label}"


def order_status_line_html(status: str | None) -> str:
    """Строка карточки: «🟢 Статус: Выполнен»."""
    key = (status or "").strip().lower()
    emoji, label = _STATUS_UI.get(key, ("⚪", key or "неизвестно"))
    return f"{emoji} <b>Статус:</b> {esc(label)}"


def format_order_created_display(raw: str | None) -> str:
    """дд.мм.гггг чч:мм (МСК при наличии таймзоны, иначе как есть)."""
    s = (raw or "").strip()
    if not s:
        return "—"
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            # SQLite datetime('now') — UTC без tz.
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))
        local = dt.astimezone(ZoneInfo("Europe/Moscow"))
        return local.strftime("%d.%m.%Y %H:%M")
    except (TypeError, ValueError):
        return s[:16].replace("T", " ") if len(s) >= 16 else s


def order_list_card_html(
    *,
    order_id: int,
    product_title: str,
    rub_amount: float,
    created_at: str | None,
    status: str | None,
) -> str:
    title = (product_title or "Заказ").strip() or "Заказ"
    amt = f"{float(rub_amount):.0f}" if abs(float(rub_amount) - round(float(rub_amount))) < 0.005 else f"{float(rub_amount):.2f}"
    when = format_order_created_display(created_at)
    return (
        f"{_CARD_RULE}\n"
        f"<b>{esc(title)}</b>\n"
        f"📦 Заказ №{esc(order_id)}\n"
        f"💰 Сумма: {esc(amt)} ₽\n"
        f"📅 {esc(when)}\n"
        f"{order_status_line_html(status)}\n"
        f"{_CARD_RULE}"
    )
