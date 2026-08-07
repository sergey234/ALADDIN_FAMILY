from __future__ import annotations

import asyncio
import logging

from aiogram import Bot

from bot.config import Settings
from bot.db.database import connect
from bot.services import vpn_referral_extensions, vpn_referral_repo

_log = logging.getLogger(__name__)


async def run_vpn_referral_api_retry_sweep(settings: Settings) -> int:
    """Повторяет add-subscription-days для грантов с api_*_ok=0, пока attempts < max."""
    base = (settings.vpn_api_base_url or "").strip()
    secret = (settings.vpn_api_hmac_secret or "").strip()
    if not base or not secret:
        return 0
    conn = await connect(settings.database_path)
    n_done = 0
    try:
        rows = await vpn_referral_repo.list_grants_needing_vpn_api_retry(
            conn,
            max_attempts=settings.vpn_referral_api_max_attempts_per_side,
            limit=12,
        )
        for row in rows:
            try:
                await vpn_referral_extensions.retry_vpn_referral_grant_row(conn, row, settings)
                n_done += 1
            except Exception:
                _log.exception("vpn_referral_retry_row order_id=%s", row["order_id"])
    finally:
        await conn.close()
    if n_done:
        _log.info("vpn_referral_api_retry_sweep processed=%s", n_done)
    return n_done


async def vpn_referral_api_retry_loop(_bot: Bot, settings: Settings) -> None:
    interval = int(settings.vpn_referral_api_retry_interval_seconds)
    if interval <= 0:
        return
    interval = max(30, interval)
    while True:
        try:
            await run_vpn_referral_api_retry_sweep(settings)
        except asyncio.CancelledError:
            raise
        except Exception:
            _log.exception("vpn_referral_api_retry_loop_iteration")
        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            raise
