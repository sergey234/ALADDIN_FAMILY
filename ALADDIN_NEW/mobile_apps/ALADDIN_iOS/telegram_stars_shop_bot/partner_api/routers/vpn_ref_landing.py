"""vpn-12 + web: GET /r/{code} → web storefront cookie, optional Telegram deep link."""

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
    request: Request,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> RedirectResponse:
    raw = (code or "").strip()
    if not _CODE_RE.match(raw):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "invalid_code", "message": "Invalid referral code"},
        )
    # Prefer web checkout when enabled (get.aladdin-ai.ru or WEB_CHECKOUT_PUBLIC_ORIGIN).
    if bool(getattr(settings, "web_checkout_enabled", True)):
        origin = (getattr(settings, "web_checkout_public_origin", None) or "").strip().rstrip("/")
        if origin:
            resp = RedirectResponse(url=f"{origin}/?ref={raw}", status_code=302)
            # First-write-wins: keep the first invite cookie; later /r/ codes do not override.
            existing = (request.cookies.get("aim_ref") or "").strip()
            if not existing:
                resp.set_cookie(
                    key="aim_ref",
                    value=raw,
                    max_age=30 * 24 * 3600,
                    httponly=False,
                    samesite="lax",
                    secure=True,
                )
            return resp

    u = (settings.shop_bot_username or "").strip().lstrip("@")
    if not u:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "misconfigured", "message": "SHOP_BOT_USERNAME is not set"},
        )
    url = f"https://t.me/{u}?start=r-{raw}"
    return RedirectResponse(url=url, status_code=302)
