from __future__ import annotations

import asyncio
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from bot.config import Settings
from bot.db.database import connect
from bot.services.hmac_util import verify_hmac_sha256_hex
from bot.services.partner_outbound import emit_order_status_changed
from bot.services.provider_mark_paid import mark_order_paid_idempotent
from partner_api.deps import get_settings

router = APIRouter(tags=["payments"])
_log = logging.getLogger(__name__)


def _parse_payment_sig_header(raw: str | None) -> str | None:
    if not raw:
        return None
    s = raw.strip()
    low = s.lower()
    if low.startswith("sha256="):
        return s[7:].strip()
    return s


class PaymentProviderWebhookBody(BaseModel):
    idempotency_key: str = Field(..., min_length=8, max_length=128)
    order_id: int = Field(..., gt=0)
    action: str = Field(default="mark_paid")


def _settings_dep(request: Request) -> Settings:
    return get_settings(request)


@router.post("/payments/provider-webhook")
async def payment_provider_webhook(
    request: Request,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> dict[str, Any]:
    """
    Автоплатежи v1: свой оркестратор (не LAVA) вызывает после успешной оплаты по договорённости.
    Подпись: hex HMAC-SHA256(PAYMENT_WEBHOOK_SECRET, raw_body) в заголовке X-Payment-Signature (опционально префикс sha256=).
    """
    secret = (settings.payment_webhook_secret or "").strip()
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "misconfigured", "message": "PAYMENT_WEBHOOK_SECRET is not set"},
        )
    raw = await request.body()
    sig_hdr = _parse_payment_sig_header(request.headers.get("X-Payment-Signature"))
    if not sig_hdr or not verify_hmac_sha256_hex(secret, raw, sig_hdr):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_signature", "message": "Invalid X-Payment-Signature"},
        )
    try:
        body = PaymentProviderWebhookBody.model_validate_json(raw.decode("utf-8"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": str(exc)},
        ) from exc
    if body.action != "mark_paid":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Unsupported action"},
        )
    idem = body.idempotency_key.strip()
    if len(idem) < 8 or len(idem) > 128:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "idempotency_key length 8..128"},
        )

    conn = await connect(settings.database_path)
    prev_status: str | None = None
    new_status: str | None = None
    order_id_out: int | None = None
    try:
        await conn.execute("BEGIN IMMEDIATE")
        res = await mark_order_paid_idempotent(conn, order_id=body.order_id, idempotency_key=idem)
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
        _log.exception("payment_provider_webhook_failed")
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
            from bot.services.vpn_payment_hook import schedule_vpn_provision_after_paid

            schedule_vpn_provision_after_paid(settings, order_id_out)
    return {"ok": True, "order_id": body.order_id, "status": "paid"}
