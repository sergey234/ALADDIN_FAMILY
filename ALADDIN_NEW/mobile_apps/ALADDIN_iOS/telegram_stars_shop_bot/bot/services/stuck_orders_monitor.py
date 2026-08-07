from __future__ import annotations

import asyncio
import logging

from aiogram import Bot

from bot.config import Settings
from bot.db.database import connect
from bot.services.alerts import send_alert
from bot.services import orders_repo

_log = logging.getLogger(__name__)


def _filter_alert_order_ids(settings: Settings, ids: list[int]) -> list[int]:
    ignore = settings.parsed_stuck_alert_ignore_order_ids()
    if not ignore:
        return ids
    return [i for i in ids if int(i) not in ignore]


async def run_stuck_paid_check(settings: Settings) -> None:
    hours = int(settings.stuck_paid_alert_hours)
    if hours <= 0:
        return
    conn = await connect(settings.database_path)
    try:
        ids = await orders_repo.list_order_ids_stuck_paid_or_processing(
            conn, hours_without_update=hours, limit=200
        )
    finally:
        await conn.close()
    ids = _filter_alert_order_ids(settings, ids)
    if not ids:
        return
    _log.warning(
        "stuck_paid_orders hours=%s count=%s sample_ids=%s",
        hours,
        len(ids),
        ids[:30],
    )
    await send_alert(
        settings=settings,
        severity="warning",
        title="stuck paid orders detected",
        body=f"hours={hours} count={len(ids)} sample_ids={ids[:30]}",
        dedupe_key=f"stuck_paid_orders:{hours}",
        cooldown_seconds=int(settings.stuck_alert_cooldown_seconds),
    )


async def run_stuck_paid_fast_check(settings: Settings) -> None:
    mins = int(settings.stuck_paid_fast_alert_minutes)
    if mins <= 0:
        return
    conn = await connect(settings.database_path)
    try:
        ids = await orders_repo.list_order_ids_stuck_paid_only(
            conn, minutes_without_update=mins, limit=200
        )
    finally:
        await conn.close()
    ids = _filter_alert_order_ids(settings, ids)
    if not ids:
        return
    _log.warning(
        "stuck_paid_only_orders minutes=%s count=%s sample_ids=%s",
        mins,
        len(ids),
        ids[:30],
    )
    await send_alert(
        settings=settings,
        severity="warning",
        title="stuck paid orders (no processing)",
        body=f"minutes={mins} count={len(ids)} sample_ids={ids[:30]}",
        dedupe_key=f"stuck_paid_only_orders:{mins}",
        cooldown_seconds=int(settings.stuck_alert_cooldown_seconds),
    )


async def run_stuck_processing_check(settings: Settings) -> None:
    mins = int(settings.stuck_processing_alert_minutes)
    if mins <= 0:
        return
    conn = await connect(settings.database_path)
    try:
        ids = await orders_repo.list_order_ids_stuck_processing_only(
            conn, minutes_without_update=mins, limit=200
        )
    finally:
        await conn.close()
    ids = _filter_alert_order_ids(settings, ids)
    if not ids:
        return
    _log.warning(
        "stuck_processing_orders minutes=%s count=%s sample_ids=%s",
        mins,
        len(ids),
        ids[:30],
    )
    await send_alert(
        settings=settings,
        severity="warning",
        title="stuck processing orders detected",
        body=f"minutes={mins} count={len(ids)} sample_ids={ids[:30]}",
        dedupe_key=f"stuck_processing_orders:{mins}",
        cooldown_seconds=int(settings.stuck_alert_cooldown_seconds),
    )


async def stuck_paid_orders_loop(_bot: Bot, settings: Settings) -> None:
    """Периодически: paid без processing (мин), paid/processing (часы), processing (мин)."""
    if (
        int(settings.stuck_paid_alert_hours) <= 0
        and int(settings.stuck_processing_alert_minutes) <= 0
        and int(settings.stuck_paid_fast_alert_minutes) <= 0
    ):
        return
    interval = max(300, int(settings.stuck_paid_check_interval_seconds))
    while True:
        try:
            await run_stuck_paid_fast_check(settings)
            await run_stuck_paid_check(settings)
            await run_stuck_processing_check(settings)
        except asyncio.CancelledError:
            raise
        except Exception:
            _log.exception("stuck_paid_orders_loop_iteration")
        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            raise
