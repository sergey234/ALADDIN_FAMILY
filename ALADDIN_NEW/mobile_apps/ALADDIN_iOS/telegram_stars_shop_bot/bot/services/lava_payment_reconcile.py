"""Сверка оплат LAVA по API, если webhook не дошёл."""

from __future__ import annotations

import asyncio
import logging

from bot.config import Settings
from bot.db.database import connect
from bot.services import orders_repo
from bot.services.lava_api import fetch_invoice_status, lava_checkout_configured
from bot.services.partner_outbound import emit_order_status_changed
from bot.services.provider_mark_paid import mark_order_paid_idempotent
from bot.services.topup_lava_reconcile import reconcile_lava_pending_topups_once

_log = logging.getLogger(__name__)


async def reconcile_lava_pending_orders_once(settings: Settings, *, limit: int = 20) -> int:
    """Помечает paid заказы LAVA со status=success в API. Возвращает число обновлённых."""
    if not lava_checkout_configured(settings):
        return 0
    interval = int(settings.lava_reconcile_interval_seconds or 0)
    if interval <= 0:
        return 0

    conn = await connect(settings.database_path)
    marked = 0
    try:
        pending = await orders_repo.list_lava_pending_payment_orders(conn, limit=limit)
        expired = await orders_repo.list_lava_recent_expired_payment_orders(
            conn, lookback_hours=48, limit=limit
        )
        # pending first; skip duplicate ids from expired list
        seen: set[int] = set()
        rows: list = []
        for row in (*pending, *expired):
            oid = int(row["id"])
            if oid in seen:
                continue
            seen.add(oid)
            rows.append(row)
        for row in rows:
            order_id = int(row["id"])
            ext = str(row["invoice_last_external_id"] or "").strip()
            if not ext:
                continue
            data = await fetch_invoice_status(settings, order_id=order_id, invoice_id=ext)
            if not data:
                continue
            if str(data.get("status") or "").strip().lower() != "success":
                continue
            try:
                hook_amount = float(data.get("amount"))
            except (TypeError, ValueError):
                _log.warning("lava_reconcile_bad_amount order_id=%s data=%s", order_id, data)
                continue
            try:
                bap = float(row["balance_applied_rub"] or 0)
            except (KeyError, TypeError, ValueError):
                bap = 0.0
            if bap > 0.01:
                expected = float(orders_repo.amount_due_external(row))
            else:
                expected = float(row["rub_after_discounts"] or 0)
            if abs(hook_amount - expected) > 0.05:
                _log.warning(
                    "lava_reconcile_amount_mismatch order_id=%s expected=%s got=%s",
                    order_id,
                    expected,
                    hook_amount,
                )
                continue

            idem = f"lava:{ext}"
            await conn.execute("BEGIN IMMEDIATE")
            try:
                res = await mark_order_paid_idempotent(conn, order_id=order_id, idempotency_key=idem)
                if res.outcome == "ok":
                    await conn.commit()
                    marked += 1
                    _log.info(
                        "lava_reconcile_marked_paid order_id=%s invoice_id=%s from_status=%s",
                        order_id,
                        ext,
                        res.previous_status,
                    )
                    asyncio.create_task(
                        emit_order_status_changed(
                            db_path=settings.database_path,
                            order_id=order_id,
                            previous_status=res.previous_status or "pending_payment",
                            new_status="paid",
                        )
                    )
                    from bot.services.paid_order_hooks import schedule_post_paid_order_hooks

                    schedule_post_paid_order_hooks(settings, order_id)
                else:
                    await conn.rollback()
                    if res.outcome not in ("duplicate", "already_terminal"):
                        _log.info(
                            "lava_reconcile_skip order_id=%s outcome=%s",
                            order_id,
                            res.outcome,
                        )
            except Exception:
                await conn.rollback()
                raise
    finally:
        await conn.close()
    return marked


def schedule_lava_reconcile_once(settings: Settings) -> None:
    """Сразу проверить pending LAVA (после оплаты / открытие «Заказы»)."""
    asyncio.create_task(reconcile_lava_pending_orders_once(settings))


async def lava_payment_reconcile_loop(settings: Settings) -> None:
    interval = max(15, int(settings.lava_reconcile_interval_seconds or 30))
    while True:
        try:
            n = await reconcile_lava_pending_orders_once(settings)
            tn = await reconcile_lava_pending_topups_once(settings)
            if n or tn:
                _log.info("lava_reconcile_cycle orders=%s topups=%s", n, tn)
        except asyncio.CancelledError:
            raise
        except Exception:
            _log.exception("lava_reconcile_loop_iteration")
        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            raise
