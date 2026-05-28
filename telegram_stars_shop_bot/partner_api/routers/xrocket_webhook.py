from __future__ import annotations

import asyncio
import json
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from bot.config import Settings
from bot.db.database import connect
from bot.services import orders_repo
from bot.services.crypto_pay_payload import (
    decode_crypto_invoice_payload,
    verify_decoded_payload_against_order,
)
from bot.services.partner_outbound import emit_order_status_changed
from bot.services.provider_mark_paid import mark_order_paid_idempotent
from bot.services.xrocket_webhook_sig import verify_xrocket_webhook_signature
from partner_api.deps import get_settings

router = APIRouter(tags=["payments"])
_log = logging.getLogger(__name__)

_ROCKET_SIG_HEADER = "rocket-pay-signature"


def _settings_dep(request: Request) -> Settings:
    return get_settings(request)


def _header_signature(request: Request) -> str | None:
    for name, value in request.headers.items():
        if name.lower() == _ROCKET_SIG_HEADER:
            return value
    return None


def _verify_xrocket_body_strings(raw: bytes, signature: str | None, api_key: str) -> str | None:
    """Возвращает строку тела, прошедшую проверку подписи, или None."""
    try:
        primary = raw.decode("utf-8")
    except Exception:
        return None
    if verify_xrocket_webhook_signature(primary, signature, api_key):
        return primary
    try:
        obj = json.loads(primary)
        if not isinstance(obj, dict):
            return None
        compact = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)
        if compact != primary and verify_xrocket_webhook_signature(compact, signature, api_key):
            return compact
    except Exception:
        return None
    return None


@router.post("/payments/xrocket-webhook")
async def xrocket_pay_webhook(
    request: Request,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> dict[str, Any]:
    """
    Вебхук xRocket Pay (type = invoicePay). Подпись: rocket-pay-signature,
    hex(HMAC-SHA256(SHA256(XROCKET_PAY_API_KEY), UTF-8 тело)) — как xrocket-pay-api-sdk.
    """
    key = (settings.xrocket_pay_api_key or "").strip()
    if not key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "misconfigured", "message": "XROCKET_PAY_API_KEY is not set"},
        )

    raw = await request.body()
    sig = _header_signature(request)
    body_ok = _verify_xrocket_body_strings(raw, sig, key)
    if body_ok is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_signature", "message": "Invalid rocket-pay-signature"},
        )

    try:
        root = json.loads(body_ok)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": str(exc)},
        ) from exc
    if not isinstance(root, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Body must be a JSON object"},
        )

    wtype = str(root.get("type") or "").strip()
    if wtype != "invoicePay":
        return {"ok": True, "ignored": True, "type": wtype or None}

    data = root.get("data")
    if not isinstance(data, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Missing data"},
        )

    try:
        invoice_id = int(data.get("id"))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Invalid invoice id"},
        ) from None

    st = str(data.get("status") or "").strip().lower()
    if st != "paid":
        return {"ok": True, "ignored": True, "invoice_status": st or None}

    cur = str(data.get("currency") or "").strip().upper()
    if cur and cur != "USDT":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "asset_mismatch", "message": "Invoice currency must be USDT"},
        )

    payment = data.get("payment")
    if not isinstance(payment, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Missing payment"},
        )

    payload_raw = data.get("payload")
    if not isinstance(payload_raw, str) or not payload_raw.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Missing payload string"},
        )

    try:
        decoded = decode_crypto_invoice_payload(payload_raw.strip())
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": str(exc)},
        ) from exc

    order_id = decoded.order_id
    idem = f"xrocket:{invoice_id}"

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
            verify_decoded_payload_against_order(decoded, order)
        except ValueError as exc:
            await conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "payload_mismatch", "message": str(exc)},
            ) from exc

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
        _log.exception("xrocket_webhook_failed")
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
    return {"ok": True, "order_id": order_id, "status": "paid"}
