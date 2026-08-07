"""Немедленная автовыдача после перевода заказа в paid (дополнение к polling-воркеру)."""

from __future__ import annotations

import asyncio
import logging

from bot.config import Settings
from bot.services.auto_fulfill_runner import process_auto_fulfill_once
from bot.services.catalog import load_products

_log = logging.getLogger(__name__)


def schedule_auto_fulfill_after_paid(settings: Settings, order_id: int) -> None:
    """Fire-and-forget: один цикл воркера сразу после оплаты."""
    asyncio.create_task(_run_after_paid(settings=settings, order_id=order_id))


async def _run_after_paid(*, settings: Settings, order_id: int) -> None:
    if not settings.auto_fulfill_enabled:
        return
    try:
        products = load_products(settings.products_path)
        stats = await process_auto_fulfill_once(settings, products, limit=10)
        _log.info("auto_fulfill_after_paid order_id=%s stats=%s", order_id, stats)
    except Exception:
        _log.exception("auto_fulfill_after_paid_failed order_id=%s", order_id)
