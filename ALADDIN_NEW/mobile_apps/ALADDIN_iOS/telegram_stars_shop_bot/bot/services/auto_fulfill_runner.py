from __future__ import annotations

import asyncio
import logging
from typing import Any, Mapping

import aiosqlite
import httpx

from bot.config import Settings
from bot.db.database import connect
from bot.services import orders_repo
from bot.services.admin_order_status_notify import schedule_notify_admins_auto_fulfill_manual_needed
from bot.services.alerts import send_alert
from bot.services.auto_fulfill_policy import auto_fulfill_order_eligible
from bot.services.catalog import Product, products_by_id
from bot.services.fulfillment_recipient import parse_fulfillment_recipient_username
from bot.services.buyer_order_notify import (
    buyer_message_auto_create_failed,
    buyer_message_auto_submitted,
    schedule_buyer_html,
)
from bot.services.istar_circuit_breaker import (
    istar_circuit_is_open,
    istar_circuit_record_success,
    istar_circuit_record_transient_failure,
    istar_circuit_seconds_until_open,
)
from bot.services.istar_fulfill_client import IstarFulfillClient, IstarFulfillError
from bot.services.istar_fulfill_errors import (
    backoff_minutes_for_transient_count,
    istar_error_is_transient,
)
from bot.services.istar_wallet_monitor import (
    check_istar_ton_balance_for_auto_fulfill,
    notify_ops_istar_insufficient_on_create,
    notify_ops_istar_search_http_error,
)
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


async def _notify_istar_circuit_open(settings: Settings) -> None:
    if not settings.auto_fulfill_failure_alerts_enabled:
        return
    secs = istar_circuit_seconds_until_open()
    try:
        await send_alert(
            settings,
            severity="warning",
            title="iStar circuit breaker: автовыдача на паузе",
            body=(
                f"Серия 5xx от iStar — воркер пропускает batch ~{secs // 60} мин. "
                "Заказы в очереди; при долгом простое — ручная выдача."
            ),
            dedupe_key="istar_circuit_open",
        )
    except Exception:
        logger.exception("istar_circuit_alert_failed")


async def _handle_fulfill_error(
    conn: aiosqlite.Connection,
    settings: Settings,
    *,
    order_id: int,
    username: str | None,
    exc: BaseException,
    stats: dict[str, int],
    notify_search: bool = True,
) -> None:
    err_text = str(exc)[:2000]
    if istar_error_is_transient(exc):
        await orders_repo.revert_auto_fulfill_attempt_claim(conn, order_id)
        fresh = await orders_repo.get_order(conn, order_id)
        tc_next = int((fresh["fulfillment_transient_fail_count"] if fresh else 0) or 0) + 1
        backoff = backoff_minutes_for_transient_count(tc_next)
        tc = await orders_repo.schedule_auto_fulfill_transient_retry(
            conn,
            order_id,
            error_message=err_text,
            backoff_minutes=backoff,
        )
        opened = istar_circuit_record_transient_failure()
        if opened:
            asyncio.create_task(_notify_istar_circuit_open(settings))
        stats["transient_errors"] = stats.get("transient_errors", 0) + 1
        if notify_search and username:
            asyncio.create_task(
                notify_ops_istar_search_http_error(
                    settings,
                    order_id=order_id,
                    username=username,
                    exc=exc,
                )
            )
        logger.info(
            "auto_fulfill transient_error order=%s err=%s retry_min=%s transient_count=%s",
            order_id,
            exc,
            backoff_minutes_for_transient_count(tc),
            tc,
        )
        return

    await orders_repo.set_fulfillment_last_error(conn, order_id, err_text)
    stats["errors"] += 1
    if notify_search and username and isinstance(exc, IstarFulfillError):
        asyncio.create_task(
            notify_ops_istar_search_http_error(
                settings,
                order_id=order_id,
                username=username,
                exc=exc,
            )
        )
    schedule_notify_admins_auto_fulfill_manual_needed(
        settings,
        order_id=order_id,
        error_summary=err_text,
    )
    logger.info("auto_fulfill permanent_error order=%s err=%s", order_id, exc)


def _row_dict(row: aiosqlite.Row) -> dict[str, Any]:
    return {str(k): row[k] for k in row.keys()}


def _product_stars_quantity(product: Product) -> int | None:
    if product.stars is None:
        return None
    try:
        return int(product.stars)
    except (TypeError, ValueError):
        return None


def stars_quantity_for_fulfillment(row: Mapping[str, Any], product: Product) -> int | None:
    """Кол-во Stars для iStar: из заказа (stars_custom) или из каталога."""
    raw = row.get("stars_qty")
    if raw is not None:
        try:
            q = int(raw)
            if q > 0:
                return q
        except (TypeError, ValueError):
            pass
    q_prod = _product_stars_quantity(product)
    if q_prod is not None and q_prod > 0:
        return q_prod
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
        logger.warning("AUTO_FULFILL_ENABLED but ISTAR_API_KEY is empty - batch skipped")
        return stats

    if istar_circuit_is_open():
        stats["circuit_open"] = 1
        logger.warning(
            "auto_fulfill batch_skipped_circuit_open seconds_left=%s",
            istar_circuit_seconds_until_open(),
        )
        return stats

    balance_ok, balance_ton = await check_istar_ton_balance_for_auto_fulfill(settings, istar)
    if not balance_ok:
        logger.warning(
            "auto_fulfill batch_skipped_low_ton balance=%s threshold=%s",
            balance_ton,
            settings.istar_min_ton_balance_alert,
        )
        stats["low_ton_skip"] = 1
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

        stars_q = stars_quantity_for_fulfillment(_row_dict(row), product)
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
            await _handle_fulfill_error(
                conn,
                settings,
                order_id=order_id,
                username=username,
                exc=exc,
                stats=stats,
            )
            continue

        istar_circuit_record_success()
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
                    order_id=order_id,
                )
            else:
                ext_id = await istar.create_premium_order(
                    username=username,
                    recipient_hash=recipient_hash,
                    months=months or 0,
                    order_id=order_id,
                )
        except IstarFulfillError as exc:
            logger.warning("auto_fulfill create_failed order=%s err=%s", order_id, exc)
            reverted = await orders_repo.revert_processing_to_paid_after_auto_fulfill_failure(conn, order_id)
            if reverted:
                if istar_error_is_transient(exc):
                    await _handle_fulfill_error(
                        conn,
                        settings,
                        order_id=order_id,
                        username=username,
                        exc=exc,
                        stats=stats,
                        notify_search=False,
                    )
                else:
                    await orders_repo.set_fulfillment_last_error(conn, order_id, str(exc)[:2000])
                    stats["errors"] += 1
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
                asyncio.create_task(
                    notify_ops_istar_insufficient_on_create(settings, order_id=order_id, exc=exc)
                )
            else:
                await orders_repo.set_fulfillment_last_error(conn, order_id, str(exc)[:2000])
                stats["errors"] += 1
            continue

        istar_circuit_record_success()
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
