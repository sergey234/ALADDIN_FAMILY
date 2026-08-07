"""Опрос статуса заказов iStar в processing (fallback если webhook не пришёл)."""

from __future__ import annotations

import asyncio
import logging

import httpx

from bot.config import Settings
from bot.db.database import connect
from bot.services import orders_repo
from bot.services.istar_fulfill_client import IstarFulfillClient, IstarFulfillError
from bot.services.istar_order_finalize import (
    run_completed_side_effects_and_emit,
    schedule_post_order_completed_notifications,
)
from bot.services.order_status import require_transition

_log = logging.getLogger(__name__)


async def _mark_completed_from_poll(
    settings: Settings,
    *,
    order_id: int,
    user_id: int,
) -> bool:
    conn = await connect(settings.database_path)
    try:
        await conn.execute("BEGIN IMMEDIATE")
        fresh = await orders_repo.get_order(conn, order_id)
        if fresh is None or str(fresh["status"]) != "processing":
            await conn.rollback()
            return False
        require_transition("processing", "completed")
        await orders_repo.update_status_no_commit(conn, order_id, "completed")
        await conn.commit()
    except Exception:
        await conn.rollback()
        _log.exception("istar_poll_mark_completed_failed order_id=%s", order_id)
        return False
    finally:
        await conn.close()

    await run_completed_side_effects_and_emit(
        settings, order_id=order_id, previous_status="processing"
    )
    schedule_post_order_completed_notifications(
        settings, order_id=order_id, user_id=user_id, source="istar_poll"
    )
    _log.info("istar_poll_completed order_id=%s", order_id)
    return True


async def run_istar_order_poll_once(settings: Settings) -> dict[str, int]:
    stats = {"candidates": 0, "completed": 0, "failed": 0, "skipped": 0, "errors": 0}
    if not IstarFulfillClient.is_configured(settings):
        return stats
    mins = max(1, int(settings.istar_order_poll_min_processing_minutes))
    conn = await connect(settings.database_path)
    try:
        rows = await orders_repo.list_processing_orders_for_istar_poll(
            conn, min_processing_minutes=mins, limit=20
        )
    finally:
        await conn.close()
    stats["candidates"] = len(rows)
    if not rows:
        return stats

    timeout = httpx.Timeout(45.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as http:
        istar = IstarFulfillClient(settings, http)
        for row in rows:
            order_id = int(row["id"])
            ext = str(row["fulfillment_provider_ref"] or "").strip()
            if not ext:
                stats["skipped"] += 1
                continue
            try:
                data = await istar.get_partner_order(ext)
                st = IstarFulfillClient.partner_order_status(data)
            except IstarFulfillError as exc:
                _log.info("istar_poll_fetch_failed order_id=%s err=%s", order_id, exc)
                stats["errors"] += 1
                continue
            if st == "completed":
                ok = await _mark_completed_from_poll(
                    settings, order_id=order_id, user_id=int(row["user_id"])
                )
                if ok:
                    stats["completed"] += 1
                else:
                    stats["skipped"] += 1
            elif st in ("failed", "error", "cancelled", "canceled"):
                err = str(data.get("error") or st)[:2000]
                conn2 = await connect(settings.database_path)
                try:
                    await orders_repo.set_fulfillment_last_error(conn2, order_id, err)
                finally:
                    await conn2.close()
                stats["failed"] += 1
            else:
                stats["skipped"] += 1
    return stats


async def istar_order_poll_loop(_bot, settings: Settings) -> None:
    interval = int(settings.istar_order_poll_interval_seconds)
    if interval <= 0:
        return
    while True:
        try:
            stats = await run_istar_order_poll_once(settings)
            if stats.get("completed") or stats.get("failed"):
                _log.info("istar_order_poll_cycle stats=%s", stats)
        except asyncio.CancelledError:
            raise
        except Exception:
            _log.exception("istar_order_poll_iteration")
        try:
            await asyncio.sleep(max(30, interval))
        except asyncio.CancelledError:
            raise
