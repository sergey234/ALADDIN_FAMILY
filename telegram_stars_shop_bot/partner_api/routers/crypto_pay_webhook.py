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
from bot.services.crypto_pay_webhook_sig import verify_crypto_pay_webhook_signature
from bot.services.partner_outbound import emit_order_status_changed
from bot.services.provider_mark_paid import mark_order_paid_idempotent
from partner_api.deps import get_settings

router = APIRouter(tags=["payments"])
_log = logging.getLogger(__name__)

_CRYPTO_SIG_HEADER = "crypto-pay-api-signature"


def _settings_dep(request: Request) -> Settings:
    return get_settings(request)


def _header_signature(request: Request) -> str | None:
    for name, value in request.headers.items():
        if name.lower() == _CRYPTO_SIG_HEADER:
            return value
    return None


def _parse_update(raw: bytes) -> dict[str, Any]:
    try:
        obj = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": str(exc)},
        ) from exc
    if not isinstance(obj, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Body must be a JSON object"},
        )
    return obj


def _verify_crypto_signature(raw: bytes, signature: str | None, token: str) -> bool:
    if verify_crypto_pay_webhook_signature(raw, signature, token):
        return True
    try:
        update = json.loads(raw.decode("utf-8"))
        if not isinstance(update, dict):
            return False
        alt = json.dumps(update, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        if alt == raw:
            return False
        return verify_crypto_pay_webhook_signature(alt, signature, token)
    except Exception:
        return False


@router.post("/payments/crypto-pay-webhook")
async def crypto_pay_webhook(
    request: Request,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> dict[str, Any]:
    """
    Вебхук Crypto Pay после оплаты счёта (update_type = invoice_paid).
    Подпись: hex(HMAC-SHA256(SHA256(CRYPTO_PAY_API_TOKEN), сырое тело POST)), заголовок crypto-pay-api-signature
    (как в pycryptopay-sdk; при расхождении пробуем компактный json.dumps от распарсенного объекта).
    """
    token = (settings.crypto_pay_api_token or "").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "misconfigured", "message": "CRYPTO_PAY_API_TOKEN is not set"},
        )

    raw = await request.body()
    sig = _header_signature(request)
    if not sig or not _verify_crypto_signature(raw, sig, token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_signature", "message": "Invalid crypto-pay-api-signature"},
        )

    update = _parse_update(raw)
    ut = str(update.get("update_type") or update.get("updateType") or "").strip().lower()
    if ut != "invoice_paid":
        return {"ok": True, "ignored": True, "update_type": ut or None}

    inv = update.get("payload")
    if not isinstance(inv, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Missing invoice payload"},
        )

    invoice_id_raw = inv.get("invoice_id", inv.get("invoiceId"))
    try:
        invoice_id = int(invoice_id_raw)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Invalid invoice_id"},
        ) from None

    st = str(inv.get("status") or "").strip().lower()
    if st != "paid":
        return {"ok": True, "ignored": True, "invoice_status": st or None}

    asset = str(inv.get("asset") or inv.get("Asset") or "").strip().upper()
    if asset and asset != "USDT":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "asset_mismatch", "message": "Invoice asset must be USDT"},
        )

    payload_raw = inv.get("payload") or inv.get("Payload")
    if not isinstance(payload_raw, str) or not payload_raw.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Missing invoice payload string"},
        )

    try:
        decoded = decode_crypto_invoice_payload(payload_raw.strip())
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": str(exc)},
        ) from exc

    order_id = decoded.order_id
    idem = f"cryptobot:{invoice_id}"

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
        _log.exception("crypto_pay_webhook_failed")
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
