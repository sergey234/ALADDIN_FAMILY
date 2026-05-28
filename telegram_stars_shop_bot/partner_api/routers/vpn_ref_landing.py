"""vpn-12: GET /r/{code} → Telegram deep link с тем же кодом, что в shop.db (vpn_referral_codes)."""

from __future__ import annotations

import re
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from bot.config import Settings
from partner_api.deps import get_settings

router = APIRouter(tags=["public"])

_CODE_RE = re.compile(r"^[A-Za-z0-9_-]{4,32}$")


def _settings_dep(request: Request) -> Settings:
    return get_settings(request)


@router.get("/r/{code}")
async def vpn_referral_redirect(
    code: str,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> RedirectResponse:
    raw = (code or "").strip()
    if not _CODE_RE.match(raw):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "invalid_code", "message": "Invalid referral code"},
        )
    u = (settings.shop_bot_username or "").strip().lstrip("@")
    if not u:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "misconfigured", "message": "SHOP_BOT_USERNAME is not set"},
        )
    url = f"https://t.me/{u}?start=r-{raw}"
    return RedirectResponse(url=url, status_code=302)
