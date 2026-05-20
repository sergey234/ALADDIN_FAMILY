# -*- coding: utf-8 -*-
"""Telegram @AladdinchatAI_bot — link codes, bot proxy to AI (tg-auth, tg-hermes-wire, tg-redact)."""
from __future__ import annotations

import logging
import os
from typing import Optional

import jwt
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

try:
    from app.auth import JWT_ALGORITHM, JWT_SECRET
except ImportError:
    JWT_SECRET = os.environ["JWT_SECRET"]
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

try:
    from security.services.telegram_link_store import (
        confirm_link,
        create_link_code,
        get_link,
        unlink,
    )
    from security.services.ai_prompt_gate import PIIPromptBlockedError, prepare_for_llm_prompt
    from security.api.routers.ai_assistant_router import (
        ChatMessageRequest,
        ChatMessageResponse,
        ai_assistant_chat,
        get_current_user,
    )
except ImportError:
    from telegram_link_store import confirm_link, create_link_code, get_link, unlink  # type: ignore
    from ai_prompt_gate import PIIPromptBlockedError, prepare_for_llm_prompt  # type: ignore
    from ai_assistant_router import (  # type: ignore
        ChatMessageRequest,
        ChatMessageResponse,
        ai_assistant_chat,
        get_current_user,
    )

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/telegram", tags=["Telegram AI Bot"])
security = HTTPBearer()


class LinkCodeResponse(BaseModel):
    code: str
    expires_in_sec: int = 600
    bot_username: str = "AladdinchatAI_bot"


class BotLinkRequest(BaseModel):
    telegram_user_id: int
    code: str
    telegram_username: Optional[str] = None


class BotUnlinkRequest(BaseModel):
    telegram_user_id: int


class BotChatRequest(BaseModel):
    telegram_user_id: int
    message: str = Field(..., min_length=1, max_length=2000)


def _verify_bot_secret(x_tg_bot_secret: Optional[str] = Header(None, alias="X-TG-Bot-Secret")) -> None:
    expected = os.getenv("TG_BOT_INTERNAL_SECRET", "").strip()
    if not expected or x_tg_bot_secret != expected:
        raise HTTPException(status_code=403, detail="Invalid bot secret")


@router.post("/link-code", response_model=LinkCodeResponse)
async def create_telegram_link_code(user: dict = Depends(get_current_user)) -> LinkCodeResponse:
    """iOS: Settings → Connect Telegram. Requires AI data sharing opt-in."""
    ai_opt_in = bool(user.get("payload", {}).get("ai_data_sharing", True))
    user_id = user.get("user_id") or "anonymous"
    code = create_link_code(aladdin_user_id=str(user_id), ai_opt_in=ai_opt_in)
    return LinkCodeResponse(code=code)


@router.post("/bot/link")
async def bot_confirm_link(
    body: BotLinkRequest,
    _: None = Depends(_verify_bot_secret),
) -> dict:
    link = confirm_link(
        code=body.code,
        telegram_user_id=body.telegram_user_id,
        telegram_username=body.telegram_username,
    )
    if not link:
        raise HTTPException(status_code=400, detail="Invalid or expired link code")
    return {"linked": True, "aladdin_user_id": link.aladdin_user_id, "ai_opt_in": link.ai_opt_in}


@router.post("/bot/unlink")
async def bot_unlink(
    body: BotUnlinkRequest,
    _: None = Depends(_verify_bot_secret),
) -> dict:
    ok = unlink(body.telegram_user_id)
    return {"unlinked": ok}


@router.post("/bot/chat", response_model=ChatMessageResponse)
async def bot_chat(
    body: BotChatRequest,
    _: None = Depends(_verify_bot_secret),
) -> ChatMessageResponse:
    """tg-hermes-wire: same stack as iOS AI assistant."""
    link = get_link(body.telegram_user_id)
    if not link:
        raise HTTPException(status_code=403, detail="Telegram account not linked")
    if not link.ai_opt_in:
        raise HTTPException(status_code=403, detail="AI data sharing not enabled for this account")

    try:
        prepare_for_llm_prompt(body.message, field_name="message")
    except PIIPromptBlockedError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    fake_user = {
        "user_id": link.aladdin_user_id,
        "subscription_level": "premium",
        "limits": {},
        "payload": {"sub": link.aladdin_user_id, "subscription": {"level": "premium"}},
    }
    req = ChatMessageRequest(message=body.message, context="general", user_id=link.aladdin_user_id)
    return await ai_assistant_chat(req, user=fake_user)
