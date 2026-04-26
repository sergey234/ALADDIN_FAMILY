from __future__ import annotations

from fastapi import APIRouter

from bot.services import balance_repo, users_repo
from partner_api.deps import PartnerCtx
from partner_api.schemas import UserProfileOut

router = APIRouter(tags=["profile"])


@router.get("/user/profile", response_model=UserProfileOut)
async def user_profile(ctx: PartnerCtx) -> UserProfileOut:
    conn, client = ctx
    owner = int(client["owner_user_id"])
    u = await users_repo.get_user(conn, owner)
    bal = await balance_repo.get_balance(conn, owner)
    ref_bal = float(u["ref_balance_rub"] or 0) if u else 0.0
    st = await users_repo.user_stats(conn, owner)
    raw = str(client["scopes"] or "")
    scopes = [s.strip() for s in raw.replace(";", ",").split(",") if s.strip()]
    if not scopes:
        scopes = ["orders:write", "orders:read", "profile:read", "topups:read", "topups:write"]
    return UserProfileOut(
        owner_user_id=owner,
        balance_rub=round(bal, 2),
        ref_balance_rub=round(ref_bal, 2),
        scopes=scopes,
        referral_invited_count=int(st["referral_invited_count"]),
        referral_buyers_completed_count=int(st["referral_buyers_completed_count"]),
        referral_commission_earned_rub=round(float(st["referral_commission_earned_rub"]), 2),
    )
