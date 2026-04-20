from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from bot.config import Settings
from bot.services import balance_repo
from partner_api.deps import PartnerCtx
from partner_api.notify import notify_admins_new_topup
from partner_api.schemas import TopupCreateBody, TopupCreateResponse, TopupListOut, TopupOut

router = APIRouter(tags=["topups"])


@router.post("/topups/create", response_model=TopupCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_topup(request: Request, ctx: PartnerCtx, body: TopupCreateBody) -> TopupCreateResponse:
    settings: Settings = request.app.state.settings
    conn, client = ctx
    owner = int(client["owner_user_id"])
    tid = await balance_repo.create_topup_request(conn, user_id=owner, amount_rub=body.amount_rub)
    await notify_admins_new_topup(settings, tid, owner, body.amount_rub)
    return TopupCreateResponse(topup_id=tid, status="pending", amount_rub=body.amount_rub)


@router.get("/topups/{topup_id}", response_model=TopupOut)
async def get_topup(ctx: PartnerCtx, topup_id: int) -> TopupOut:
    conn, client = ctx
    owner = int(client["owner_user_id"])
    row = await balance_repo.get_topup_for_user(conn, topup_id, owner)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "not_found", "message": "Topup not found"},
        )
    return TopupOut(
        id=int(row["id"]),
        amount_rub=float(row["amount_rub"] or 0),
        status=str(row["status"]),
        created_at=str(row["created_at"] or ""),
    )


@router.get("/topups", response_model=TopupListOut)
async def list_topups(ctx: PartnerCtx, limit: int = 50) -> TopupListOut:
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=422, detail={"code": "validation_error", "message": "limit 1..100"})
    conn, client = ctx
    owner = int(client["owner_user_id"])
    rows = await balance_repo.list_topups_for_user(conn, owner, limit=limit)
    items = [
        TopupOut(id=int(r["id"]), amount_rub=float(r["amount_rub"] or 0), status=str(r["status"]), created_at=str(r["created_at"] or ""))
        for r in rows
    ]
    return TopupListOut(items=items)
