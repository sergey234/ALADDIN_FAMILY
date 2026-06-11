# -*- coding: utf-8 -*-
"""Structured llm_path metrics for Companion + AI Assistant (Phase 2.0)."""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, List, Optional

logger = logging.getLogger("aladdin.companion_llm")

_LOG_PATH = os.getenv("COMPANION_LLM_METRICS_LOG", "/var/log/aladdin-backend/companion_llm.log")


def _infer_llm_path(tools_used: Optional[List[str]]) -> str:
    tools = [str(t).lower() for t in (tools_used or [])]
    if any("hermes" in t for t in tools):
        return "hermes"
    if any("ollama" in t for t in tools):
        return "ollama"
    if any("openrouter_direct" in t or t.startswith("openrouter:") for t in tools):
        return "openrouter_direct"
    if any(t in ("kb_rag", "kb-rag") or t.startswith("kb:") for t in tools):
        return "kb_rag"
    return "sfm"


def log_llm_turn(
    *,
    ui_context: str,
    llm_path: str,
    intent: Optional[str] = None,
    tools_used: Optional[List[str]] = None,
    user_id: Optional[str] = None,
    character_id: Optional[str] = None,
    chat_mode: Optional[str] = None,
    latency_ms: Optional[int] = None,
    hermes_err_redacted: Optional[str] = None,
    message_len: Optional[int] = None,
) -> None:
    """Emit one JSON line for metrics / alerting (no PII in message body)."""
    payload: dict[str, Any] = {
        "ts": int(time.time()),
        "ui_context": (ui_context or "general")[:32],
        "llm_path": llm_path,
        "intent": (intent or "")[:64],
        "tools_used": (tools_used or [])[:12],
        "user_id_hash": (user_id or "")[:8] if user_id else "",
        "character_id": (character_id or "")[:24],
        "chat_mode": (chat_mode or "")[:16],
        "latency_ms": latency_ms,
        "message_len": message_len,
    }
    if hermes_err_redacted:
        payload["hermes_err"] = hermes_err_redacted[:200]

    line = json.dumps(payload, ensure_ascii=False)
    logger.info("companion_llm_path %s", line)
    try:
        log_dir = os.path.dirname(_LOG_PATH)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        with open(_LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError as exc:
        logger.warning("companion_llm metrics file write failed: %s", exc)


def log_from_tools(
    *,
    ui_context: str,
    tools_used: Optional[List[str]],
    intent: Optional[str] = None,
    user_id: Optional[str] = None,
    character_id: Optional[str] = None,
    chat_mode: Optional[str] = None,
    latency_ms: Optional[int] = None,
    hermes_err_redacted: Optional[str] = None,
    message_len: Optional[int] = None,
    llm_path: Optional[str] = None,
) -> None:
    path = llm_path or _infer_llm_path(tools_used)
    log_llm_turn(
        ui_context=ui_context,
        llm_path=path,
        intent=intent,
        tools_used=tools_used,
        user_id=user_id,
        character_id=character_id,
        chat_mode=chat_mode,
        latency_ms=latency_ms,
        hermes_err_redacted=hermes_err_redacted,
        message_len=message_len,
    )
