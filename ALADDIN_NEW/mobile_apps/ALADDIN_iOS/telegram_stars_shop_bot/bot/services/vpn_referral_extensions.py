from __future__ import annotations

import logging

import aiosqlite

from bot.config import Settings
from bot.services import vpn_api_client, vpn_referral_repo

logger = logging.getLogger(__name__)


async def apply_vpn_referral_extensions(
    conn: aiosqlite.Connection,
    grant: dict,
    settings: Settings,
) -> None:
    """После commit заказа: вызвать VPN API для друга и реферера; обновить флаги в shop.db."""
    oid = int(grant["order_id"])
    referred = int(grant["referred_user_id"])
    referrer = int(grant["referrer_user_id"])
    fd = int(grant["friend_days"])
    rd = int(grant["referrer_days"])

    friend_res: tuple[bool, str] | None = None
    referrer_res: tuple[bool, str] | None = None
    if fd > 0:
        f_ok, msg = await vpn_api_client.post_add_subscription_days(
            settings,
            telegram_user_id=referred,
            order_id=oid,
            days=fd,
            reason="vpn_referral_friend",
            idempotency_key=f"shop-vpn-ref:{oid}:friend:{referred}",
        )
        if not f_ok:
            logger.warning("vpn referral friend extend failed order=%s user=%s: %s", oid, referred, msg)
        friend_res = (f_ok, msg if not f_ok else "")
    else:
        # Trial-реф: другу уже выдан trial через provision — доп. extend не нужен.
        friend_res = (True, "")
    if rd > 0:
        r_ok, msg = await vpn_api_client.post_add_subscription_days(
            settings,
            telegram_user_id=referrer,
            order_id=oid,
            days=rd,
            reason="vpn_referral_referrer",
            idempotency_key=f"shop-vpn-ref:{oid}:referrer:{referrer}",
        )
        if not r_ok:
            logger.warning("vpn referral referrer extend failed order=%s user=%s: %s", oid, referrer, msg)
        referrer_res = (r_ok, msg if not r_ok else "")

    await vpn_referral_repo.record_grant_api_results(
        conn,
        order_id=oid,
        friend=friend_res,
        referrer=referrer_res,
    )


async def retry_vpn_referral_grant_row(
    conn: aiosqlite.Connection,
    grant_row: aiosqlite.Row,
    settings: Settings,
) -> None:
    """Повтор add-subscription-days для сторон гранта, где api_*_ok ещё 0 (те же Idempotency-Key)."""
    oid = int(grant_row["order_id"])
    referred = int(grant_row["referred_user_id"])
    referrer = int(grant_row["referrer_user_id"])
    fd = int(grant_row["friend_days"])
    rd = int(grant_row["referrer_days"])
    f_ok = int(grant_row["api_friend_ok"] or 0)
    r_ok = int(grant_row["api_referrer_ok"] or 0)

    friend_res: tuple[bool, str] | None = None
    referrer_res: tuple[bool, str] | None = None
    if fd > 0 and f_ok == 0:
        ok, msg = await vpn_api_client.post_add_subscription_days(
            settings,
            telegram_user_id=referred,
            order_id=oid,
            days=fd,
            reason="vpn_referral_friend",
            idempotency_key=f"shop-vpn-ref:{oid}:friend:{referred}",
        )
        if not ok:
            logger.warning("vpn referral retry friend order=%s user=%s: %s", oid, referred, msg)
        friend_res = (ok, msg if not ok else "")
    if rd > 0 and r_ok == 0:
        ok, msg = await vpn_api_client.post_add_subscription_days(
            settings,
            telegram_user_id=referrer,
            order_id=oid,
            days=rd,
            reason="vpn_referral_referrer",
            idempotency_key=f"shop-vpn-ref:{oid}:referrer:{referrer}",
        )
        if not ok:
            logger.warning("vpn referral retry referrer order=%s user=%s: %s", oid, referrer, msg)
        referrer_res = (ok, msg if not ok else "")

    if friend_res is not None or referrer_res is not None:
        await vpn_referral_repo.record_grant_api_results(
            conn,
            order_id=oid,
            friend=friend_res,
            referrer=referrer_res,
        )
