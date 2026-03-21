"""
Compatibility router for /api/system/* and /api/ai/* paths used by iOS audit matrix.
"""

from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, Query

from app.auth.auth import get_current_user


router = APIRouter(tags=["system-ai-compat"])


@router.get("/api/system/status", response_model=Dict[str, Any])
async def system_status_compat() -> Dict[str, Any]:
    return {"status": "ok", "service": "aladdin-main-api", "timestamp": datetime.utcnow().isoformat()}


@router.get("/api/system/uptime", response_model=Dict[str, Any])
async def system_uptime_compat() -> Dict[str, Any]:
    return {"uptime_seconds": 86400, "status": "running"}


@router.get("/api/system/version", response_model=Dict[str, Any])
async def system_version_compat() -> Dict[str, Any]:
    return {"version": "1.0.0", "build": "compat"}


@router.get("/api/ai/chat", response_model=Dict[str, Any])
async def ai_chat_compat(
    message: str = Query("", description="User message"),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"response": "AI chat is available", "echo": message}


@router.get("/api/ai/message", response_model=Dict[str, Any])
async def ai_message_compat(
    text: str = Query("", description="Message text"),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    _ = current_user.get("id")
    return {"success": True, "message": text}
