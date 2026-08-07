"""Сверка оплат LAVA для пополнения баланса (TOPUP)."""

from __future__ import annotations

import logging

from bot.config import Settings
from bot.db.database import connect
from bot.services import balance_repo
from bot.services.lava_api import fetch_invoice_status, lava_checkout_configured
from bot.services.topup_payment_webhook import mark_topup_paid_from_provider

_log = logging.getLogger(__name__)


async def reconcile_lava_pending_topups_once(settings: Settings, *, limit: int = 20) -> int:
    if not lava_checkout_configured(settings):
        return 0
    if int(settings.lava_reconcile_interval_seconds or 0) <= 0:
        return 0

    conn = await connect(settings.database_path)
    marked = 0
    try:
        rows = await balance_repo.list_lava_pending_topups(conn, limit=limit)
        for row in rows:
            topup_id = int(row["id"])
            ext = str(row["external_invoice_id"] or "").strip()
            if not ext:
                continue
            data = await fetch_invoice_status(settings, invoice_id=ext)
            if not data:
                continue
            if str(data.get("status") or "").strip().lower() != "success":
                continue
            try:
                hook_amount = float(data.get("amount"))
            except (TypeError, ValueError):
                continue
            expected = float(row["amount_rub"])
            if abs(hook_amount - expected) > 0.05:
                _log.warning(
                    "topup_lava_reconcile_amount_mismatch topup_id=%s expected=%s got=%s",
                    topup_id,
                    expected,
                    hook_amount,
                )
                continue
            idem = f"lava:topup:{ext}"
            await conn.execute("BEGIN IMMEDIATE")
            try:
                res = await mark_topup_paid_from_provider(
                    conn,
                    settings,
                    topup_id=topup_id,
                    idempotency_key=idem,
                    expected_amount_rub=expected,
                )
                if res.outcome == "ok":
                    await conn.commit()
                    marked += 1
                    _log.info("topup_lava_reconcile_marked_paid topup_id=%s invoice_id=%s", topup_id, ext)
                else:
                    await conn.rollback()
            except Exception:
                await conn.rollback()
                raise
    finally:
        await conn.close()
    return marked
