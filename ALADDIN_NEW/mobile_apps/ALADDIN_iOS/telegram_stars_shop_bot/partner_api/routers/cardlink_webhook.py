from __future__ import annotations

import asyncio
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import PlainTextResponse

from bot.config import Settings
from bot.db.database import connect
from bot.services import orders_repo
from bot.services.cardlink_api import (
    cardlink_checkout_configured,
    parse_cardlink_order_id,
    verify_cardlink_chargeback_signature,
    verify_cardlink_payment_signature,
    verify_cardlink_refund_signature,
)
from bot.services.partner_outbound import emit_order_status_changed
from bot.services.provider_mark_paid import mark_order_paid_idempotent
from partner_api.deps import get_settings

router = APIRouter(tags=["payments"])
_log = logging.getLogger(__name__)

_PAID_STATUSES = frozenset({"SUCCESS", "OVERPAID"})


def _settings_dep(request: Request) -> Settings:
    return get_settings(request)


async def _form_dict(request: Request) -> dict[str, str]:
    form = await request.form()
    return {str(k): str(v) for k, v in form.items()}


async def _mark_paid_from_cardlink(
    settings: Settings,
    *,
    order_id: int,
    idem: str,
    hook_amount: float,
) -> dict[str, Any]:
    conn = await connect(settings.database_path)
    prev_status: str | None = None
    new_status: str | None = None
    order_id_out: int | None = None
    try:
        await conn.execute("BEGIN IMMEDIATE")
        order = await orders_repo.get_order(conn, order_id)
        if order is None:
            await conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "not_found", "message": "Order not found"},
            )
        try:
            bap = float(order["balance_applied_rub"] or 0)
        except (KeyError, TypeError, ValueError):
            bap = 0.0
        if bap > 0.01:
            expected = float(orders_repo.amount_due_external(order))
        else:
            expected = float(order["rub_after_discounts"] or 0)
        if abs(hook_amount - expected) > 0.05:
            await conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "amount_mismatch", "message": "Payment amount does not match order"},
            )

        res = await mark_order_paid_idempotent(conn, order_id=order_id, idempotency_key=idem)
        if res.outcome == "duplicate":
            await conn.rollback()
            return {"ok": True, "duplicate": True, "order_id": res.order_id}
        if res.outcome == "already_terminal":
            await conn.rollback()
            return {
                "ok": True,
                "already_terminal": True,
                "order_id": res.order_id,
                "status": res.previous_status or "paid",
            }
        if res.outcome == "not_found":
            await conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "not_found", "message": "Order not found"},
            )
        if res.outcome == "conflict":
            await conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "invalid_state",
                    "message": f"Order status {res.previous_status} cannot transition to paid via webhook",
                },
            )

        prev_status = res.previous_status
        new_status = res.new_status
        order_id_out = res.order_id
        await conn.commit()
    except HTTPException:
        await conn.rollback()
        raise
    except Exception:
        await conn.rollback()
        _log.exception("cardlink_webhook_mark_paid_failed order_id=%s", order_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "internal", "message": "Webhook processing failed"},
        ) from None
    finally:
        await conn.close()

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
    return {"ok": True, "order_id": order_id, "status": "paid"}


@router.post("/payments/cardlink-webhook")
async def cardlink_payment_webhook(
    request: Request,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> PlainTextResponse:
    """
    Cardlink payment postback (Result URL).
    Формат: application/x-www-form-urlencoded.
    Подпись: md5(OutSum:InvId:apiToken) → SignatureValue.
    """
    if not cardlink_checkout_configured(settings):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "misconfigured", "message": "Cardlink is not configured"},
        )
    token = (settings.cardlink_api_token or "").strip()
    fields = await _form_dict(request)

    inv_id = (fields.get("InvId") or "").strip()
    out_sum = (fields.get("OutSum") or "").strip()
    sig = (fields.get("SignatureValue") or "").strip()
    st = (fields.get("Status") or "").strip().upper()
    trs_id = (fields.get("TrsId") or "").strip() or "unknown"

    if not inv_id or not out_sum or not sig:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Missing InvId, OutSum or SignatureValue"},
        )
    if not verify_cardlink_payment_signature(token, out_sum=out_sum, inv_id=inv_id, signature_value=sig):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_signature", "message": "Invalid SignatureValue"},
        )

    if st not in _PAID_STATUSES:
        _log.info("cardlink_webhook_ignored_status inv_id=%s status=%s trs_id=%s", inv_id, st, trs_id)
        return PlainTextResponse("OK", status_code=200)

    order_id = parse_cardlink_order_id(inv_id)
    if order_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Invalid InvId"},
        )

    try:
        hook_amount = float(out_sum)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Invalid OutSum"},
        ) from None

    idem = f"cardlink:{trs_id}"
    if len(idem) < 8:
        idem = f"cardlink:{trs_id}:order:{order_id}"

    await _mark_paid_from_cardlink(
        settings,
        order_id=order_id,
        idem=idem,
        hook_amount=hook_amount,
    )
    return PlainTextResponse("OK", status_code=200)


@router.post("/payments/cardlink-refund")
async def cardlink_refund_webhook(
    request: Request,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> PlainTextResponse:
    """Cardlink Refund URL — логируем, отвечаем 200."""
    token = (settings.cardlink_api_token or "").strip()
    if not token:
        return PlainTextResponse("OK", status_code=200)
    fields = await _form_dict(request)
    sig = (fields.get("SignatureValue") or "").strip()
    amount = (fields.get("Amount") or "").strip()
    currency = (fields.get("Currency") or "").strip()
    bill_id = (fields.get("BillId") or "").strip()
    payment_id = (fields.get("PaymentId") or "").strip()
    refund_id = (fields.get("Id") or "").strip()
    inv_id = (fields.get("InvId") or "").strip()
    st = (fields.get("Status") or "").strip()

    if sig and amount and currency and bill_id and payment_id and refund_id:
        if not verify_cardlink_refund_signature(
            token,
            amount=amount,
            currency=currency,
            bill_id=bill_id,
            payment_id=payment_id,
            refund_id=refund_id,
            signature_value=sig,
        ):
            _log.warning("cardlink_refund_bad_signature inv_id=%s refund_id=%s", inv_id, refund_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "invalid_signature", "message": "Invalid SignatureValue"},
            )

    _log.info(
        "cardlink_refund_postback inv_id=%s status=%s amount=%s currency=%s bill_id=%s payment_id=%s id=%s",
        inv_id,
        st,
        amount,
        currency,
        bill_id,
        payment_id,
        refund_id,
    )
    return PlainTextResponse("OK", status_code=200)


@router.post("/payments/cardlink-chargeback")
async def cardlink_chargeback_webhook(
    request: Request,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> PlainTextResponse:
    """Cardlink Chargeback URL — логируем, отвечаем 200."""
    token = (settings.cardlink_api_token or "").strip()
    if not token:
        return PlainTextResponse("OK", status_code=200)
    fields = await _form_dict(request)
    sig = (fields.get("SignatureValue") or "").strip()
    bill_id = (fields.get("BillId") or "").strip()
    payment_id = (fields.get("PaymentId") or "").strip()
    chargeback_id = (fields.get("Id") or "").strip()
    inv_id = (fields.get("InvId") or "").strip()
    st = (fields.get("Status") or "").strip()

    if sig and bill_id and payment_id and chargeback_id:
        if not verify_cardlink_chargeback_signature(
            token,
            bill_id=bill_id,
            payment_id=payment_id,
            chargeback_id=chargeback_id,
            signature_value=sig,
        ):
            _log.warning("cardlink_chargeback_bad_signature inv_id=%s id=%s", inv_id, chargeback_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "invalid_signature", "message": "Invalid SignatureValue"},
            )

    _log.warning(
        "cardlink_chargeback_postback inv_id=%s status=%s bill_id=%s payment_id=%s id=%s",
        inv_id,
        st,
        bill_id,
        payment_id,
        chargeback_id,
    )
    return PlainTextResponse("OK", status_code=200)
