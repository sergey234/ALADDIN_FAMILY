from __future__ import annotations

import logging
from typing import Annotated

import aiosqlite
from fastapi import APIRouter, Header, HTTPException, Request, Response, status

from bot.logutil import slog

from bot.config import Settings
from bot.services import orders_repo, users_repo
from bot.services.catalog import products_by_id
from bot.services.pricing import quote_product
from partner_api.deps import PartnerCtx, normalize_recipient, validate_idempotency_key
from partner_api.notify import notify_admins_new_api_order
from partner_api.schemas import OrderCreateBody, OrderCreateResponse, OrderListOut, OrderOut

router = APIRouter(tags=["orders"])
_log = logging.getLogger(__name__)


def _order_out(row: aiosqlite.Row) -> OrderOut:
    due = orders_repo.amount_due_external(row)
    try:
        ext = row["external_ref"]
    except (KeyError, IndexError):
        ext = None
    return OrderOut(
        id=int(row["id"]),
        status=str(row["status"]),
        product_id=str(row["product_id"]),
        product_title=str(row["product_title"]),
        payment_method=str(row["payment_method"]),
        rub_after_discounts=float(row["rub_after_discounts"] or 0),
        balance_applied_rub=float(row["balance_applied_rub"] or 0),
        amount_due_external_rub=due,
        user_note=row["user_note"],
        source=str(row["source"] or "telegram"),
        external_ref=ext,
        created_at=str(row["created_at"] or ""),
        updated_at=str(row["updated_at"] or ""),
    )


@router.post("/orders/create", response_model=OrderCreateResponse)
async def create_order(
    request: Request,
    ctx: PartnerCtx,
    body: OrderCreateBody,
    response: Response,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
) -> OrderCreateResponse:
    settings: Settings = request.app.state.settings
    products = request.app.state.products

    conn, client = ctx
    owner = int(client["owner_user_id"])
    api_client_id = int(client["id"])
    idem = validate_idempotency_key(idempotency_key)

    pmap = products_by_id(products)
    p = pmap.get(body.product_id)
    if not p:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "unknown_product", "message": f"Unknown product_id: {body.product_id}"},
        )

    cur = await conn.execute(
        "SELECT COUNT(*) AS c FROM orders WHERE user_id = ? AND status = 'completed'",
        (owner,),
    )
    cr = await cur.fetchone()
    is_first = int(cr["c"] if cr else 0) == 0
    q = quote_product(p, settings, is_first_order=is_first)
    u = await users_repo.get_user(conn, owner)
    referrer_id = int(u["referrer_id"]) if u and u["referrer_id"] is not None else None

    recipient = normalize_recipient(body.recipient)
    title = f"{p.emoji} {p.title}"

    try:
        oid, created = await orders_repo.create_order_partner_api(
            conn,
            owner_user_id=owner,
            api_client_id=api_client_id,
            idempotency_key=idem,
            external_ref=body.external_ref,
            product_id=p.id,
            product_title=title,
            payment_method=body.payment_method,
            usd_base=q.usd,
            rub_before=q.rub_list,
            rub_after=q.rub_final,
            referral_discount_rub=q.rub_referral_discount,
            wholesale_discount_rub=q.rub_wholesale_discount,
            referrer_id=referrer_id,
            user_note=recipient,
            settings=settings,
        )
    except ValueError as e:
        if str(e) == "order_pending_cap":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "code": "order_pending_cap",
                    "message": "Too many orders awaiting payment for this user",
                },
            ) from e
        raise

    row = await orders_repo.get_order(conn, oid)
    if not row:
        raise HTTPException(status_code=500, detail={"code": "internal", "message": "Order not found after create"})

    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    if created:
        slog(_log, "api_order_created", order_id=oid, owner_user_id=owner, api_client_id=api_client_id)
        await notify_admins_new_api_order(settings, oid)
    due = orders_repo.amount_due_external(row)
    return OrderCreateResponse(
        order_id=oid,
        created=created,
        status=str(row["status"]),
        rub_after_discounts=float(row["rub_after_discounts"] or 0),
        balance_applied_rub=float(row["balance_applied_rub"] or 0),
        amount_due_external_rub=due,
        recipient_normalized=recipient,
        payment_method=str(row["payment_method"]),
    )


@router.get("/orders/{order_id}", response_model=OrderOut)
async def get_order(request: Request, ctx: PartnerCtx, order_id: int) -> OrderOut:
    conn, client = ctx
    owner = int(client["owner_user_id"])
    row = await orders_repo.get_order_api_for_owner(conn, order_id, owner)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Order not found"},
        )
    return _order_out(row)


@router.get("/orders", response_model=OrderListOut)
async def list_orders(
    ctx: PartnerCtx,
    limit: int = 20,
    offset: int = 0,
) -> OrderListOut:
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=422, detail={"code": "validation_error", "message": "limit 1..100"})
    if offset < 0:
        raise HTTPException(status_code=422, detail={"code": "validation_error", "message": "offset >= 0"})
    conn, client = ctx
    owner = int(client["owner_user_id"])
    rows = await orders_repo.list_orders_api_for_owner(conn, owner, limit=limit, offset=offset)
    items = [_order_out(r) for r in rows]
    next_offset = (offset + limit) if len(rows) == limit else None
    return OrderListOut(items=items, next_offset=next_offset)
