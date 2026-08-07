from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from bot.util_html import esc


def order_row_to_mapping(row: Mapping[str, Any] | Any) -> dict[str, Any]:
    """aiosqlite.Row → dict для ff_context / format block."""
    if row is None:
        return {}
    keys = getattr(row, "keys", None)
    if callable(keys):
        return {str(k): row[k] for k in row.keys()}  # type: ignore[union-attr]
    return dict(row)


@dataclass(frozen=True)
class AdminOrderFfContext:
    """Сводка для админ-клавиатуры и текста карточки заказа (автовыдача)."""

    status: str
    fulfillment_mode_raw: str | None
    attempt_count: int
    has_provider_ref: bool
    payment_method: str | None = None


def _is_manual_only(raw: str | None) -> bool:
    return str(raw or "").strip().lower() == "manual_only"


def ff_context_from_order_row(row: Mapping[str, Any] | Any | None) -> AdminOrderFfContext | None:
    if row is None:
        return None
    m = order_row_to_mapping(row)
    st = str(m.get("status") or "").strip().lower()
    try:
        ac = int(m.get("fulfillment_attempt_count") or 0)
    except (TypeError, ValueError):
        ac = 0
    ref = str(m.get("fulfillment_provider_ref") or "").strip()
    try:
        mode_raw = m["fulfillment_mode"]
    except (KeyError, IndexError, TypeError):
        mode_raw = None
    mode_s = None if mode_raw is None else str(mode_raw)
    pmt = m.get("payment_method")
    pm_str = None if pmt is None else str(pmt)
    return AdminOrderFfContext(
        status=st,
        fulfillment_mode_raw=mode_s,
        attempt_count=max(0, ac),
        has_provider_ref=bool(ref),
        payment_method=pm_str,
    )


def format_fulfillment_admin_block(row: Mapping[str, Any] | Any | None) -> str:
    """Доп. блок HTML для карточки заказа в админке (режим, ref, ошибка / выдача)."""
    if row is None:
        return ""
    row_m: Mapping[str, Any] = order_row_to_mapping(row)
    ctx = ff_context_from_order_row(row_m)
    if ctx is None:
        return ""

    if ctx.status == "completed":
        ref_raw = str(row_m.get("fulfillment_provider_ref") or "").strip()
        applied = str(row_m.get("fulfillment_applied_at") or row_m.get("updated_at") or "").strip()
        recipient = str(row_m.get("user_note") or "").strip() or "—"
        ref_disp = esc(ref_raw) if ref_raw else "—"
        applied_disp = esc(applied) if applied else "—"
        return (
            "\n\n<b>Выдача</b>\n"
            f"получатель: <code>{esc(recipient)}</code>\n"
            f"время: <code>{applied_disp}</code>\n"
            f"iStar ref: <code>{ref_disp}</code>"
        )

    if ctx.status == "expired":
        return ""

    mode_label = "manual_only" if _is_manual_only(ctx.fulfillment_mode_raw) else "auto"
    ref_raw = str(row_m.get("fulfillment_provider_ref") or "").strip()
    ref_disp = esc(ref_raw) if ref_raw else " - "
    err_raw = str(row_m.get("fulfillment_last_error") or "").strip()
    err_disp = esc(err_raw[:500]) if err_raw else " - "
    att = esc(str(ctx.attempt_count))
    lines = [
        "",
        "<b>Автовыдача</b>",
        f"режим: <code>{esc(mode_label)}</code> · попыток: <code>{att}</code>",
        f"провайдер ref: <code>{ref_disp}</code>",
        f"последняя ошибка: {err_disp}",
    ]
    return "\n".join(lines)


def fulfillment_controls_allowed(ctx: AdminOrderFfContext | None) -> bool:
    if ctx is None:
        return False
    return ctx.status in ("paid", "processing")
