from __future__ import annotations

import asyncio
import json
import logging

from aiogram import Bot

from bot.config import Settings
from bot.db.database import connect
from bot.services import admin_audit_repo
from bot.services.alerts import send_alert

_log = logging.getLogger(__name__)


async def run_break_glass_report(settings: Settings) -> None:
    lookback_h = max(1, int(settings.break_glass_report_lookback_hours))
    conn = await connect(settings.database_path)
    try:
        rows = await admin_audit_repo.list_recent_break_glass_actions(
            conn, lookback_hours=lookback_h, limit=200
        )
    finally:
        await conn.close()
    if not rows:
        return

    order_ids: list[int] = []
    for r in rows:
        try:
            payload = json.loads(str(r["payload_json"] or "{}"))
        except Exception:
            payload = {}
        try:
            oid = int(payload.get("order_id"))
            order_ids.append(oid)
        except Exception:
            continue

    sample = sorted(set(order_ids))[:30]
    _log.warning(
        "break_glass_report lookback_h=%s count=%s sample_order_ids=%s",
        lookback_h,
        len(rows),
        sample,
    )
    await send_alert(
        settings=settings,
        severity="warning",
        title="break-glass periodic report",
        body=f"lookback_h={lookback_h} count={len(rows)} sample_order_ids={sample}",
        dedupe_key=f"break_glass_report:{lookback_h}:{len(rows)}",
    )


async def break_glass_report_loop(_bot: Bot, settings: Settings) -> None:
    interval = int(settings.break_glass_report_interval_seconds)
    if interval <= 0:
        return
    interval = max(600, interval)
    while True:
        try:
            await run_break_glass_report(settings)
        except asyncio.CancelledError:
            raise
        except Exception:
            _log.exception("break_glass_report_loop_iteration")
        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            raise
