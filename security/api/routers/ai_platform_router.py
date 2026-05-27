# -*- coding: utf-8 -*-
"""
AI Platform API — shared infrastructure for ALADDIN Family + Adult apps.

Not bundled in ALADDIN iOS UI for adult-only features; backend ready day one.

Endpoints:
  POST /api/ai/platform/chat
  GET  /api/ai/platform/threads
  POST /api/ai/platform/threads
  GET  /api/ai/platform/profile
  PUT  /api/ai/platform/profile
  GET  /api/ai/platform/capabilities
  POST /api/ai/voice/ephemeral-token
"""

from __future__ import annotations

import logging
import os
import secrets
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import jwt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(tags=["AI Platform"])
platform_router = APIRouter(prefix="/api/ai/platform", tags=["AI Platform"])
voice_router = APIRouter(prefix="/api/ai/voice", tags=["AI Voice"])

security = HTTPBearer()

try:
    from app.auth import JWT_SECRET, JWT_ALGORITHM
except ImportError:
    JWT_SECRET = os.environ["JWT_SECRET"]
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

try:
    from security.services.ai_platform.config import AppId, ChatMode, ContentPolicy
    from security.services.ai_platform.policy_engine import evaluate_request_policy
    from security.services.ai_platform.orchestrator import OrchestratorRequest, run_orchestrator
    from security.services.ai_platform.capabilities import get_platform_capabilities
    from security.api.routers.ai_assistant_router import (
        ChatMessageRequest,
        ai_assistant_chat,
        get_current_user,
    )
except ImportError:
    from ai_platform.config import AppId, ChatMode, ContentPolicy  # type: ignore
    from ai_platform.policy_engine import evaluate_request_policy  # type: ignore
    from ai_platform.orchestrator import OrchestratorRequest, run_orchestrator  # type: ignore
    from ai_assistant_router import ChatMessageRequest, ai_assistant_chat, get_current_user  # type: ignore
    from capabilities import get_platform_capabilities  # type: ignore

# In-memory MVP stores (replace with DB)
_threads: Dict[str, List[Dict[str, Any]]] = {}
_profiles: Dict[str, Dict[str, Any]] = {}


def _platform_user(user: dict) -> dict:
    payload = user.get("payload") or {}
    return {
        **user,
        "app_id": payload.get("app_id", AppId.ALADDIN_FAMILY.value),
        "content_policy": payload.get("content_policy"),
        "age_verified": bool(payload.get("age_verified", False)),
    }


class PlatformChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    mode: ChatMode = ChatMode.FAST
    context: str = Field("general", max_length=64)
    thread_id: Optional[str] = None
    character_id: Optional[str] = None
    response_language: Optional[str] = None
    client_requests_nsfw: bool = False


class PlatformChatResponse(BaseModel):
    response: str
    app_id: str
    content_policy: str
    mode: str
    intent: Optional[str] = None
    agents_used: List[str] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    sources: List[str] = Field(default_factory=list)
    nsfw_allowed: bool = False
    recording_allowed: bool = False
    thread_id: Optional[str] = None


class ThreadSummary(BaseModel):
    thread_id: str
    title: str
    updated_at: datetime
    message_count: int


class ThreadListResponse(BaseModel):
    threads: List[ThreadSummary]


class CreateThreadRequest(BaseModel):
    title: str = Field("New chat", max_length=200)


class UserProfileResponse(BaseModel):
    custom_instructions: Optional[str] = None
    personality_preset: Optional[str] = None
    memory_enabled: bool = False
    default_mode: ChatMode = ChatMode.FAST
    default_character_id: Optional[str] = None


class UserProfileUpdateRequest(BaseModel):
    custom_instructions: Optional[str] = Field(None, max_length=12000)
    personality_preset: Optional[str] = Field(None, max_length=64)
    memory_enabled: Optional[bool] = None
    default_mode: Optional[ChatMode] = None
    default_character_id: Optional[str] = None


class EphemeralTokenResponse(BaseModel):
    token: str
    expires_in_seconds: int = 300


async def _delegate_assistant(message: str, context: str, user_id: str, lang: Optional[str]) -> Dict[str, Any]:
    req = ChatMessageRequest(
        message=message,
        context=context,
        user_id=user_id,
        response_language=lang,
    )
    user_stub = {
        "user_id": user_id,
        "subscription_level": "premium",
        "limits": {},
        "payload": {},
    }
    resp = await ai_assistant_chat(req, user_stub)
    return resp.model_dump()


@platform_router.get("/capabilities")
async def platform_capabilities(user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Какие фичи включены для этого пользователя (флаги + возраст).
    iOS строит UI: mic, streaming, персонажи — без хардкода.
    """
    return get_platform_capabilities(user)


@platform_router.post("/chat", response_model=PlatformChatResponse)
async def platform_chat(body: PlatformChatRequest, user: dict = Depends(get_current_user)) -> PlatformChatResponse:
    pu = _platform_user(user)
    decision = evaluate_request_policy(
        app_id=pu["app_id"],
        message=body.message,
        age_verified=pu["age_verified"],
        jwt_policy=pu.get("content_policy"),
        client_requests_nsfw=body.client_requests_nsfw,
    )
    if not decision.allowed:
        raise HTTPException(
            status_code=422,
            detail={"code": decision.blocked_reason, "content_policy": decision.content_policy.value},
        )

    orch_req = OrchestratorRequest(
        message=body.message,
        user_id=pu["user_id"] or "anonymous",
        app_id=pu["app_id"],
        mode=body.mode,
        context=body.context,
        character_id=body.character_id,
        response_language=body.response_language,
        thread_id=body.thread_id,
    )
    result = await run_orchestrator(orch_req, delegate_chat=_delegate_assistant)

    thread_id = body.thread_id or secrets.token_hex(8)
    _threads.setdefault(pu["user_id"] or "anonymous", []).append(
        {"thread_id": thread_id, "role": "user", "text": body.message, "at": datetime.now().isoformat()}
    )

    return PlatformChatResponse(
        response=result.response_text,
        app_id=pu["app_id"],
        content_policy=decision.content_policy.value,
        mode=body.mode.value,
        intent=result.intent,
        agents_used=result.agents_used,
        tools_used=result.tools_used,
        sources=result.sources,
        nsfw_allowed=decision.nsfw_allowed,
        recording_allowed=decision.recording_allowed,
        thread_id=thread_id,
    )


@platform_router.get("/threads", response_model=ThreadListResponse)
async def list_threads(user: dict = Depends(get_current_user)) -> ThreadListResponse:
    uid = user["user_id"] or "anonymous"
    raw = _threads.get(uid, [])
    by_id: Dict[str, ThreadSummary] = {}
    for item in raw:
        tid = item["thread_id"]
        if tid not in by_id:
            by_id[tid] = ThreadSummary(
                thread_id=tid,
                title=item.get("text", "Chat")[:80],
                updated_at=datetime.fromisoformat(item["at"]),
                message_count=1,
            )
        else:
            by_id[tid].message_count += 1
    return ThreadListResponse(threads=list(by_id.values()))


@platform_router.post("/threads", response_model=ThreadSummary)
async def create_thread(body: CreateThreadRequest, user: dict = Depends(get_current_user)) -> ThreadSummary:
    tid = secrets.token_hex(8)
    return ThreadSummary(thread_id=tid, title=body.title, updated_at=datetime.now(), message_count=0)


@platform_router.get("/profile", response_model=UserProfileResponse)
async def get_profile(user: dict = Depends(get_current_user)) -> UserProfileResponse:
    uid = user["user_id"] or "anonymous"
    data = _profiles.get(uid, {})
    return UserProfileResponse(**{k: data.get(k) for k in UserProfileResponse.model_fields})


@platform_router.put("/profile", response_model=UserProfileResponse)
async def update_profile(body: UserProfileUpdateRequest, user: dict = Depends(get_current_user)) -> UserProfileResponse:
    uid = user["user_id"] or "anonymous"
    current = _profiles.get(uid, {})
    patch = body.model_dump(exclude_unset=True)
    current.update(patch)
    _profiles[uid] = current
    return UserProfileResponse(**{k: current.get(k) for k in UserProfileResponse.model_fields})


@voice_router.post("/ephemeral-token", response_model=EphemeralTokenResponse)
async def ephemeral_voice_token(user: dict = Depends(get_current_user)) -> EphemeralTokenResponse:
    """Short-lived token for mobile WebSocket voice (no API key on device)."""
    pu = _platform_user(user)
    payload = user.get("payload") or {}
    age_band = user.get("age_band") or payload.get("age_band", "parent")
    limits = user.get("limits") or {}
    parent_consent = user.get("parent_consent") or payload.get("parent_consent") or {}
    subscription_level = user.get("subscription_level") or "free"
    token = jwt.encode(
        {
            "sub": pu["user_id"],
            "app_id": pu["app_id"],
            "age_band": age_band,
            "scope": "voice_realtime",
            "limits": limits,
            "parent_consent": parent_consent,
            "subscription_level": subscription_level,
            "session_id": secrets.token_hex(8),
            "exp": int(time.time()) + 300,
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )
    return EphemeralTokenResponse(token=f"xai-client-secret.{token}", expires_in_seconds=300)


router.include_router(platform_router)
router.include_router(voice_router)
