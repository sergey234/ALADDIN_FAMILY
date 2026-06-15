from __future__ import annotations

import asyncio
import json
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from bot.config import Settings
from bot.db.database import connect
from bot.services import analytics_repo, orders_repo
from bot.services.buyer_order_notify import (
    buyer_message_istar_completed,
    buyer_message_istar_failed,
    schedule_buyer_html,
)
from bot.services.hmac_util import verify_hmac_sha256_hex
from bot.services.order_flow import apply_completed_side_effects
from bot.services.order_status import require_transition
from bot.services.partner_outbound import emit_order_status_changed
from partner_api.deps import get_settings

router = APIRouter(tags=["payments"])
_log = logging.getLogger(__name__)

_SIG_HEADER = "x-istar-signature"


def _settings_dep(request: Request) -> Settings:
    return get_settings(request)


def _parse_body(raw: bytes) -> dict[str, Any]:
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


def _header_signature(request: Request) -> str | None:
    for name, value in request.headers.items():
        if name.lower() == _SIG_HEADER:
            return value
    return None


@router.post("/payments/istar-webhook")
async def istar_webhook(
    request: Request,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> dict[str, Any]:
    """
    Вебхук iStar после завершения или ошибки заказа выдачи (см. istar.fragmentapi.com/docs Webhooks).
    Подпись: hex(HMAC-SHA256(UTF-8 secret, сырое тело)) в заголовке X-iStar-Signature.
    """
    raw = await request.body()
    secret = (settings.istar_webhook_secret or "").strip()
    sig = _header_signature(request)
    if secret:
        if not sig or not verify_hmac_sha256_hex(secret, raw, sig):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "invalid_signature", "message": "Invalid X-iStar-Signature"},
            )
    elif sig:
        _log.warning("istar_webhook: signature present but ISTAR_WEBHOOK_SECRET empty — ignored")

    body = _parse_body(raw)
    event = str(body.get("event_type") or request.headers.get("X-iStar-Event") or "").strip().lower()
    order_wrap = body.get("order")
    if not isinstance(order_wrap, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Missing order object"},
        )
    ext_id_raw = order_wrap.get("id")
    if not isinstance(ext_id_raw, str) or not ext_id_raw.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Missing order.id"},
        )
    ext_id = ext_id_raw.strip()

    conn = await connect(settings.database_path)
    try:
        row = await orders_repo.get_order_by_fulfillment_provider_ref(conn, ext_id)
        if row is None:
            return {"ok": True, "ignored": True, "reason": "unknown_provider_ref", "external_order_id": ext_id}

        order_id = int(row["id"])
        cur_status = str(row["status"] or "")

        if event == "order.completed":
            if cur_status != "processing":
                return {"ok": True, "ignored": True, "order_id": order_id, "status": cur_status}
            await conn.execute("BEGIN IMMEDIATE")
            fresh = await orders_repo.get_order(conn, order_id)
            if fresh is None or str(fresh["status"]) != "processing":
                await conn.rollback()
                return {"ok": True, "ignored": True, "order_id": order_id}
            require_transition("processing", "completed")
            await orders_repo.update_status_no_commit(conn, order_id, "completed")
            await conn.commit()
        elif event == "order.failed":
            err = str(body.get("error") or order_wrap.get("status") or "istar_order_failed")[:2000]
            buyer_uid = int(row["user_id"])
            await conn.execute("BEGIN IMMEDIATE")
            await conn.execute(
                """
                UPDATE orders SET fulfillment_last_error = ?, updated_at = datetime('now')
                WHERE id = ? AND status = 'processing'
                """,
                (err, order_id),
            )
            await conn.commit()
            schedule_buyer_html(
                settings,
                buyer_uid,
                buyer_message_istar_failed(order_id=order_id, settings=settings, reason=err),
            )
            return {"ok": True, "order_id": order_id, "status": "processing", "recorded_error": True}
        else:
            return {"ok": True, "ignored": True, "event_type": event or None}
    except HTTPException:
        await conn.rollback()
        raise
    except Exception:
        await conn.rollback()
        _log.exception("istar_webhook_failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "internal", "message": "Webhook processing failed"},
        ) from None
    finally:
        await conn.close()

    order_id_out = order_id
    conn2 = await connect(settings.database_path)
    try:
        await apply_completed_side_effects(conn2, order_id_out, settings)
        try:
            await analytics_repo.log_event(
                conn2,
                user_id=int(row["user_id"]),
                event_type="order_completed",
                meta={"order_id": order_id_out, "payment_method": str(row["payment_method"] or "")},
            )
        except Exception:
            pass
    finally:
        await conn2.close()

    asyncio.create_task(
        emit_order_status_changed(
            db_path=settings.database_path,
            order_id=order_id_out,
            previous_status="processing",
            new_status="completed",
        )
    )

    try:
        buyer_uid = int(row["user_id"])
    except (TypeError, ValueError, KeyError, IndexError):
        buyer_uid = 0
    if buyer_uid:
        schedule_buyer_html(settings, buyer_uid, buyer_message_istar_completed(order_id=order_id_out))

    return {"ok": True, "order_id": order_id_out, "status": "completed"}
