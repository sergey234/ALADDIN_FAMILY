from __future__ import annotations

import secrets
from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, status

from bot.services import api_clients_repo
from partner_api.deps import PartnerCtx
from partner_api.schemas import WebhookSubscriptionGetOut, WebhookSubscriptionPutBody, WebhookSubscriptionPutOut

router = APIRouter(tags=["webhooks"])


def _require_https_url(url: str) -> str:
    u = url.strip()
    p = urlparse(u)
    if p.scheme != "https" or not p.netloc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "webhook_url must be https with a host"},
        )
    return u


@router.get("/webhooks/subscription", response_model=WebhookSubscriptionGetOut)
async def get_webhook_subscription(ctx: PartnerCtx) -> WebhookSubscriptionGetOut:
    conn, row = ctx
    cid = int(row["id"])
    full = await api_clients_repo.get_by_id(conn, cid)
    if full is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "not_found", "message": "Client"})
    url = ""
    sec = ""
    try:
        url = str(full["webhook_url"] or "")
    except (KeyError, IndexError, TypeError):
        pass
    try:
        sec = str(full["webhook_secret"] or "")
    except (KeyError, IndexError, TypeError):
        pass
    return WebhookSubscriptionGetOut(
        webhook_url=url.strip() or None,
        has_signing_secret=bool(sec.strip()),
    )


@router.put("/webhooks/subscription", response_model=WebhookSubscriptionPutOut)
async def put_webhook_subscription(body: WebhookSubscriptionPutBody, ctx: PartnerCtx) -> WebhookSubscriptionPutOut:
    conn, row = ctx
    cid = int(row["id"])
    full = await api_clients_repo.get_by_id(conn, cid)
    if full is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "not_found", "message": "Client"})

    existing_url = ""
    existing_secret = ""
    try:
        existing_url = str(full["webhook_url"] or "").strip()
    except (KeyError, IndexError, TypeError):
        pass
    try:
        existing_secret = str(full["webhook_secret"] or "").strip()
    except (KeyError, IndexError, TypeError):
        pass

    if body.webhook_url is not None and not str(body.webhook_url).strip():
        await api_clients_repo.set_partner_webhook(conn, client_id=cid, webhook_url=None, webhook_secret=None)
        return WebhookSubscriptionPutOut(webhook_url=None, has_signing_secret=False, signing_secret=None)

    if body.webhook_url is not None:
        url = _require_https_url(str(body.webhook_url))
    else:
        url = existing_url
        if not url.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"code": "validation_error", "message": "webhook_url required until a URL is configured"},
            )
    new_secret = existing_secret
    signing_out: str | None = None
    if body.rotate_secret or not existing_secret:
        new_secret = f"whsec_{secrets.token_urlsafe(24)}"
        signing_out = new_secret

    await api_clients_repo.set_partner_webhook(
        conn,
        client_id=cid,
        webhook_url=url,
        webhook_secret=new_secret,
    )
    return WebhookSubscriptionPutOut(
        webhook_url=url,
        has_signing_secret=bool(new_secret),
        signing_secret=signing_out,
    )
