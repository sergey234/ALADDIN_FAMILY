"""
vpn-11: после перевода заказа в paid — вызов aladdin-shop-vpn-api POST /internal/v1/provision.

Идемпотентность: Idempotency-Key = shop-vpn-prov:{order_id} (повтор вебхука не дублирует job).
Web orders: vpn_subject_id from accounts (may be synthetic); skip Telegram DM if no real TG.
"""

from __future__ import annotations

import asyncio
import logging
from bot.config import Settings
from bot.db.database import connect
from bot.services import accounts_repo, orders_repo, vpn_admin_support_repo, vpn_api_client
from bot.services.catalog import load_products, products_by_id
from bot.services.vpn_subscription_dates import compute_paid_until_after_purchase
from bot.services.vpn_post_purchase_delivery import (
    schedule_vpn_happ_delivery_after_paid,
    schedule_vpn_paid_ack,
    schedule_vpn_wg_delivery_after_paid,
)
from bot.services.vpn_referral_repo import is_vpn_order_row

logger = logging.getLogger(__name__)


def schedule_vpn_provision_after_paid(settings: Settings, order_id: int) -> None:
    asyncio.create_task(run_vpn_provision_after_paid(settings=settings, order_id=order_id))


async def run_vpn_provision_after_paid(*, settings: Settings, order_id: int) -> None:
    if not (settings.vpn_api_base_url or "").strip() or not (settings.vpn_api_hmac_secret or "").strip():
        return
    conn = await connect(settings.database_path)
    try:
        order = await orders_repo.get_order(conn, order_id)
        if order is None:
            return
        if str(order["status"] or "").strip().lower() != "paid":
            return
        if not is_vpn_order_row(order):
            return
        pmap = products_by_id(load_products(settings.products_path))
        p = pmap.get(str(order["product_id"] or ""))
        days = int(p.vpn_subscription_days) if p and p.vpn_subscription_days else 0
        if days <= 0:
            logger.warning(
                "vpn_payment_hook: order %s product %s has no vpn_subscription_days",
                order_id,
                order["product_id"],
            )
            return

        uid = int(order["user_id"])
        account_id = (order["account_id"] if "account_id" in order.keys() else None) or None
        account_id = str(account_id).strip() if account_id else ""
        acc = None
        if account_id:
            acc = await accounts_repo.get_account_by_id(conn, account_id)
        if acc is None:
            acc = await accounts_repo.get_account_by_vpn_subject(conn, uid)
        if acc is None and uid > 0:
            acc = await accounts_repo.ensure_account_for_telegram(conn, telegram_user_id=uid)
        vpn_subject = int(acc["vpn_subject_id"]) if acc else uid
        shop_aid = str(acc["account_id"]) if acc else (account_id or None)
        real_tg = acc.get("telegram_user_id") if acc else (uid if uid > 0 else None)
        if real_tg is not None:
            real_tg = int(real_tg)

        vpath = settings.resolved_vpn_db_path()
        existing = None
        if vpath is not None:
            existing = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, vpn_subject)
            if existing is None and real_tg and real_tg != vpn_subject:
                existing = await vpn_admin_support_repo.fetch_vpn_account_user_facing(vpath, real_tg)
        cur_paid = (existing or {}).get("paid_until") if existing else None
        until = compute_paid_until_after_purchase(current_paid_until=cur_paid, days=days)

        # Ack/DM only when a real Telegram user can receive messages.
        if real_tg and real_tg > 0:
            schedule_vpn_paid_ack(settings, order_id=order_id, telegram_user_id=real_tg)

        if existing and (existing.get("opaque_token") or "").strip():
            ok, msg = await vpn_api_client.post_extend(
                settings,
                telegram_user_id=vpn_subject,
                order_id=order_id,
                paid_until=until,
                idempotency_key=f"shop-vpn-ext:{order_id}",
                shop_account_id=shop_aid,
            )
        else:
            ok, msg = await vpn_api_client.post_provision(
                settings,
                telegram_user_id=vpn_subject,
                order_id=order_id,
                paid_until=until,
                idempotency_key=f"shop-vpn-prov:{order_id}",
                shop_account_id=shop_aid,
            )
        if not ok:
            logger.warning(
                "vpn_payment_hook: provision failed order=%s subject=%s: %s",
                order_id,
                vpn_subject,
                msg,
            )
            return
        from bot.services.vpn_order_finalize import finalize_vpn_order_completed

        await finalize_vpn_order_completed(settings, order_id)
        if real_tg and real_tg > 0:
            schedule_vpn_happ_delivery_after_paid(
                settings,
                order_id=order_id,
                telegram_user_id=real_tg,
            )
            schedule_vpn_wg_delivery_after_paid(
                settings,
                order_id=order_id,
                telegram_user_id=real_tg,
            )
    except Exception:
        logger.exception("vpn_payment_hook: order=%s", order_id)
    finally:
        await conn.close()
