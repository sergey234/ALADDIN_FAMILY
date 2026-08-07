from __future__ import annotations

import asyncio
import json
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from bot.config import Settings
from bot.db.database import connect
from bot.services import orders_repo
from bot.services.hmac_util import verify_hmac_sha256_hex
from bot.services.payment_reference import parse_lava_payment_reference
from bot.services.partner_outbound import emit_order_status_changed
from bot.services.provider_mark_paid import mark_order_paid_idempotent
from bot.services.topup_payment_webhook import mark_topup_paid_from_provider
from partner_api.deps import get_settings

router = APIRouter(tags=["payments"])
_log = logging.getLogger(__name__)


def _normalize_auth_header(raw: str | None) -> str | None:
    if not raw:
        return None
    s = raw.strip()
    if s.lower().startswith("bearer "):
        s = s[7:].strip()
    if s.lower().startswith("sha256="):
        s = s[7:].strip()
    return s.strip() or None


def _lava_webhook_signature_candidates(request: Request) -> list[str]:
    """
    Lava SDK шлёт HMAC в Authorization; docs — в Signature.
    Пробуем оба (и редкие алиасы), без дублей.
    """
    keys = ("Authorization", "Signature", "X-Signature", "X-Api-Signature")
    out: list[str] = []
    seen: set[str] = set()
    for key in keys:
        norm = _normalize_auth_header(request.headers.get(key))
        if not norm:
            continue
        low = norm.lower()
        if low in seen:
            continue
        seen.add(low)
        out.append(norm)
    return out


def _settings_dep(request: Request) -> Settings:
    return get_settings(request)


@router.post("/payments/lava-webhook")
async def lava_payment_webhook(
    request: Request,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> dict[str, Any]:
    """
    Вебхук LAVA Business после успешной оплаты счёта.
    Подпись: HMAC-SHA256(LAVA_WEBHOOK_ADDITIONAL_SECRET, raw_body) в Authorization
    или Signature (см. https://dev.lava.ru/api-invoice-sign — «дополнительный ключ»).
    """
    secret = (settings.lava_webhook_additional_secret or "").strip()
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "misconfigured", "message": "LAVA_WEBHOOK_ADDITIONAL_SECRET is not set"},
        )
    raw = await request.body()
    candidates = _lava_webhook_signature_candidates(request)
    if not candidates or not any(verify_hmac_sha256_hex(secret, raw, sig) for sig in candidates):
        _log.info(
            "lava_webhook_auth_rejected has_authorization=%s has_signature=%s candidates=%s body_len=%s",
            bool(request.headers.get("Authorization")),
            bool(request.headers.get("Signature")),
            len(candidates),
            len(raw),
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_signature", "message": "Invalid Authorization"},
        )
    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": str(exc)},
        ) from exc
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Body must be a JSON object"},
        )
    st = str(payload.get("status") or "").lower()
    if st != "success":
        return {"ok": True, "ignored": True, "status": st or None}

    _log.info(
        "lava_webhook_received client=%s order_id=%s invoice_id=%s",
        request.client.host if request.client else "?",
        payload.get("order_id"),
        payload.get("invoice_id"),
    )

    ref = parse_lava_payment_reference(payload.get("order_id"))
    if ref is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Invalid order_id"},
        )
    kind, entity_id = ref

    invoice_id = str(payload.get("invoice_id") or "").strip() or "unknown"
    idem = f"lava:{invoice_id}"
    if len(idem) < 8:
        idem = f"lava:{invoice_id}:{kind}:{entity_id}"

    try:
        hook_amount = float(payload.get("amount"))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Invalid amount"},
        ) from None

    if kind == "topup":
        conn = await connect(settings.database_path)
        try:
            await conn.execute("BEGIN IMMEDIATE")
            res = await mark_topup_paid_from_provider(
                conn,
                settings,
                topup_id=entity_id,
                idempotency_key=idem,
                expected_amount_rub=hook_amount,
            )
            if res.outcome == "duplicate":
                await conn.rollback()
                return {"ok": True, "duplicate": True, "topup_id": res.topup_id}
            if res.outcome == "already_terminal":
                await conn.rollback()
                return {"ok": True, "already_terminal": True, "topup_id": res.topup_id, "status": "completed"}
            if res.outcome == "not_found":
                await conn.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"code": "not_found", "message": "Topup not found"},
                )
            if res.outcome == "conflict":
                await conn.rollback()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={"code": "invalid_state", "message": "Topup cannot be marked paid"},
                )
            await conn.commit()
        except HTTPException:
            await conn.rollback()
            raise
        except Exception:
            await conn.rollback()
            _log.exception("lava_webhook_topup_failed")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"code": "internal", "message": "Webhook processing failed"},
            ) from None
        finally:
            await conn.close()
        return {"ok": True, "topup_id": entity_id, "status": "completed"}

    order_id = entity_id

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
                detail={"code": "amount_mismatch", "message": "Invoice amount does not match order"},
            )

        pay_svc = str(payload.get("pay_service") or payload.get("service") or "").strip()
        if pay_svc:
            from bot.services.profit_compute import normalize_payment_rail

            await orders_repo.set_payment_rail(
                conn, order_id=order_id, payment_rail=normalize_payment_rail(pay_svc)
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
        _log.exception("lava_webhook_failed")
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
