# -*- coding: utf-8 -*-
"""AI response policy helpers (prod: no mock unless AI_ALLOW_MOCK)."""
from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Dict

from fastapi import HTTPException

AI_SERVICE_UNAVAILABLE_DETAIL = "AI service unavailable"


def mock_allowed() -> bool:
    env = (os.getenv("ENV") or os.getenv("ENVIRONMENT") or "").lower()
    if env in ("development", "dev", "local", "test"):
        return os.getenv("AI_ALLOW_MOCK", "true").lower() in ("1", "true", "yes")
    return os.getenv("AI_ALLOW_MOCK", "false").lower() in ("1", "true", "yes")


def raise_service_unavailable(detail: str = AI_SERVICE_UNAVAILABLE_DETAIL) -> None:
    raise HTTPException(status_code=503, detail=detail)


def require_sfm_adapter(available: bool) -> None:
    if not available and not mock_allowed():
        raise_service_unavailable()


def dev_fallback_chat(context: str = "general") -> Dict[str, Any]:
    responses = {
        "protection_status": "[dev] Protection status mock",
        "threat_analysis": "[dev] Threat analysis mock",
        "general": "[dev] ALADDIN AI mock",
    }
    text = responses.get(context, responses["general"])
    return {
        "response": text,
        "confidence": 0.5,
        "suggestions": [],
        "follow_up_questions": [],
        "timestamp": datetime.now(),
        "grounded": False,
    }
