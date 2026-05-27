# -*- coding: utf-8 -*-
"""P1-13 — Companion voice turn (STT transcript → companion chat → reply)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from starlette.requests import Request


async def run_companion_voice_turn(
    *,
    user: Dict[str, Any],
    character_id: str,
    transcript: str,
    session_id: Optional[str] = None,
    family_id: Optional[str] = None,
    security_expert_mode: Optional[bool] = None,
    response_language: Optional[str] = None,
):
    """
    Run one companion chat turn for voice (same logic as POST /companion/chat).
    """
    from security.api.routers.ai_companion_router import CompanionChatRequest, companion_chat

    headers = []
    if family_id and family_id.strip():
        headers.append((b"x-aladdin-family-id", family_id.strip().encode()))
    scope = {"type": "http", "headers": headers, "method": "POST", "path": "/api/ai/companion/chat"}
    http_request = Request(scope)

    body = CompanionChatRequest(
        message=transcript.strip(),
        character_id=character_id,
        context="companion",
        response_language=response_language,
        session_id=session_id,
        input_mode="voice",
        security_expert_mode=security_expert_mode,
    )
    return await companion_chat(body, http_request, user)
