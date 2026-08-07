from __future__ import annotations

import asyncio
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from starlette.responses import PlainTextResponse

from bot.config import Settings
from bot.db.database import connect
from bot.services import orders_repo
from bot.services.ckassa_api import (
    CKASSA_DEMO_SECRET,
    CKASSA_DEMO_SHOP,
    ckassa_callback_signature,
    ckassa_checkout_configured,
    rub_to_kopecks,
)
from bot.services.partner_outbound import emit_order_status_changed
from bot.services.provider_mark_paid import mark_order_paid_idempotent
from partner_api.deps import get_settings

router = APIRouter(tags=["payments"])
_log = logging.getLogger(__name__)


def _settings_dep(request: Request) -> Settings:
    return get_settings(request)


async def _flat_request_params(request: Request) -> dict[str, str]:
    if request.method == "POST":
        ct = (request.headers.get("content-type") or "").lower()
        if "application/x-www-form-urlencoded" in ct or "multipart/form-data" in ct:
            form = await request.form()
            return {str(k): str(v) for k, v in form.multi_items()}
        if "application/json" in ct:
            try:
                raw = await request.json()
            except Exception:
                return {}
            if isinstance(raw, dict):
                return {str(k): str(v) for k, v in raw.items() if v is not None}
            return {}
    q = request.query_params
    return {str(k): str(v) for k, v in q.multi_items()}


def _shop_secret(settings: Settings) -> tuple[str, str]:
    if bool(settings.ckassa_test_mode):
        return CKASSA_DEMO_SHOP, CKASSA_DEMO_SECRET
    return (settings.ckassa_shop_token or "").strip(), (settings.ckassa_secret_key or "").strip()


async def _ckassa_payment_webhook_impl(request: Request, settings: Settings) -> PlainTextResponse:
    """
    Callback Ckassa (как WooCommerce notify_url): плоские поля regPayNum, result, orderId, amount, shop, signature.
    Ответ строго «success» или «fail» — текст/plain, как ожидает процессинг ЦК.
    """
    # Не 503/JSON: иначе PartnerRateLimitMiddleware шлёт WARNING в Telegram на каждый
    # зонд (мониторинг, браузер, ЦК). Ckassa ждёт text/plain success|fail при 200.
    if not bool(settings.ckassa_enabled):
        _log.info("ckassa_webhook noop: CKASSA_ENABLED is false")
        return PlainTextResponse("fail", status_code=200)
    if not bool(settings.ckassa_test_mode) and not ckassa_checkout_configured(settings):
        _log.warning("ckassa_webhook noop: CKASSA prod not configured (token/secret/callback)")
        return PlainTextResponse("fail", status_code=200)
    params = await _flat_request_params(request)
    try:
        order_id = int(str(params.get("orderId") or params.get("order_id") or "").strip())
    except ValueError:
        return PlainTextResponse("fail", status_code=200)

    reg_pay_num = str(params.get("regPayNum") or params.get("reg_pay_num") or "").strip()
    result_raw = str(params.get("result") or "").strip()
    result = result_raw.lower()
    shop_req = str(params.get("shop") or "").strip()
    sig_req = str(params.get("signature") or "").strip()
    err_msg = str(params.get("errorMsg") or params.get("error_msg") or "").strip()

    shop, secret = _shop_secret(settings)
    if not shop_req or shop_req != shop:
        _log.warning("ckassa_webhook_shop_mismatch order_id=%s", order_id)
        return PlainTextResponse("fail", status_code=200)

    try:
        amount_k = int(str(params.get("amount") or "0").strip())
    except ValueError:
        return PlainTextResponse("fail", status_code=200)

    if result != "success":
        _log.info(
            "ckassa_webhook_non_success order_id=%s result=%s err=%s",
            order_id,
            result,
            err_msg[:200],
        )
        return PlainTextResponse("success", status_code=200)

    expected_sig = ckassa_callback_signature(
        secret,
        shop,
        order_id=order_id,
        reg_pay_num=reg_pay_num,
        amount_kopecks=amount_k,
        result=result_raw,
    )
    if not sig_req or sig_req != expected_sig:
        _log.warning("ckassa_webhook_bad_signature order_id=%s", order_id)
        return PlainTextResponse("fail", status_code=200)

    conn = await connect(settings.database_path)
    prev_status: str | None = None
    new_status: str | None = None
    order_id_out: int | None = None
    try:
        await conn.execute("BEGIN IMMEDIATE")
        order = await orders_repo.get_order(conn, order_id)
        if order is None:
            await conn.rollback()
            return PlainTextResponse("fail", status_code=200)
        try:
            bap = float(order["balance_applied_rub"] or 0)
        except (KeyError, TypeError, ValueError):
            bap = 0.0
        if bap > 0.01:
            expected_rub = float(orders_repo.amount_due_external(order))
        else:
            expected_rub = float(order["rub_after_discounts"] or 0)
        expected_k = rub_to_kopecks(expected_rub)
        if int(amount_k) != int(expected_k):
            _log.warning(
                "ckassa_webhook_amount_mismatch order_id=%s expected_k=%s got_k=%s",
                order_id,
                expected_k,
                amount_k,
            )
            await conn.rollback()
            return PlainTextResponse("fail", status_code=200)

        idem = f"ckassa:{reg_pay_num or f'order:{order_id}'}"
        res = await mark_order_paid_idempotent(conn, order_id=order_id, idempotency_key=idem)
        if res.outcome == "duplicate":
            await conn.rollback()
            return PlainTextResponse("success", status_code=200)
        if res.outcome == "already_terminal":
            await conn.rollback()
            return PlainTextResponse("success", status_code=200)
        if res.outcome == "not_found":
            await conn.rollback()
            return PlainTextResponse("fail", status_code=200)
        if res.outcome == "conflict":
            await conn.rollback()
            return PlainTextResponse("fail", status_code=200)

        prev_status = res.previous_status
        new_status = res.new_status
        order_id_out = res.order_id
        await conn.commit()
    except Exception:
        await conn.rollback()
        _log.exception("ckassa_webhook_failed order_id=%s", order_id)
        return PlainTextResponse("fail", status_code=200)
    finally:
        await conn.close()

    if reg_pay_num and order_id_out is not None:
        conn2 = await connect(settings.database_path)
        try:
            await orders_repo.set_invoice_provider_metadata(
                conn2, order_id=int(order_id_out), provider="ckassa", external_id=reg_pay_num
            )
        finally:
            await conn2.close()

    if order_id_out is not None and prev_status is not None and new_status is not None:
        asyncio.create_task(
            emit_order_status_changed(
                db_path=settings.database_path,
                order_id=order_id_out,
                previous_status=prev_status,
                new_status=new_status,
            )
        )
        if new_status == "paid":
            from bot.services.paid_order_hooks import schedule_post_paid_order_hooks

            schedule_post_paid_order_hooks(settings, order_id_out)
    return PlainTextResponse("success", status_code=200)


@router.post("/payments/ckassa-webhook")
async def ckassa_payment_webhook_post(
    request: Request,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> PlainTextResponse:
    return await _ckassa_payment_webhook_impl(request, settings)


@router.get("/payments/ckassa-webhook", include_in_schema=False)
async def ckassa_payment_webhook_get(
    request: Request,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> PlainTextResponse:
    """ЦК может дергать callback GET query-параметрами (как WooCommerce wc-api)."""
    return await _ckassa_payment_webhook_impl(request, settings)
