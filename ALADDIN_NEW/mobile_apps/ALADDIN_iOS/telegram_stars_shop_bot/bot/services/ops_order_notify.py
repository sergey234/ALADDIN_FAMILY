"""Ops-уведомления об успешной автовыдаче Stars/Premium."""

from __future__ import annotations

import logging

from bot.config import Settings
from bot.services.alerts import send_alert
from bot.util_html import esc

_log = logging.getLogger(__name__)


async def notify_ops_order_auto_completed(
    settings: Settings,
    *,
    order_id: int,
    user_id: int,
    product_title: str,
    recipient: str | None,
    provider_ref: str | None,
) -> None:
    if not settings.alerts_enabled or not settings.auto_fulfill_success_alerts_enabled:
        return
    oid = esc(order_id)
    title_esc = esc((product_title or "").strip() or "—")
    rcpt = esc((recipient or "").strip() or "—")
    ref = esc((provider_ref or "").strip() or "—")
    try:
        await send_alert(
            settings,
            severity="info",
            title="Автовыдача: заказ выдан",
            body=(
                f"order_id=#{oid} user_id={user_id}\n"
                f"товар: {title_esc}\n"
                f"получатель: {rcpt}\n"
                f"istar_ref={ref}\n"
                f"цепочка: pending_payment → paid → processing → completed"
            ),
            dedupe_key=f"auto_fulfill_completed:{order_id}",
        )
    except Exception:
        _log.exception("ops_order_auto_completed_alert_failed order_id=%s", order_id)
