# -*- coding: utf-8 -*-
"""
WebSocket voice realtime — production (P1-13).

Client sends on-device STT transcript with audio.stop:
  {"type": "audio.stop", "transcript": "...", "character_id": "unicorn", ...}
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, Optional

import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai/voice", tags=["AI Voice"])

try:
    from app.auth import JWT_SECRET, JWT_ALGORITHM
except ImportError:
    JWT_SECRET = os.environ["JWT_SECRET"]
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

try:
    from security.services.ai_platform.feature_flags import VOICE_ENABLED
    from security.services.ai_platform.usage_meters import check_voice_allowed, record_voice_seconds
    from security.services.ai_platform.companion_voice_turn import run_companion_voice_turn
except ImportError:
    VOICE_ENABLED = True

    def check_voice_allowed(*_a, **_k):  # type: ignore
        class R:
            allowed = True
            reason = None

        return R()

    def record_voice_seconds(user_id: str, seconds: int) -> Dict[str, int]:
        return {"voice_seconds": seconds}

    async def run_companion_voice_turn(**_kwargs):  # type: ignore
        raise RuntimeError("companion_voice_turn unavailable")


def _decode_ephemeral(token: str) -> Dict[str, Any]:
    raw = token
    if raw.startswith("xai-client-secret."):
        raw = raw[len("xai-client-secret.") :]
    return jwt.decode(raw, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def _user_from_voice_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    user_id = str(payload.get("sub") or "anonymous")
    return {
        "user_id": user_id,
        "subscription_level": payload.get("subscription_level") or "free",
        "limits": payload.get("limits") or {},
        "age_band": payload.get("age_band") or "child",
        "parent_consent": payload.get("parent_consent") or {},
        "payload": payload,
    }


@router.websocket("/realtime")
async def voice_realtime(websocket: WebSocket, token: Optional[str] = None):
    if not VOICE_ENABLED:
        await websocket.close(code=4403, reason="voice_disabled")
        return

    if not token:
        await websocket.close(code=4401, reason="missing_token")
        return

    try:
        payload = _decode_ephemeral(token)
    except jwt.PyJWTError:
        await websocket.close(code=4401, reason="invalid_token")
        return

    if payload.get("scope") != "voice_realtime":
        await websocket.close(code=4403, reason="invalid_scope")
        return

    user_id = str(payload.get("sub") or "anonymous")
    limits = payload.get("limits") or {}
    voice_check = check_voice_allowed(user_id, limits=limits, requested_seconds=0)
    if not voice_check.allowed:
        await websocket.close(code=4429, reason=voice_check.reason or "voice_limit")
        return

    await websocket.accept()
    session_id = payload.get("session_id") or f"voice-{int(time.time())}"
    user = _user_from_voice_payload(payload)
    voice_state: Dict[str, Any] = {
        "character_id": "unicorn",
        "family_id": None,
        "security_expert_mode": None,
        "response_language": None,
    }

    await websocket.send_json(
        {
            "type": "session.ready",
            "session_id": session_id,
            "app_id": payload.get("app_id"),
            "age_band": payload.get("age_band"),
        }
    )

    seconds_used = 0
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "code": "invalid_json"})
                continue

            mtype = msg.get("type")
            if mtype == "ping":
                await websocket.send_json({"type": "pong", "ts": int(time.time())})
            elif mtype == "audio.start":
                await websocket.send_json({"type": "listening", "emotion": "listening"})
            elif mtype == "config":
                if msg.get("character_id") in ("unicorn", "aladdin"):
                    voice_state["character_id"] = msg["character_id"]
                if msg.get("family_id"):
                    voice_state["family_id"] = str(msg.get("family_id"))[:128]
                if "security_expert_mode" in msg:
                    voice_state["security_expert_mode"] = bool(msg.get("security_expert_mode"))
                if msg.get("response_language"):
                    voice_state["response_language"] = str(msg.get("response_language"))[:8]
                await websocket.send_json({"type": "config.ack"})
            elif mtype == "audio.stop":
                transcript = str(msg.get("transcript") or "").strip()
                character_id = str(msg.get("character_id") or voice_state["character_id"])
                if character_id not in ("unicorn", "aladdin"):
                    character_id = "unicorn"

                await websocket.send_json(
                    {
                        "type": "transcript",
                        "text": transcript,
                        "partial": False,
                    }
                )

                if not transcript:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "code": "transcript_required",
                            "message": "Send transcript from on-device STT with audio.stop",
                        }
                    )
                    continue

                await websocket.send_json({"type": "thinking", "emotion": "thinking"})
                try:
                    resp = await run_companion_voice_turn(
                        user=user,
                        character_id=character_id,
                        transcript=transcript,
                        session_id=msg.get("session_id") or session_id,
                        family_id=msg.get("family_id") or voice_state.get("family_id"),
                        security_expert_mode=msg.get("security_expert_mode")
                        if "security_expert_mode" in msg
                        else voice_state.get("security_expert_mode"),
                        response_language=msg.get("response_language")
                        or voice_state.get("response_language"),
                    )
                    await websocket.send_json(
                        {
                            "type": "assistant.text",
                            "text": resp.response,
                            "emotion": resp.emotion,
                            "character_id": resp.character_id,
                            "companion_domain": resp.companion_domain,
                            "companion_mood": resp.companion_mood,
                            "trust_score": resp.trust_score,
                            "cosmetic_unlocked": resp.cosmetic_unlocked,
                        }
                    )
                    seconds_used += max(5, min(30, len(transcript) // 10 + 5))
                except Exception as exc:
                    logger.exception("companion voice turn failed: %s", exc)
                    await websocket.send_json(
                        {
                            "type": "error",
                            "code": "companion_unavailable",
                            "message": "Companion voice unavailable",
                        }
                    )
            elif mtype == "session.end":
                break
            else:
                await websocket.send_json({"type": "error", "code": "unknown_type", "got": mtype})
    except WebSocketDisconnect:
        logger.info("voice ws disconnect user=%s session=%s", user_id, session_id)
    finally:
        if seconds_used:
            record_voice_seconds(user_id, seconds_used)
        try:
            await websocket.send_json({"type": "session.closed"})
        except Exception:
            pass
