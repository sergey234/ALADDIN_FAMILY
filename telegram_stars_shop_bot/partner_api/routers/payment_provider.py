from __future__ import annotations

import asyncio
import logging
from typing import Annotated, Any

import aiosqlite
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from bot.config import Settings
from bot.db.database import connect
from bot.services.hmac_util import verify_hmac_sha256_hex
from bot.services import orders_repo
from bot.services.partner_outbound import emit_order_status_changed
from bot.services.payment_events_repo import claim_provider_event
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
    Автоплатежи v1: провайдер (YooKassa / свой оркестратор) вызывает после успешной оплаты.
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
        cur = await conn.execute(
            "SELECT order_id FROM payment_provider_events WHERE idempotency_key = ?",
            (idem,),
        )
        dup = await cur.fetchone()
        if dup is not None:
            await conn.rollback()
            return {"ok": True, "duplicate": True, "order_id": int(dup["order_id"])}

        order = await orders_repo.get_order(conn, body.order_id)
        if order is None:
            await conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "not_found", "message": "Order not found"},
            )
        st = str(order["status"])
        if st in ("paid", "completed"):
            await conn.rollback()
            return {"ok": True, "already_terminal": True, "order_id": body.order_id, "status": st}

        if st != "pending_payment":
            await conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "invalid_state", "message": f"Order status {st} cannot transition to paid via webhook"},
            )

        try:
            await claim_provider_event(conn, idempotency_key=idem, order_id=body.order_id)
        except aiosqlite.IntegrityError:
            await conn.rollback()
            cur2 = await conn.execute(
                "SELECT order_id FROM payment_provider_events WHERE idempotency_key = ?",
                (idem,),
            )
            row2 = await cur2.fetchone()
            oid = int(row2["order_id"]) if row2 else body.order_id
            return {"ok": True, "duplicate": True, "order_id": oid}

        prev_status = st
        await orders_repo.update_status_no_commit(conn, body.order_id, "paid")
        new_status = "paid"
        order_id_out = body.order_id
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
    return {"ok": True, "order_id": body.order_id, "status": "paid"}
