from __future__ import annotations

import re
import uuid
from collections.abc import AsyncGenerator
from typing import Annotated, Tuple

import aiosqlite
from fastapi import Depends, Header, HTTPException, Request, status

from bot.config import Settings
from bot.db.database import connect
from bot.services import api_clients_repo
from partner_api.ratelimit import PerClientRateLimiter

_USERNAME_RE = re.compile(r"^@?[a-zA-Z0-9_]{4,32}$")

_limiter = PerClientRateLimiter(max_hits=120, window_sec=60.0)


def normalize_recipient(raw: str) -> str:
    s = raw.strip()
    if not _USERNAME_RE.match(s):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Invalid recipient username"},
        )
    return s if s.startswith("@") else f"@{s}"


def validate_idempotency_key(value: str) -> str:
    s = value.strip()
    try:
        uuid.UUID(s)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "validation_error", "message": "Idempotency-Key must be a UUID"},
        )
    return s


def get_settings(request: Request) -> Settings:
    s = getattr(request.app.state, "settings", None)
    if not isinstance(s, Settings):
        raise HTTPException(status_code=500, detail={"code": "internal", "message": "Settings not initialized"})
    return s


async def partner_scope(
    request: Request,
    x_api_key: Annotated[str, Header(alias="X-API-KEY")],
) -> AsyncGenerator[Tuple[aiosqlite.Connection, aiosqlite.Row], None]:
    """
    Одно соединение SQLite на запрос: аутентификация, лимит, yield, затем last_used и close.
    """
    settings = get_settings(request)
    pepper = (settings.api_key_pepper or "").strip()
    if not pepper:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "misconfigured", "message": "API_KEY_PEPPER is not set on server"},
        )

    conn = await connect(settings.database_path)
    row: aiosqlite.Row | None = None
    try:
        row = await api_clients_repo.get_active_by_secret(conn, x_api_key.strip(), pepper)
        if not row:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "unauthorized", "message": "Invalid or revoked API key"},
            )
        cid = int(row["id"])
        if not _limiter.allow(cid):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={"code": "rate_limited", "message": "Too many requests for this API key"},
            )
        request.state.api_client_id = cid
        request.state.owner_user_id = int(row["owner_user_id"])
        yield conn, row
    finally:
        if row is not None:
            try:
                await api_clients_repo.touch_last_used(conn, int(row["id"]))
            except Exception:
                pass
        await conn.close()


PartnerCtx = Annotated[Tuple[aiosqlite.Connection, aiosqlite.Row], Depends(partner_scope)]
