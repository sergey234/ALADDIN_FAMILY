from __future__ import annotations

import hashlib
import hmac
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from bot.config import Settings
from bot.db.database import connect
from bot.services import orders_repo
from bot.services.buyer_order_notify import (
    buyer_message_istar_failed,
    schedule_buyer_html,
)
from bot.services.istar_order_finalize import (
    run_completed_side_effects_and_emit,
    schedule_post_order_completed_notifications,
)
from bot.services.order_status import require_transition
from partner_api.deps import get_settings

router = APIRouter(tags=["payments"])
_log = logging.getLogger(__name__)

_SIG_HEADERS = (
    "x-apifragment-signature",
    "x-webhook-signature",
    "x-signature",
    "x-istar-signature",
)
_TS_HEADERS = (
    "x-apifragment-timestamp",
    "x-webhook-timestamp",
    "x-timestamp",
)


def _settings_dep(request: Request) -> Settings:
    return get_settings(request)


def _parse_body(raw: bytes) -> dict[str, Any]:
    import json

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
        if name.lower() in _SIG_HEADERS:
            return value
    return None


def _header_timestamp(request: Request) -> str | None:
    for name, value in request.headers.items():
        if name.lower() in _TS_HEADERS:
            s = (value or "").strip()
            if s:
                return s
    return None


def _normalize_signature_hex(raw: str | None) -> str | None:
    if not raw:
        return None
    s = raw.strip()
    if s.lower().startswith("sha256="):
        s = s[7:].strip()
    return s.strip().lower() or None


def verify_apifragment_signature(*, secret: str, raw_body: bytes, signature: str, timestamp: str | None) -> bool:
    """
    ApiFragment: HMAC-SHA256('<X-ApiFragment-Timestamp>.<body>', secret) → hex,
    header X-ApiFragment-Signature: sha256=<hex>.
    """
    sig = _normalize_signature_hex(signature)
    if not sig or not (secret or "").strip():
        return False
    ts = (timestamp or "").strip()
    if not ts:
        return False
    message = f"{ts}.".encode("utf-8") + raw_body
    expected = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()
    try:
        return hmac.compare_digest(expected, sig)
    except Exception:
        return False


def _extract_task_id(body: dict[str, Any]) -> str | None:
    for key in ("task_id", "id", "order_id", "external_id"):
        raw = body.get(key)
        if raw is not None and str(raw).strip():
            return str(raw).strip()
    order = body.get("order")
    if isinstance(order, dict):
        for key in ("id", "task_id", "order_id"):
            raw = order.get(key)
            if raw is not None and str(raw).strip():
                return str(raw).strip()
    data = body.get("data")
    if isinstance(data, dict):
        for key in ("task_id", "id"):
            raw = data.get(key)
            if raw is not None and str(raw).strip():
                return str(raw).strip()
    return None


def _extract_status(body: dict[str, Any]) -> str:
    for key in ("status", "event_type", "event", "type"):
        raw = body.get(key)
        if raw is not None and str(raw).strip():
            return str(raw).strip().lower()
    order = body.get("order")
    if isinstance(order, dict) and order.get("status"):
        return str(order["status"]).strip().lower()
    return ""


def _is_completed_event(status: str) -> bool:
    s = (status or "").strip().lower()
    return s in (
        "completed",
        "success",
        "done",
        "ok",
        "finished",
        "order.completed",
        "task.completed",
    )


def _is_failed_event(status: str) -> bool:
    s = (status or "").strip().lower()
    return s in (
        "failed",
        "error",
        "cancelled",
        "canceled",
        "fail",
        "order.failed",
        "task.failed",
    )


@router.post("/payments/apifragment-webhook")
async def apifragment_webhook(
    request: Request,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> dict[str, Any]:
    """
    Webhook ApiFragment (apifragment.online) после завершения task Stars/Premium.
    URL для кабинета: https://aladdin-ai.ru/v1/payments/apifragment-webhook
    """
    raw = await request.body()
    # Только APIFRAGMENT_WEBHOOK_SECRET — ISTAR_WEBHOOK_SECRET другой схемы/значения.
    secret = (settings.apifragment_webhook_secret or "").strip()
    sig = _header_signature(request)
    ts = _header_timestamp(request)
    if secret:
        if not sig or not verify_apifragment_signature(
            secret=secret, raw_body=raw, signature=sig, timestamp=ts
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "invalid_signature", "message": "Invalid webhook signature"},
            )
    elif sig:
        _log.warning("apifragment_webhook: signature present but APIFRAGMENT_WEBHOOK_SECRET empty — ignored")

    body = _parse_body(raw)
    task_id = _extract_task_id(body)
    if not task_id:
        return {"ok": True, "ignored": True, "reason": "no_task_id"}

    status_raw = _extract_status(body)
    conn = await connect(settings.database_path)
    try:
        row = await orders_repo.get_order_by_fulfillment_provider_ref(conn, task_id)
        if row is None:
            return {"ok": True, "ignored": True, "reason": "unknown_provider_ref", "task_id": task_id}

        order_id = int(row["id"])
        cur_status = str(row["status"] or "")

        if _is_completed_event(status_raw):
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
        elif _is_failed_event(status_raw):
            err = str(body.get("error_msg") or body.get("error") or status_raw or "apifragment_task_failed")[
                :2000
            ]
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
            return {"ok": True, "ignored": True, "status": status_raw or None, "task_id": task_id}
    except HTTPException:
        await conn.rollback()
        raise
    except Exception:
        await conn.rollback()
        _log.exception("apifragment_webhook_failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "internal", "message": "Webhook processing failed"},
        ) from None
    finally:
        await conn.close()

    await run_completed_side_effects_and_emit(
        settings, order_id=order_id, previous_status="processing"
    )
    schedule_post_order_completed_notifications(
        settings,
        order_id=order_id,
        user_id=int(row["user_id"]),
        source="auto",
    )

    return {"ok": True, "order_id": order_id, "status": "completed"}
