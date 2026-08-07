"""Общая финализация заказа после выдачи Stars/Premium (webhook, poller, админка)."""

from __future__ import annotations

import asyncio
import logging

from bot.config import Settings
from bot.db.database import connect
from bot.services import analytics_repo, orders_repo
from bot.services.admin_order_status_notify import schedule_notify_admins_order_completed
from bot.services.buyer_order_notify import (
    buyer_message_istar_completed,
    schedule_buyer_html,
)
from bot.services.order_flow import apply_completed_side_effects
from bot.services.ops_order_notify import notify_ops_order_auto_completed
from bot.services.partner_outbound import emit_order_status_changed
from bot.services.post_order_feedback import schedule_post_order_nps_prompt

_log = logging.getLogger(__name__)


def schedule_post_order_completed_notifications(
    settings: Settings,
    *,
    order_id: int,
    user_id: int,
    source: str = "auto",
) -> None:
    """Покупатель (всегда) + NPS (если включён) + админы + ops-алерт."""
    schedule_buyer_html(settings, user_id, buyer_message_istar_completed(order_id=order_id))
    schedule_post_order_nps_prompt(settings, user_id=user_id, order_id=order_id)
    schedule_notify_admins_order_completed(settings, order_id, source=source)

    async def _ops() -> None:
        conn = await connect(settings.database_path)
        try:
            row = await orders_repo.get_order(conn, order_id)
            if row is None:
                return
            await notify_ops_order_auto_completed(
                settings,
                order_id=order_id,
                user_id=int(row["user_id"]),
                product_title=str(row["product_title"] or ""),
                recipient=str(row["user_note"] or "") if row["user_note"] is not None else None,
                provider_ref=str(row["fulfillment_provider_ref"] or "") or None,
            )
        except Exception:
            _log.exception("post_completed_ops_notify_failed order_id=%s", order_id)
        finally:
            await conn.close()

    asyncio.create_task(_ops())


async def run_completed_side_effects_and_emit(
    settings: Settings,
    *,
    order_id: int,
    previous_status: str,
) -> None:
    conn = await connect(settings.database_path)
    try:
        await apply_completed_side_effects(conn, order_id, settings)
        try:
            row = await orders_repo.get_order(conn, order_id)
            if row is not None:
                await analytics_repo.log_event(
                    conn,
                    user_id=int(row["user_id"]),
                    event_type="order_completed",
                    meta={
                        "order_id": order_id,
                        "payment_method": str(row["payment_method"] or ""),
                    },
                )
        except Exception:
            pass
    finally:
        await conn.close()

    asyncio.create_task(
        emit_order_status_changed(
            db_path=settings.database_path,
            order_id=order_id,
            previous_status=previous_status,
            new_status="completed",
        )
    )
