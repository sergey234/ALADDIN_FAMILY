from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiosqlite
import httpx

from bot.config import Settings
from bot.db.database import connect
from bot.services import orders_repo
from bot.services.auto_fulfill_policy import auto_fulfill_order_eligible
from bot.services.catalog import Product, products_by_id
from bot.services.fulfillment_recipient import parse_fulfillment_recipient_username
from bot.services.buyer_order_notify import (
    buyer_message_auto_create_failed,
    buyer_message_auto_submitted,
    schedule_buyer_html,
)
from bot.services.alerts import send_alert
from bot.services.istar_fulfill_client import IstarFulfillClient, IstarFulfillError
from bot.services.order_status import require_transition
from bot.services.partner_outbound import emit_order_status_changed

logger = logging.getLogger(__name__)


async def notify_ops_auto_fulfill_create_failed(
    settings: Settings,
    *,
    order_id: int,
    username: str,
    exc: BaseException,
) -> None:
    """Ops-алерт при откате paid←processing после ошибки create у iStar (не блокирует воркер при вызове через task)."""
    if not settings.auto_fulfill_failure_alerts_enabled:
        return
    err_short = str(exc)[:800]
    try:
        await send_alert(
            settings,
            severity="warning",
            title="auto_fulfill create_failed (reverted to paid)",
            body=f"order_id={order_id} recipient=@{username} err={err_short}",
            dedupe_key=f"auto_fulfill_create_failed:{order_id}",
        )
    except Exception:
        logger.exception("auto_fulfill ops_alert_failed order=%s", order_id)


def _row_dict(row: aiosqlite.Row) -> dict[str, Any]:
    return {str(k): row[k] for k in row.keys()}


def _product_stars_quantity(product: Product) -> int | None:
    if product.stars is None:
        return None
    try:
        return int(product.stars)
    except (TypeError, ValueError):
        return None


def _product_months(product: Product) -> int | None:
    if product.duration_months is None:
        return None
    try:
        return int(product.duration_months)
    except (TypeError, ValueError):
        return None


async def process_auto_fulfill_batch(
    conn: aiosqlite.Connection,
    settings: Settings,
    products: list[Product],
    istar: IstarFulfillClient,
    *,
    limit: int = 10,
) -> dict[str, int]:
    """
    Берёт до `limit` заказов в paid без provider_ref, проверяет политику, атомарно резервирует попытку,
    вызывает iStar (search → paid→processing → create), сохраняет fulfillment_provider_ref.
    """
    stats: dict[str, int] = {"candidates": 0, "claimed": 0, "submitted": 0, "skipped": 0, "errors": 0}
    if not settings.auto_fulfill_enabled:
        return stats
    if not IstarFulfillClient.is_configured(settings):
        logger.warning("AUTO_FULFILL_ENABLED but ISTAR_API_KEY is empty — batch skipped")
        return stats

    pmap = products_by_id(products)
    rows = await orders_repo.list_orders_for_auto_fulfill(conn, limit=max(1, limit))
    stats["candidates"] = len(rows)

    for row in rows:
        order_id = int(row["id"])
        product_id = str(row["product_id"] or "")
        product = pmap.get(product_id)
        if product is None:
            stats["skipped"] += 1
            continue

        stars_q = _product_stars_quantity(product)
        months = _product_months(product)
        ok_elig, reason = auto_fulfill_order_eligible(
            _row_dict(row),
            settings,
            product_kind=product.kind,
            stars=stars_q,
            duration_months=months,
        )
        if not ok_elig:
            logger.debug("auto_fulfill skip order=%s reason=%s", order_id, reason)
            stats["skipped"] += 1
            continue

        username = parse_fulfillment_recipient_username(
            str(row["user_note"]) if row["user_note"] is not None else None
        )
        if not username:
            claimed = await orders_repo.claim_auto_fulfill_attempt_slot(
                conn,
                order_id=order_id,
                max_attempts=settings.auto_fulfill_max_attempts,
            )
            if claimed is None:
                stats["skipped"] += 1
                continue
            stats["claimed"] += 1
            await orders_repo.set_fulfillment_last_error(conn, order_id, "missing_recipient_username")
            stats["errors"] += 1
            continue

        claimed = await orders_repo.claim_auto_fulfill_attempt_slot(
            conn,
            order_id=order_id,
            max_attempts=settings.auto_fulfill_max_attempts,
        )
        if claimed is None:
            stats["skipped"] += 1
            continue
        stats["claimed"] += 1

        kind = (product.kind or "").strip().lower()
        try:
            if kind in ("stars", "gift"):
                if stars_q is None:
                    raise IstarFulfillError("internal_no_stars_on_product")
                recipient_hash = await istar.search_star_recipient(username=username, quantity=stars_q)
            elif kind == "premium":
                if months is None:
                    raise IstarFulfillError("internal_no_months_on_product")
                recipient_hash = await istar.search_premium_recipient(username=username, months=months)
            else:
                raise IstarFulfillError(f"unsupported_product_kind:{kind}")
        except IstarFulfillError as exc:
            logger.info("auto_fulfill search_failed order=%s err=%s", order_id, exc)
            await orders_repo.set_fulfillment_last_error(conn, order_id, str(exc)[:2000])
            stats["errors"] += 1
            continue

        prev_status = "paid"
        try:
            await conn.execute("BEGIN IMMEDIATE")
            fresh = await orders_repo.get_order(conn, order_id)
            if fresh is None or str(fresh["status"]) != "paid":
                await conn.rollback()
                stats["skipped"] += 1
                continue
            require_transition(str(fresh["status"]), "processing")
            await orders_repo.update_status_no_commit(conn, order_id, "processing")
            await conn.commit()
        except ValueError as exc:
            await conn.rollback()
            logger.info("auto_fulfill transition_denied order=%s err=%s", order_id, exc)
            await orders_repo.set_fulfillment_last_error(conn, order_id, str(exc)[:2000])
            stats["errors"] += 1
            continue
        except Exception:
            await conn.rollback()
            raise

        asyncio.create_task(
            emit_order_status_changed(
                db_path=settings.database_path,
                order_id=order_id,
                previous_status=prev_status,
                new_status="processing",
            )
        )

        buyer_uid = int(row["user_id"])

        try:
            if kind in ("stars", "gift"):
                ext_id = await istar.create_star_order(
                    username=username,
                    recipient_hash=recipient_hash,
                    quantity=stars_q or 0,
                )
            else:
                ext_id = await istar.create_premium_order(
                    username=username,
                    recipient_hash=recipient_hash,
                    months=months or 0,
                )
        except IstarFulfillError as exc:
            logger.warning("auto_fulfill create_failed order=%s err=%s", order_id, exc)
            await orders_repo.set_fulfillment_last_error(conn, order_id, str(exc)[:2000])
            reverted = await orders_repo.revert_processing_to_paid_after_auto_fulfill_failure(conn, order_id)
            if reverted:
                asyncio.create_task(
                    emit_order_status_changed(
                        db_path=settings.database_path,
                        order_id=order_id,
                        previous_status="processing",
                        new_status="paid",
                    )
                )
                schedule_buyer_html(
                    settings,
                    buyer_uid,
                    buyer_message_auto_create_failed(order_id=order_id, settings=settings),
                )
                asyncio.create_task(
                    notify_ops_auto_fulfill_create_failed(
                        settings, order_id=order_id, username=username, exc=exc
                    )
                )
            stats["errors"] += 1
            continue

        await orders_repo.set_fulfillment_provider_ref(conn, order_id, ext_id)
        stats["submitted"] += 1
        schedule_buyer_html(settings, buyer_uid, buyer_message_auto_submitted(order_id=order_id))

    return stats


async def process_auto_fulfill_once(
    settings: Settings,
    products: list[Product],
    *,
    limit: int = 10,
) -> dict[str, int]:
    """Один цикл: своё соединение БД и httpx-клиент."""
    conn = await connect(settings.database_path)
    try:
        timeout = httpx.Timeout(45.0, connect=10.0)
        async with httpx.AsyncClient(timeout=timeout) as http:
            istar = IstarFulfillClient(settings, http)
            return await process_auto_fulfill_batch(conn, settings, products, istar, limit=limit)
    finally:
        await conn.close()
