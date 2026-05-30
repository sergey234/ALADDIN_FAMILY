# -*- coding: utf-8 -*-
"""
ALADDIN Family Companion API (ADR P1-16 hot path).

REST API for animated family companions (Unicorn / Aladdin / Genie).
Delegates LLM work to ai_assistant_router; adds persona, trust, emotion, cosmetics.

Text: POST /chat, POST /stream (SSE resume).
Voice turn reuses /chat via companion_voice_turn + ai_voice_ws_router.
Post-LLM moderation: companion_post_llm_moderation (P1-22).

Usage in main.py:
    from security.api.routers.ai_companion_router import router as ai_companion_router
    app.include_router(ai_companion_router)
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import secrets
from datetime import datetime
from typing import Any, Dict, List, Optional

import jwt
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai/companion", tags=["AI Companion"])

security = HTTPBearer()

try:
    from app.auth import JWT_SECRET, JWT_ALGORITHM
except ImportError:
    JWT_SECRET = os.environ["JWT_SECRET"]
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Reuse assistant auth + rate limits
try:
    from security.api.routers.ai_assistant_router import (
        ChatMessageRequest,
        ChatMessageResponse,
        SuggestedAction,
        check_rate_limit,
        get_current_user,
        ai_assistant_chat,
    )
except ImportError:
    from ai_assistant_router import (  # type: ignore
        ChatMessageRequest,
        ChatMessageResponse,
        SuggestedAction,
        check_rate_limit,
        get_current_user,
        ai_assistant_chat,
    )

try:
    from security.services.ai_platform.config import AppId
    from security.services.ai_platform.policy_engine import evaluate_request_policy
    from security.services.ai_platform.capabilities import get_platform_capabilities
    from security.services.ai_platform.age_policy import (
        companion_access_allowed,
        filter_characters_for_age,
        get_age_band_rules,
        memory_allowed,
    )
    from security.services.ai_platform.companion_store import get_companion_store
    from security.services.ai_platform.companion_persona import (
        PERSONALITY_PRESET_HINTS,
        build_companion_system_prefix,
    )
    from security.services.ai_platform.companion_characters import (
        CHARACTER_ID_PATTERN,
        VALID_CHARACTER_IDS,
        normalize_personality_preset,
        available_personality_presets,
    )
    from security.services.ai_platform.companion_intent_router import classify_companion_intent
    from security.services.ai_platform.companion_emotions import emotion_for_companion
    from security.services.ai_platform.companion_ethics import evaluate_companion_ethics, ethics_hint_for_prompt
    from security.services.ai_platform.companion_post_llm_moderation import moderate_companion_assistant_text
    from security.services.ai_platform.companion_persona import security_expert_mode_active
    from security.services.ai_platform.companion_life_domains import list_life_domains
    from security.services.ai_platform.companion_teen_playbook import teen_playbook_hint
    from security.services.ai_platform.companion_social_bridge import apply_social_bridge
    from security.services.ai_platform.companion_trust_decay import apply_trust_visit
    from security.services.ai_platform.companion_family_context import build_family_context_hint
    from security.services.ai_platform.companion_web_search import maybe_companion_web_search
    from security.services.ai_platform.companion_attachments import validate_and_format_attachments
    from security.services.ai_platform.companion_responses_tools import tools_used_for_turn
    from security.services.ai_platform.companion_cogs import record_turn_cogs, build_cogs_dashboard
    from security.services.ai_platform.companion_workspaces import (
        create_workspace,
        list_workspaces,
        resolve_thread_for_workspace,
    )
    from security.services.ai_platform.companion_long_context import build_long_context_hint
    from security.services.ai_platform.companion_media_gen import (
        generate_companion_image,
        generate_companion_video,
    )
    from security.services.ai_platform.config import ChatMode
    from security.services.ai_platform.feature_flags import COMPANION_USE_ORCHESTRATOR
    from security.services.ai_platform.orchestrator import OrchestratorRequest, run_orchestrator
    from security.services.ai_platform.usage_meters import (
        check_message_allowed,
        check_voice_allowed,
        record_message,
        record_voice_seconds,
    )
    from security.services.ai_platform.companion_neuro_tts import (
        assert_premium_tts_allowed,
        build_tts_response_payload,
        estimate_speech_seconds,
        neuro_tts_configured,
        synthesize_neuro_tts,
    )
    from security.services.ai_platform.feature_flags import NEURO_TTS_ENABLED, COMPANION_SERVER_STT_ENABLED
    from security.services.ai_platform.companion_stt import (
        server_stt_configured,
        transcribe_audio_bytes,
    )
    from security.services.ai_pii_redactor import redact as redact_pii
    from security.services.ai_response_helpers import mock_allowed, is_probable_mock_response
except ImportError:
    from ai_platform.config import AppId  # type: ignore
    from ai_platform.policy_engine import evaluate_request_policy  # type: ignore
    from capabilities import get_platform_capabilities  # type: ignore

    def filter_characters_for_age(chars, age_band, parent_consent=None):  # type: ignore
        return chars

    def companion_access_allowed(*_a, **_k):  # type: ignore
        return True

    def get_age_band_rules(*_a, **_k):  # type: ignore
        class R:
            max_message_length = 2000
            voice_enabled = True

        return R()

    def memory_allowed(*_a, **_k):  # type: ignore
        return False

    def get_companion_store():  # type: ignore
        raise RuntimeError("companion_store unavailable")

    def check_message_allowed(*_a, **_k):  # type: ignore
        class U:
            allowed = True
            reason = None

        return U()

    def record_message(_uid):  # type: ignore
        return {}

    def redact_pii(t):  # type: ignore
        return type("R", (), {"text": t})()

    def mock_allowed():  # type: ignore
        return True

    def is_probable_mock_response(_t):  # type: ignore
        return False

    CHARACTER_ID_PATTERN = "^(aladdin|unicorn|genie)$"
    VALID_CHARACTER_IDS = ("unicorn", "aladdin", "genie")

    def normalize_personality_preset(preset, character_id, age_band):  # type: ignore
        return preset

    def available_personality_presets(age_band):  # type: ignore
        return ("friendly", "calm", "playful", "mentor")

CHARACTERS = [
    {
        "id": "unicorn",
        "display_name": "Единорог",
        "tagline": "Тёплый магический компаньон для детей",
        "available": True,
        "min_subscription": "free",
    },
    {
        "id": "aladdin",
        "display_name": "Аладдин",
        "tagline": "Мудрый наставник-человек (не джин)",
        "available": True,
        "min_subscription": "trial",
    },
    {
        "id": "genie",
        "display_name": "Джин",
        "tagline": "Магический остроумный спутник",
        "available": True,
        "min_subscription": "trial",
        "requires_parent_consent": True,
    },
]

COSMETICS_CATALOG = {
    "unicorn": [
        {"id": "horn_glow_soft", "trust_level": 2, "title": "Мягкое свечение рога"},
        {"id": "horn_glow_gold", "trust_level": 4, "title": "Золотое свечение рога"},
        {"id": "mane_sparkle", "trust_level": 5, "title": "Искры в гриве"},
    ],
    "aladdin": [
        {"id": "hoodie_star_patch", "trust_level": 2, "title": "Звёздная нашивка"},
        {"id": "lamp_pin_gold", "trust_level": 4, "title": "Золотой знак лампы"},
    ],
    "genie": [
        {"id": "smoke_trail_soft", "trust_level": 2, "title": "Мягкий шлейф дыма"},
        {"id": "lamp_aura_gold", "trust_level": 4, "title": "Золотая аура лампы"},
        {"id": "cuff_sparkle", "trust_level": 5, "title": "Искры на манжете"},
    ],
}

def _family_id_for_user(user: dict, header_family_id: Optional[str] = None) -> Optional[str]:
    if header_family_id and header_family_id.strip():
        return header_family_id.strip()
    payload = user.get("payload") or {}
    fid = payload.get("family_id")
    if fid:
        return str(fid).strip()
    return None


def _user_app_context(user: dict, family_id: Optional[str] = None) -> dict:
    from security.services.ai_platform.consent_resolver import resolve_parent_consent

    payload = user.get("payload") or {}
    user_id = str(user.get("user_id") or payload.get("sub") or "anonymous")
    fid = _family_id_for_user(user, family_id)
    jwt_consent = user.get("parent_consent") or payload.get("parent_consent") or {}
    return {
        "app_id": user.get("app_id") or payload.get("app_id", AppId.ALADDIN_FAMILY.value),
        "age_band": user.get("age_band") or payload.get("age_band", "parent"),
        "age_verified": bool(user.get("age_verified", payload.get("age_verified", False))),
        "content_policy": user.get("content_policy") or payload.get("content_policy"),
        "parent_consent": resolve_parent_consent(user_id, jwt_consent, fid),
        "family_id": fid,
    }

TRUST_LEVELS = [
    (0, 20, 1, "Знакомство"),
    (21, 40, 2, "Друг"),
    (41, 60, 3, "Надёжный помощник"),
    (61, 80, 4, "Семейный герой"),
    (81, 100, 5, "Хранитель семьи"),
]


def _user_key(user_id: str, character_id: str) -> str:
    return f"{user_id}:{character_id}"


def _trust_score(user_id: str, character_id: str) -> int:
    return get_companion_store().get_trust(user_id, character_id)


def _set_trust_score(user_id: str, character_id: str, score: int) -> int:
    return get_companion_store().set_trust(user_id, character_id, score)


def _trust_level_info(score: int) -> tuple:
    for lo, hi, level, name in TRUST_LEVELS:
        if lo <= score <= hi:
            return level, name
    return 5, "Хранитель семьи"


def _family_scope_key(request: Optional[Request], user: dict) -> tuple:
    """Returns (storage_key, ctx)."""
    from security.services.ai_platform.consent_resolver import memory_storage_key

    fid = request.headers.get("x-aladdin-family-id") if request else None
    ctx = _user_app_context(user, fid)
    user_id = str(user.get("user_id") or "anonymous")
    key = memory_storage_key(user_id, ctx.get("family_id") or fid)
    return key, ctx


def _normalize_profile_payload(raw: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    data = raw or {}
    preset = str(data.get("personality_preset") or "friendly")
    if preset not in PERSONALITY_PRESET_HINTS:
        preset = "friendly"
    equipped = str(data.get("equipped_cosmetic_id") or "").strip()
    equipped_char = str(data.get("equipped_cosmetic_character_id") or "unicorn").strip()
    if equipped_char not in VALID_CHARACTER_IDS:
        equipped_char = "unicorn"
    normalized = {
        "custom_instructions": str(data.get("custom_instructions") or "")[:2000],
        "personality_preset": preset,
        "security_expert_mode": bool(data.get("security_expert_mode")),
        "equipped_cosmetic_id": equipped[:64],
        "equipped_cosmetic_character_id": equipped_char,
    }
    bridge = data.get("social_bridge")
    if isinstance(bridge, dict) and bridge:
        normalized["social_bridge"] = bridge
    return normalized


def _load_companion_profile(storage_key: str) -> Dict[str, Any]:
    return _normalize_profile_payload(get_companion_store().get_profile(storage_key))


def _cosmetic_unlocked(character_id: str, cosmetic_id: str, user_id: str) -> bool:
    if not cosmetic_id:
        return True
    catalog_ids = {item["id"] for item in COSMETICS_CATALOG.get(character_id, [])}
    if cosmetic_id not in catalog_ids:
        return False
    score = _trust_score(user_id, character_id)
    level, _ = _trust_level_info(score)
    for item in COSMETICS_CATALOG.get(character_id, []):
        if item["id"] == cosmetic_id:
            return item["trust_level"] <= level
    return False


def _security_expert_phrase_toggle(message: str) -> bool:
    import re

    return bool(
        re.search(
            r"помоги с защит|режим безопасност|эксперт.*безопас|включи.*vpn|что с угроз",
            (message or "").lower(),
        )
    )


def _merge_profile_for_turn(
    profile: Dict[str, Any],
    *,
    request_flag: Optional[bool],
    message: str,
) -> Dict[str, Any]:
    merged = dict(profile)
    if request_flag is not None:
        merged["security_expert_mode"] = bool(request_flag)
    elif _security_expert_phrase_toggle(message):
        merged["security_expert_mode"] = True
    return merged


def _build_companion_system_prefix(
    character_id: str,
    profile: Optional[Dict[str, Any]] = None,
    age_band: str = "child",
) -> str:
    return build_companion_system_prefix(
        character_id,
        profile or {},
        age_band,
        redact_custom=lambda t: redact_pii(t).text,
    )


def _memory_scope(request: Optional[Request], user: dict) -> tuple:
    """Returns (storage_key, memory_enabled, ctx)."""
    from security.services.ai_platform.consent_resolver import memory_storage_key

    fid = request.headers.get("x-aladdin-family-id") if request else None
    ctx = _user_app_context(user, fid)
    user_id = str(user.get("user_id") or "anonymous")
    key = memory_storage_key(user_id, ctx.get("family_id") or fid)
    consent = ctx["parent_consent"]
    enabled = memory_allowed(ctx["age_band"], consent) and bool(consent.get("memory_enabled"))
    return key, enabled, ctx


def _parse_memory_dt(raw: str) -> datetime:
    try:
        return datetime.fromisoformat(str(raw)[:26])
    except ValueError:
        return datetime.utcnow()


def _memory_items_response(store, storage_key: str, enabled: bool) -> CompanionMemoryResponse:
    raw = store.list_memory_items(storage_key) if enabled else []
    items = [
        CompanionMemoryItem(
            key=m["key"],
            summary=m["summary"],
            updated_at=_parse_memory_dt(m["updated_at"]),
        )
        for m in raw
    ]
    return CompanionMemoryResponse(items=items, memory_enabled=enabled, item_count=len(items))


def _maybe_record_memory(
    storage_key: str,
    enabled: bool,
    user_message: str,
    assistant_message: str,
) -> None:
    if not enabled:
        return
    u = redact_pii(user_message.strip()).text[:280]
    a = redact_pii(assistant_message.strip()).text[:280]
    if not u and not a:
        return
    summary = f"Вопрос: {u} — Ответ: {a}"
    item_key = f"ex-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    get_companion_store().upsert_memory_item(storage_key, item_key, summary)


def _policy_block_message(message: str, user: dict, family_id: Optional[str] = None) -> bool:
    ctx = _user_app_context(user, family_id)
    decision = evaluate_request_policy(
        app_id=ctx["app_id"],
        message=message,
        age_verified=ctx["age_verified"],
        jwt_policy=ctx.get("content_policy"),
        client_requests_nsfw=False,
        age_band=ctx["age_band"],
    )
    return not decision.allowed


def _animation_hint_for_emotion(emotion: str) -> Optional[str]:
    if emotion in ("happy", "playful", "celebrate", "excited"):
        return "nod"
    if emotion in ("comfort", "sad", "nostalgic"):
        return "idle"
    if emotion == "alert":
        return "shake_head"
    return None


def _trust_delta(
    message: str,
    blocked: bool,
    *,
    domain: str = "general",
    mood: str = "neutral",
    intent_id: str = "",
) -> int:
    if blocked:
        return -5
    if len((message or "").strip()) < 3:
        return 0
    if domain in ("loneliness", "feelings") or mood in ("lonely", "comfort_needed"):
        return 4
    if mood == "playful" or intent_id in ("companion_humor", "companion_playful"):
        return 3
    if domain == "safety" and intent_id not in ("threat_analysis", "report_incident"):
        return 1
    return 2


def _feedback_trust_delta(vote: str) -> int:
    return 1 if vote == "up" else -1


def _parse_chat_mode(raw: Optional[str]) -> "ChatMode":
    try:
        from security.services.ai_platform.config import ChatMode as CM

        return CM((raw or "fast").lower())
    except (NameError, ValueError):
        from security.services.ai_platform.config import ChatMode as CM

        return CM.FAST


async def _invoke_companion_llm(
    prefixed: str,
    user_id: str,
    response_language: Optional[str],
    user: dict,
    *,
    chat_mode: str = "fast",
) -> ChatMessageResponse:
    """P2-02 — delegate to assistant or orchestrator when COMPANION_USE_ORCHESTRATOR=1."""
    assistant_req = ChatMessageRequest(
        message=prefixed,
        context="companion",
        user_id=user_id,
        timestamp=datetime.now(),
        response_language=response_language,
    )
    try:
        use_orch = COMPANION_USE_ORCHESTRATOR
    except NameError:
        use_orch = False

    if not use_orch:
        return await ai_assistant_chat(assistant_req, user)

    async def _delegate(msg, ctx, uid, lang):
        req = ChatMessageRequest(
            message=msg,
            context=ctx,
            user_id=uid,
            timestamp=datetime.now(),
            response_language=lang,
        )
        resp = await ai_assistant_chat(req, user)
        return {
            "response": resp.response,
            "intent": resp.intent,
            "tools_used": resp.tools_used or [],
            "sources": resp.sources or [],
            "grounded": resp.grounded,
        }

    mode = _parse_chat_mode(chat_mode)
    orch = await run_orchestrator(
        OrchestratorRequest(
            message=prefixed,
            user_id=user_id,
            app_id="aladdin_family",
            context="companion",
            response_language=response_language,
            mode=mode,
        ),
        delegate_chat=_delegate,
    )
    return ChatMessageResponse(
        response=orch.response_text,
        intent=orch.intent,
        confidence=0.9,
        tools_used=orch.tools_used,
        sources=orch.sources,
        grounded=orch.grounded,
    )


def _record_companion_feedback_analytics(
    *,
    user_id: str,
    session_id: Optional[str],
    rating: int,
    query_redacted: Optional[str],
) -> None:
    try:
        from security.services.ai_history_store import record_analytics_event

        record_analytics_event(
            user_id=user_id,
            question_redacted=query_redacted,
            ui_context="companion_feedback",
            session_id=session_id,
            rating=rating,
            resolved_by="companion",
        )
    except Exception as exc:
        logger.warning("Companion feedback analytics failed: %s", exc)


def _unlocked_cosmetics(character_id: str, score: int) -> List[str]:
    level, _ = _trust_level_info(score)
    out: List[str] = []
    for item in COSMETICS_CATALOG.get(character_id, []):
        if item["trust_level"] <= level:
            out.append(item["id"])
    return out


def _new_cosmetic_unlock(character_id: str, old_score: int, new_score: int) -> Optional[str]:
    old_level, _ = _trust_level_info(old_score)
    new_level, _ = _trust_level_info(new_score)
    if new_level <= old_level:
        return None
    for item in COSMETICS_CATALOG.get(character_id, []):
        if item["trust_level"] == new_level:
            return item["id"]
    return None


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class CompanionCharacterDTO(BaseModel):
    id: str
    display_name: str
    tagline: str
    available: bool = True
    min_subscription: str = "free"


class CompanionCharactersResponse(BaseModel):
    characters: List[CompanionCharacterDTO]


class CompanionLifeDomainDTO(BaseModel):
    id: str
    label: str
    starter_prompt: str
    age_bands: List[str] = Field(default_factory=list)


class CompanionLifeDomainsResponse(BaseModel):
    domains: List[CompanionLifeDomainDTO]


class CompanionUsageSnapshot(BaseModel):
    messages_today: int = 0
    messages_daily_cap: int = 50
    messages_usage_percent: int = 0
    voice_seconds_today: int = 0
    voice_daily_cap_seconds: int = 240
    voice_usage_percent: int = 0
    warn_threshold_percent: int = 80
    should_warn_messages: bool = False
    should_warn_voice: bool = False
    message_limit_reached: bool = False
    voice_limit_reached: bool = False


class CompanionStateResponse(BaseModel):
    character_id: str
    trust_score: int = Field(..., ge=0, le=100)
    trust_level: int = Field(..., ge=1, le=5)
    trust_level_name: str
    emotion_default: str = "idle"
    cosmetics_unlocked: List[str] = Field(default_factory=list)
    memory_enabled: bool = False
    parent_consent_memory: bool = False
    voice_enabled: bool = True
    nsfw_blocked: bool = True
    usage: Optional[CompanionUsageSnapshot] = None


class CompanionAttachmentDTO(BaseModel):
    kind: str = Field(..., pattern="^(image|pdf)$")
    filename: str = Field(..., max_length=128)
    mime_type: Optional[str] = Field(None, max_length=64)
    content_b64: Optional[str] = Field(None, max_length=500_000)


class CompanionChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    character_id: str = Field(..., pattern=CHARACTER_ID_PATTERN)
    context: str = Field("companion", max_length=64)
    response_language: Optional[str] = None
    session_id: Optional[str] = Field(None, max_length=128)
    input_mode: str = Field("text", pattern="^(text|voice)$")
    security_expert_mode: Optional[bool] = Field(
        None, description="P1-29: усилить security-контекст для этого сообщения/сессии"
    )
    chat_mode: str = Field("fast", pattern="^(fast|reasoning|think)$")
    workspace_id: Optional[str] = Field(None, max_length=64)
    attachments: List[CompanionAttachmentDTO] = Field(default_factory=list)


class CompanionStreamRequest(BaseModel):
    message: str = Field("", description="Пусто для resume", max_length=2000)
    character_id: str = Field(..., pattern=CHARACTER_ID_PATTERN)
    context: str = Field("companion", max_length=64)
    response_language: Optional[str] = None
    session_id: Optional[str] = Field(None, max_length=128)
    input_mode: str = Field("text", pattern="^(text|voice)$")
    resumeFromIndex: int = Field(0, ge=0)
    messageId: Optional[str] = Field(None, max_length=128)
    stream: bool = True
    security_expert_mode: Optional[bool] = None
    chat_mode: str = Field("fast", pattern="^(fast|reasoning|think)$")
    workspace_id: Optional[str] = Field(None, max_length=64)
    attachments: List[CompanionAttachmentDTO] = Field(default_factory=list)


class CompanionChatResponse(BaseModel):
    response: str
    character_id: str
    emotion: str
    animation_hint: Optional[str] = None
    trust_delta: int = 0
    trust_score: int
    trust_level: int
    confidence: float = 0.9
    intent: Optional[str] = None
    companion_domain: Optional[str] = Field(None, description="Life domain (P1-27)")
    companion_mood: Optional[str] = Field(None, description="Detected mood (P1-27)")
    mood_confidence: Optional[float] = Field(None, description="P2-11 mood classifier confidence")
    security_expert_mode: bool = Field(False, description="P1-29 active for this reply")
    grounded: Optional[bool] = None
    sources: List[str] = Field(default_factory=list)
    tools_used: List[str] = Field(default_factory=list)
    suggested_actions: List[SuggestedAction] = Field(default_factory=list)
    cosmetic_unlocked: Optional[str] = None
    nsfw_blocked: bool = True
    follow_up_questions: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    show_social_bridge: bool = Field(False, description="P2-13 suggest contacting a close person")
    social_bridge_suggestions: List[str] = Field(default_factory=list)
    trust_streak_days: int = Field(0, description="P2-05 consecutive active days")
    cogs_alert: bool = Field(False, description="P2-08 daily cost alert triggered")
    chat_mode: Optional[str] = Field(None, description="P2-03 mode used for this turn")


class CompanionConsentRequest(BaseModel):
    memory_enabled: bool = False
    child_can_use_companion: bool = True
    allowed_characters: List[str] = Field(
        default_factory=lambda: ["unicorn", "aladdin", "genie"]
    )
    family_id: Optional[str] = Field(None, max_length=128)


class CompanionConsentResponse(BaseModel):
    recorded: bool = True
    memory_enabled: bool
    child_can_use_companion: bool
    allowed_characters: List[str]
    family_id: Optional[str] = None
    scope: str = "user"


class CompanionProfileResponse(BaseModel):
    custom_instructions: str = ""
    personality_preset: str = "friendly"
    security_expert_mode: bool = False
    equipped_cosmetic_id: str = ""
    equipped_cosmetic_character_id: str = "unicorn"
    storage_scope: str = ""
    available_presets: List[str] = Field(
        default_factory=lambda: list(PERSONALITY_PRESET_HINTS.keys())
    )


class CompanionProfileUpdateRequest(BaseModel):
    custom_instructions: Optional[str] = Field(None, max_length=2000)
    personality_preset: Optional[str] = Field(None, max_length=32)
    security_expert_mode: Optional[bool] = None
    equipped_cosmetic_id: Optional[str] = Field(None, max_length=64)
    equipped_cosmetic_character_id: Optional[str] = Field(None, max_length=16)


class CompanionFeedbackRequest(BaseModel):
    vote: str = Field(..., pattern="^(up|down)$")
    character_id: str = Field(..., pattern=CHARACTER_ID_PATTERN)
    thread_id: Optional[str] = Field(None, max_length=128)
    message_id: Optional[str] = Field(None, max_length=64)
    assistant_text: Optional[str] = Field(None, max_length=2000)
    user_query_text: Optional[str] = Field(None, max_length=2000)


class CompanionFeedbackResponse(BaseModel):
    recorded: bool = True
    vote: str
    rating: int
    trust_delta: int = 0
    trust_score: int = 10
    feedback_id: Optional[int] = None


class CompanionAnalyticsEventRequest(BaseModel):
    """P1-10 — product metrics (no message text)."""

    event: str = Field(..., max_length=64)
    character_id: Optional[str] = Field(None, pattern=CHARACTER_ID_PATTERN)
    session_id: Optional[str] = Field(None, max_length=128)
    extra: Optional[Dict[str, str]] = None


class CompanionAnalyticsEventResponse(BaseModel):
    recorded: bool = True
    event: str


class CompanionMemoryItem(BaseModel):
    key: str
    summary: str
    updated_at: datetime


class CompanionMemoryResponse(BaseModel):
    items: List[CompanionMemoryItem]
    memory_enabled: bool
    item_count: int = 0


class CompanionMemoryExportResponse(BaseModel):
    exported_at: datetime
    storage_scope: str
    memory_enabled: bool
    item_count: int
    items: List[CompanionMemoryItem]


class CompanionCosmeticDTO(BaseModel):
    id: str
    title: str
    trust_level: int
    unlocked: bool


class CompanionCosmeticsResponse(BaseModel):
    character_id: str
    cosmetics: List[CompanionCosmeticDTO]


class CompanionThreadSummaryDTO(BaseModel):
    thread_id: str
    title: str
    updated_at: datetime
    message_count: int
    character_id: str = "unicorn"


class CompanionThreadsResponse(BaseModel):
    threads: List[CompanionThreadSummaryDTO]


class CompanionThreadMessageDTO(BaseModel):
    role: str
    text: str
    created_at: datetime
    character_id: Optional[str] = None


class CompanionThreadMessagesResponse(BaseModel):
    thread_id: str
    messages: List[CompanionThreadMessageDTO]


class CompanionTTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000)
    character_id: str = Field("unicorn", max_length=32)
    locale: str = Field("ru", max_length=8)


class CompanionTTSResponse(BaseModel):
    audio_base64: str
    content_type: str = "audio/mpeg"
    provider: str = "elevenlabs"
    cached: bool = False
    duration_seconds: Optional[float] = None


class CompanionSTTResponse(BaseModel):
    text: str
    confidence: float = 0.0
    provider: str = "openai_whisper"
    language: str = "ru"
    duration_sec: Optional[float] = None
    audio_retention_sec: int = 0


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/capabilities")
async def companion_capabilities(user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Те же capabilities что platform — для Kids companion UI."""
    return get_platform_capabilities(user)


@router.post("/tts", response_model=CompanionTTSResponse)
async def companion_neuro_tts(
    body: CompanionTTSRequest,
    user: dict = Depends(get_current_user),
) -> CompanionTTSResponse:
    """
    Premium neuro-TTS (ElevenLabs Flash). Free/trial → 403; iOS falls back to AVSpeech.
    Визуал героев не зависит от тарифа — только озвучка.
    """
    if not NEURO_TTS_ENABLED:
        raise HTTPException(status_code=424, detail="neuro_tts_disabled")
    subscription_level = user.get("subscription_level") or "free"
    try:
        assert_premium_tts_allowed(subscription_level)
    except ValueError:
        raise HTTPException(status_code=403, detail="neuro_tts_requires_premium")
    if not neuro_tts_configured():
        raise HTTPException(status_code=424, detail="neuro_tts_unconfigured")

    character_id = (body.character_id or "unicorn").strip().lower()
    if character_id not in VALID_CHARACTER_IDS:
        raise HTTPException(status_code=400, detail="invalid_character_id")

    user_id = user.get("user_id") or "anonymous"
    est_sec = estimate_speech_seconds(body.text)
    voice_check = check_voice_allowed(user_id, user.get("limits"), requested_seconds=est_sec)
    if not voice_check.allowed:
        raise HTTPException(status_code=429, detail=voice_check.reason or "voice_limit")

    try:
        audio, cached, content_type = await asyncio.to_thread(
            synthesize_neuro_tts,
            text=body.text,
            character_id=character_id,
            lang=(body.locale or "ru")[:8],
        )
    except ValueError as exc:
        reason = str(exc)
        if reason == "neuro_tts_requires_premium":
            raise HTTPException(status_code=403, detail=reason)
        if reason in ("neuro_tts_unconfigured", "voice_id_missing"):
            raise HTTPException(status_code=424, detail=reason)
        raise HTTPException(status_code=400, detail=reason)

    record_voice_seconds(user_id, est_sec)
    payload = build_tts_response_payload(
        audio,
        cached=cached,
        content_type=content_type,
        duration_seconds=float(est_sec),
    )
    return CompanionTTSResponse(**payload)


@router.post("/stt", response_model=CompanionSTTResponse)
async def companion_server_stt(
    user: dict = Depends(get_current_user),
    audio: UploadFile = File(...),
    language: str = Form("ru"),
    character_id: str = Form("unicorn"),
    session_id: Optional[str] = Form(None),
) -> CompanionSTTResponse:
    """
    Hybrid STT fallback: short audio → text in RAM → discard audio.

    Requires FEATURE_COMPANION_SERVER_STT=1 and OPENAI_API_KEY (Whisper API).
    Not a replacement for on-device / Siri STT — only when Apple path failed.
    """
    if not COMPANION_SERVER_STT_ENABLED:
        raise HTTPException(status_code=424, detail="server_stt_disabled")
    if not server_stt_configured():
        raise HTTPException(status_code=424, detail="server_stt_unconfigured")

    user_id = user.get("user_id") or "anonymous"
    subscription_level = user.get("subscription_level") or "free"
    if not check_rate_limit(user_id, subscription_level):
        raise HTTPException(status_code=429, detail="rate_limit")

    raw = await audio.read()
    content_type = (audio.content_type or "audio/wav").strip()

    try:
        result = await asyncio.to_thread(
            transcribe_audio_bytes,
            raw,
            content_type=content_type,
            language=(language or "ru")[:8],
        )
    except ValueError as exc:
        reason = str(exc)
        if reason in ("empty_audio", "audio_too_large", "audio_too_long"):
            raise HTTPException(status_code=400, detail=reason)
        if reason == "empty_transcript":
            raise HTTPException(status_code=422, detail=reason)
        if reason in ("server_stt_network_error", "server_stt_provider_error"):
            raise HTTPException(status_code=503, detail=reason)
        raise HTTPException(status_code=424, detail=reason)

    text = str(result.get("text") or "").strip()
    redacted = redact_pii(text).text if text else ""
    if not redacted.strip():
        raise HTTPException(status_code=422, detail="empty_transcript_after_redact")

    logger.info(
        "companion_stt_fallback_used user_id=%s character_id=%s session_id=%s provider=%s duration_sec=%s",
        user_id,
        (character_id or "")[:32],
        (session_id or "")[:64] or None,
        result.get("provider"),
        result.get("duration_sec"),
    )
    return CompanionSTTResponse(
        text=redacted.strip(),
        confidence=float(result.get("confidence") or 0.0),
        provider=str(result.get("provider") or "openai_whisper"),
        language=str(result.get("language") or language or "ru"),
        duration_sec=result.get("duration_sec"),
        audio_retention_sec=0,
    )


@router.get("/threads", response_model=CompanionThreadsResponse)
async def list_companion_threads(
    user: dict = Depends(get_current_user),
    limit: int = Query(50, ge=1, le=100),
) -> CompanionThreadsResponse:
    """История диалогов companion (P1-01)."""
    user_id = user["user_id"] or "anonymous"
    raw = get_companion_store().list_thread_summaries(user_id, limit=limit)
    threads = [
        CompanionThreadSummaryDTO(
            thread_id=item["thread_id"],
            title=item["title"],
            updated_at=datetime.fromisoformat(item["updated_at"]),
            message_count=int(item["message_count"]),
            character_id=item.get("character_id") or "unicorn",
        )
        for item in raw
    ]
    return CompanionThreadsResponse(threads=threads)


@router.get("/threads/{thread_id}/messages", response_model=CompanionThreadMessagesResponse)
async def get_companion_thread_messages(
    thread_id: str,
    user: dict = Depends(get_current_user),
    limit: int = Query(100, ge=1, le=200),
) -> CompanionThreadMessagesResponse:
    user_id = user["user_id"] or "anonymous"
    raw = get_companion_store().get_thread_messages(user_id, thread_id, limit=limit)
    messages = [
        CompanionThreadMessageDTO(
            role=m["role"],
            text=m["text"],
            created_at=datetime.fromisoformat(m["created_at"]),
            character_id=m.get("character_id"),
        )
        for m in raw
    ]
    return CompanionThreadMessagesResponse(thread_id=thread_id, messages=messages)


@router.get("/characters", response_model=CompanionCharactersResponse)
async def list_characters(
    request: Request,
    user: dict = Depends(get_current_user),
) -> CompanionCharactersResponse:
    """Available companion personas."""
    fid = request.headers.get("x-aladdin-family-id")
    ctx = _user_app_context(user, fid)
    filtered = filter_characters_for_age(CHARACTERS, ctx["age_band"], ctx["parent_consent"])
    return CompanionCharactersResponse(
        characters=[CompanionCharacterDTO(**c) for c in filtered]
    )


@router.get("/domains", response_model=CompanionLifeDomainsResponse)
async def list_companion_domains(
    request: Request,
    user: dict = Depends(get_current_user),
    locale: str = Query("ru", max_length=8),
    security_expert_mode: bool = Query(False),
) -> CompanionLifeDomainsResponse:
    """P2-12 — темы «О чём поговорим?» для chips в iOS."""
    fid = request.headers.get("x-aladdin-family-id")
    ctx = _user_app_context(user, fid)
    rows = list_life_domains(
        age_band=ctx["age_band"],
        locale=locale,
        security_expert_mode=security_expert_mode,
    )
    return CompanionLifeDomainsResponse(
        domains=[CompanionLifeDomainDTO(**row) for row in rows]
    )


class CompanionWorkspaceDTO(BaseModel):
    workspace_id: str
    title: str
    character_id: str = "unicorn"
    thread_id: Optional[str] = None
    updated_at: Optional[str] = None


class CompanionWorkspacesResponse(BaseModel):
    workspaces: List[CompanionWorkspaceDTO]


class CompanionWorkspaceCreateRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=80)
    character_id: str = Field("unicorn", pattern=CHARACTER_ID_PATTERN)


class CompanionCogsResponse(BaseModel):
    daily_usd: float
    month_usd: float
    turns_today: int
    alert_threshold_usd: float
    alert_triggered: bool


class CompanionMediaGenRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=500)
    character_id: str = Field("unicorn", pattern=CHARACTER_ID_PATTERN)


class CompanionMediaGenResponse(BaseModel):
    ok: bool
    status: str
    message: str
    image_url: Optional[str] = None
    video_url: Optional[str] = None


@router.get("/workspaces", response_model=CompanionWorkspacesResponse)
async def list_companion_workspaces(
    user: dict = Depends(get_current_user),
    limit: int = Query(30, ge=1, le=100),
) -> CompanionWorkspacesResponse:
    """P3-03 — topic folders for companion chats."""
    user_id = user["user_id"] or "anonymous"
    rows = list_workspaces(get_companion_store(), user_id, limit=limit)
    return CompanionWorkspacesResponse(
        workspaces=[
            CompanionWorkspaceDTO(
                workspace_id=r["workspace_id"],
                title=r.get("title") or "Чат",
                character_id=r.get("character_id") or "unicorn",
                thread_id=r.get("thread_id"),
                updated_at=r.get("updated_at"),
            )
            for r in rows
        ]
    )


@router.post("/workspaces", response_model=CompanionWorkspaceDTO)
async def create_companion_workspace(
    body: CompanionWorkspaceCreateRequest,
    user: dict = Depends(get_current_user),
) -> CompanionWorkspaceDTO:
    user_id = user["user_id"] or "anonymous"
    row = create_workspace(
        get_companion_store(),
        user_id,
        body.title,
        character_id=body.character_id,
    )
    return CompanionWorkspaceDTO(**row)


@router.get("/cogs", response_model=CompanionCogsResponse)
async def companion_cogs_dashboard(
    user: dict = Depends(get_current_user),
) -> CompanionCogsResponse:
    """P2-08 — estimated AI unit economics for the current user."""
    user_id = user["user_id"] or "anonymous"
    dash = build_cogs_dashboard(get_companion_store(), user_id)
    return CompanionCogsResponse(**dash)


@router.post("/media/image", response_model=CompanionMediaGenResponse)
async def companion_generate_image(
    body: CompanionMediaGenRequest,
    request: Request,
    user: dict = Depends(get_current_user),
) -> CompanionMediaGenResponse:
    """P3-01 — family-safe image generation (stub when flag off)."""
    fid = request.headers.get("x-aladdin-family-id")
    ctx = _user_app_context(user, fid)
    result = generate_companion_image(
        body.prompt, age_band=ctx["age_band"], character_id=body.character_id
    )
    return CompanionMediaGenResponse(
        ok=bool(result.get("ok")),
        status=str(result.get("status") or "error"),
        message=str(result.get("message") or result.get("error") or ""),
        image_url=result.get("image_url"),
    )


@router.post("/media/video", response_model=CompanionMediaGenResponse)
async def companion_generate_video(
    body: CompanionMediaGenRequest,
    request: Request,
    user: dict = Depends(get_current_user),
) -> CompanionMediaGenResponse:
    """P3-02 — video generation stub (disabled in Family MVP)."""
    fid = request.headers.get("x-aladdin-family-id")
    ctx = _user_app_context(user, fid)
    result = generate_companion_video(body.prompt, age_band=ctx["age_band"])
    return CompanionMediaGenResponse(
        ok=bool(result.get("ok")),
        status=str(result.get("status") or "error"),
        message=str(result.get("message") or result.get("error") or ""),
        video_url=result.get("video_url"),
    )


@router.post("/analytics", response_model=CompanionAnalyticsEventResponse)
async def record_companion_analytics_event(
    body: CompanionAnalyticsEventRequest,
    user: dict = Depends(get_current_user),
) -> CompanionAnalyticsEventResponse:
    """P1-10 — N1–N6 companion funnel (hash-only store, no PII)."""
    from security.services.ai_platform.companion_analytics import (
        ALLOWED_EVENTS,
        record_companion_product_event,
    )

    if body.event not in ALLOWED_EVENTS:
        raise HTTPException(status_code=400, detail="unknown_event")
    user_id = str(user.get("user_id") or "anonymous")
    record_companion_product_event(
        user_id=user_id,
        event=body.event,
        character_id=body.character_id,
        session_id=body.session_id,
        extra=dict(body.extra or {}),
    )
    return CompanionAnalyticsEventResponse(recorded=True, event=body.event)


@router.get("/state", response_model=CompanionStateResponse)
async def companion_state(
    request: Request,
    character_id: str = Query(..., pattern=CHARACTER_ID_PATTERN),
    user: dict = Depends(get_current_user),
) -> CompanionStateResponse:
    user_id = user["user_id"] or "anonymous"
    fid = request.headers.get("x-aladdin-family-id")
    ctx = _user_app_context(user, fid)
    score = _trust_score(user_id, character_id)
    level, level_name = _trust_level_info(score)
    store = get_companion_store()
    consent = ctx["parent_consent"]
    rules = get_age_band_rules(ctx["age_band"])
    memory_on = memory_allowed(ctx["age_band"], consent) and bool(consent.get("memory_enabled"))
    from security.services.ai_platform.companion_usage import build_usage_snapshot

    usage_raw = build_usage_snapshot(
        user_id,
        user.get("subscription_level") or "free",
        user.get("limits"),
    )
    return CompanionStateResponse(
        character_id=character_id,
        trust_score=score,
        trust_level=level,
        trust_level_name=level_name,
        cosmetics_unlocked=_unlocked_cosmetics(character_id, score),
        memory_enabled=memory_on,
        parent_consent_memory=bool(consent.get("memory_enabled")),
        voice_enabled=rules.voice_enabled,
        nsfw_blocked=True,
        usage=CompanionUsageSnapshot(**usage_raw),
    )


@router.post("/chat", response_model=CompanionChatResponse)
async def companion_chat(
    body: CompanionChatRequest,
    http_request: Request,
    user: dict = Depends(get_current_user),
) -> CompanionChatResponse:
    user_id = user["user_id"] or "anonymous"
    subscription_level = user["subscription_level"]
    fid = http_request.headers.get("x-aladdin-family-id")
    ctx = _user_app_context(user, fid)

    if not companion_access_allowed(ctx["age_band"], ctx["parent_consent"]):
        raise HTTPException(status_code=403, detail="Companion disabled by parental consent.")

    usage = check_message_allowed(user_id, subscription_level, user.get("limits"))
    if not usage.allowed:
        raise HTTPException(status_code=429, detail=usage.reason or "usage_limit")

    if not check_rate_limit(user_id, subscription_level):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded for {subscription_level} subscription.",
        )

    rules = get_age_band_rules(ctx["age_band"])
    if len(body.message) > rules.max_message_length:
        raise HTTPException(status_code=422, detail="message_too_long_for_age_band")

    consent = ctx["parent_consent"]
    allowed_ids = {c["id"] for c in filter_characters_for_age(CHARACTERS, ctx["age_band"], consent)}
    if body.character_id not in allowed_ids:
        raise HTTPException(status_code=403, detail="Character not allowed for this age band.")

    # Companion API is ALADDIN Family only (adult uses platform + separate app)
    safe_message = redact_pii(body.message.strip()).text
    blocked = _policy_block_message(safe_message, user, fid)

    scope_key, _ = _family_scope_key(http_request, user)
    profile = _merge_profile_for_turn(
        _load_companion_profile(scope_key),
        request_flag=body.security_expert_mode,
        message=safe_message,
    )
    cintent = classify_companion_intent(
        safe_message, ctx["age_band"], body.character_id
    )
    ethics = evaluate_companion_ethics(safe_message)

    store = get_companion_store()
    trust_visit = apply_trust_visit(store, user_id, body.character_id)
    old_score = int(trust_visit["score"])
    delta = _trust_delta(
        safe_message,
        blocked,
        domain=cintent.domain,
        mood=cintent.mood,
        intent_id=cintent.intent_id,
    )
    new_score = _set_trust_score(user_id, body.character_id, old_score + delta)
    level, _ = _trust_level_info(new_score)
    cosmetic_unlock = _new_cosmetic_unlock(body.character_id, old_score, new_score)
    streak_days = int(trust_visit.get("streak_days") or 0)

    att_accepted, att_hint, att_errors = validate_and_format_attachments(
        [a.model_dump() for a in body.attachments],
        age_band=ctx["age_band"],
    )
    if body.attachments and att_errors and not att_accepted:
        raise HTTPException(status_code=422, detail="invalid_attachments")

    web_sources, web_hint = maybe_companion_web_search(
        safe_message, locale=body.response_language or "ru"
    )
    family_hint = build_family_context_hint(scope_key, ctx, store=store)

    if ethics.crisis:
        record_message(user_id)
        thread_id = resolve_thread_for_workspace(
            store, user_id, body.workspace_id, body.session_id
        )
        store.append_thread_message(user_id, thread_id, "user", safe_message, body.character_id)
        crisis_text = ethics.response_prefix
        store.append_thread_message(user_id, thread_id, "assistant", crisis_text, body.character_id)
        return CompanionChatResponse(
            response=crisis_text,
            character_id=body.character_id,
            emotion="comfort",
            animation_hint="idle",
            trust_delta=delta,
            trust_score=new_score,
            trust_level=level,
            confidence=1.0,
            intent="companion_crisis_support",
            companion_domain="feelings",
            companion_mood="comfort_needed",
            mood_confidence=1.0,
            security_expert_mode=security_expert_mode_active(profile),
            grounded=True,
            nsfw_blocked=True,
        )

    if blocked:
        return CompanionChatResponse(
            response=(
                "Я рядом и хочу, чтобы тебе было спокойно. "
                "Давай поговорим о чём-то дружелюбном — а про защиту в ALADDIN помогу, если спросишь."
            ),
            character_id=body.character_id,
            emotion="alert",
            animation_hint="shake_head",
            trust_delta=delta,
            trust_score=new_score,
            trust_level=level,
            confidence=1.0,
            intent="policy_block",
            companion_domain=cintent.domain,
            companion_mood=cintent.mood,
            grounded=True,
            nsfw_blocked=True,
        )

    record_message(user_id)
    thread_id = resolve_thread_for_workspace(
        store, user_id, body.workspace_id, body.session_id
    )
    store.append_thread_message(user_id, thread_id, "user", safe_message, body.character_id)

    playbook_hint = teen_playbook_hint(ctx["age_band"], cintent.domain, safe_message) or ""
    intent_hint = (
        f"\n[Companion routing: domain={cintent.domain}; mood={cintent.mood}; "
        f"confidence={cintent.mood_confidence:.2f}. {cintent.response_hint} "
        f"{ethics_hint_for_prompt(ethics)}{playbook_hint}]\n"
    )
    long_hint = build_long_context_hint(store, user_id, thread_id)
    prefixed = (
        _build_companion_system_prefix(body.character_id, profile, ctx["age_band"])
        + family_hint
        + long_hint
        + web_hint
        + att_hint
        + intent_hint
        + safe_message
    )
    try:
        use_orch = COMPANION_USE_ORCHESTRATOR
    except NameError:
        use_orch = False
    assistant_resp: ChatMessageResponse = await _invoke_companion_llm(
        prefixed,
        user_id,
        body.response_language,
        user,
        chat_mode=body.chat_mode,
    )
    if not mock_allowed() and is_probable_mock_response(assistant_resp.response):
        raise HTTPException(status_code=503, detail="ai_unavailable_no_mock_in_prod")

    safe_response, post_mod_blocked, _post_reason = moderate_companion_assistant_text(
        assistant_resp.response,
        app_id=ctx["app_id"],
        age_band=ctx["age_band"],
        age_verified=ctx["age_verified"],
        jwt_policy=ctx.get("content_policy"),
    )
    if post_mod_blocked:
        emotion = "alert"
        hint = "shake_head"
        intent_id = "post_moderation_block"
    else:
        emotion = emotion_for_companion(
            domain=cintent.domain,
            mood=cintent.mood,
            blocked=False,
            fallback_intent=assistant_resp.intent,
        )
        hint = _animation_hint_for_emotion(emotion)
        intent_id = cintent.intent_id

    store.append_thread_message(user_id, thread_id, "assistant", safe_response, body.character_id)
    m_key, m_enabled, _ = _memory_scope(http_request, user)
    if not post_mod_blocked:
        _maybe_record_memory(m_key, m_enabled, safe_message, safe_response)

    profile, show_bridge, bridge_suggestions = apply_social_bridge(
        profile,
        domain=cintent.domain,
        social_bridge_hint=ethics.social_bridge_hint,
        crisis=False,
        thread_id=thread_id,
    )
    store.set_profile(scope_key, profile)

    merged_sources = list(assistant_resp.sources or []) + list(web_sources)
    merged_tools = list(
        dict.fromkeys(
            (assistant_resp.tools_used or [])
            + tools_used_for_turn(
                web_search=bool(web_sources),
                attachments=bool(att_accepted),
                orchestrator=use_orch,
            )
        )
    )
    record_turn_cogs(
        store,
        user_id,
        input_chars=len(prefixed),
        output_chars=len(safe_response),
        chat_mode=body.chat_mode,
    )
    cogs_dash = build_cogs_dashboard(store, user_id)

    return CompanionChatResponse(
        response=safe_response,
        character_id=body.character_id,
        emotion=emotion,
        animation_hint=hint,
        trust_delta=delta,
        trust_score=new_score,
        trust_level=level,
        confidence=assistant_resp.confidence or 0.9,
        intent=intent_id,
        companion_domain=cintent.domain,
        companion_mood=cintent.mood,
        mood_confidence=cintent.mood_confidence,
        security_expert_mode=security_expert_mode_active(profile),
        grounded=assistant_resp.grounded,
        sources=merged_sources,
        tools_used=merged_tools,
        suggested_actions=assistant_resp.suggested_actions or [],
        cosmetic_unlocked=cosmetic_unlock,
        nsfw_blocked=True,
        follow_up_questions=assistant_resp.follow_up_questions or [],
        suggestions=assistant_resp.suggestions or [],
        show_social_bridge=show_bridge,
        social_bridge_suggestions=bridge_suggestions,
        trust_streak_days=streak_days,
        cogs_alert=bool(cogs_dash.get("alert_triggered")),
        chat_mode=body.chat_mode,
    )


@router.post("/stream")
async def companion_stream(
    body: CompanionStreamRequest,
    http_request: Request,
    user: dict = Depends(get_current_user),
):
    """
    SSE stream with resume (B16): cache tokenized reply; client sends resumeFromIndex on reconnect.
    Wire format matches assistant stream: data: {"token": "...", "done": false, "messageId": "..."}.
    """
    if not body.stream:
        raise HTTPException(status_code=400, detail="stream flag must be true")

    user_id = str(user.get("user_id") or "anonymous")
    message_id = (body.messageId or "").strip() or secrets.token_hex(16)
    store = get_companion_store()

    is_resume = body.context == "resume" or (
        body.resumeFromIndex > 0 and not body.message.strip()
    )

    if is_resume or body.resumeFromIndex > 0:
        cached = store.get_stream_cache(message_id, user_id=user_id)
        if not cached:
            raise HTTPException(status_code=404, detail="stream_cache_not_found")
        tokens: List[str] = list(cached["tokens"])
        meta: Dict[str, Any] = dict(cached["meta"])
    else:
        if not body.message.strip():
            raise HTTPException(status_code=422, detail="message_required_for_new_stream")
        chat_body = CompanionChatRequest(
            message=body.message,
            character_id=body.character_id,
            context=body.context or "companion",
            response_language=body.response_language,
            session_id=body.session_id,
            input_mode=body.input_mode,
            security_expert_mode=body.security_expert_mode,
            chat_mode=body.chat_mode,
            workspace_id=body.workspace_id,
            attachments=body.attachments,
        )
        resp = await companion_chat(chat_body, http_request, user)
        tokens = resp.response.split() if resp.response else []
        meta = resp.model_dump(mode="json")
        store.put_stream_cache(message_id, user_id, tokens, meta)

    start_index = min(body.resumeFromIndex, len(tokens))
    stream_tokens = tokens[start_index:]

    async def event_generator():
        hero_emotion = str(meta.get("emotion") or "thinking")
        thinking = {"emotion": hero_emotion, "done": False, "messageId": message_id}
        yield f"data: {json.dumps(thinking, ensure_ascii=False)}\n\n"
        for token in stream_tokens:
            payload = {"token": f"{token} ", "done": False, "messageId": message_id}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.02)
        done_payload = {**meta, "done": True, "messageId": message_id}
        yield f"data: {json.dumps(done_payload, ensure_ascii=False, default=str)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/consent", response_model=CompanionConsentResponse)
async def companion_get_consent(
    request: Request,
    user: dict = Depends(get_current_user),
    family_id: Optional[str] = Query(None, max_length=128),
) -> CompanionConsentResponse:
    """Текущие настройки согласия (семья + пользователь)."""
    from security.services.ai_platform.consent_resolver import family_consent_key

    fid = family_id or request.headers.get("x-aladdin-family-id")
    ctx = _user_app_context(user, fid)
    consent = ctx["parent_consent"]
    scope = "family" if fid and get_companion_store().get_consent(family_consent_key(fid)) else "user"
    return CompanionConsentResponse(
        recorded=True,
        memory_enabled=bool(consent.get("memory_enabled")),
        child_can_use_companion=bool(consent.get("child_can_use_companion", True)),
        allowed_characters=list(consent.get("allowed_characters") or ["aladdin", "unicorn"]),
        family_id=fid,
        scope=scope,
    )


@router.post("/consent", response_model=CompanionConsentResponse)
async def companion_set_consent(
    body: CompanionConsentRequest,
    user: dict = Depends(get_current_user),
) -> CompanionConsentResponse:
    from security.services.ai_platform.consent_resolver import family_consent_key, normalize_parent_consent

    user_id = user["user_id"] or "anonymous"
    store = get_companion_store()
    payload = normalize_parent_consent(
        {
            "memory_enabled": body.memory_enabled,
            "child_can_use_companion": body.child_can_use_companion,
            "allowed_characters": body.allowed_characters,
            "companion": body.child_can_use_companion,
            "memory": body.memory_enabled,
        }
    )
    store.set_consent(user_id, payload)
    scope = "user"
    fid = (body.family_id or "").strip()
    if fid:
        store.set_consent(family_consent_key(fid), payload)
        scope = "family"
    return CompanionConsentResponse(
        recorded=True,
        memory_enabled=body.memory_enabled,
        child_can_use_companion=body.child_can_use_companion,
        allowed_characters=body.allowed_characters,
        family_id=fid or None,
        scope=scope,
    )


@router.get("/profile", response_model=CompanionProfileResponse)
async def companion_get_profile(
    request: Request,
    user: dict = Depends(get_current_user),
) -> CompanionProfileResponse:
    storage_key, ctx = _family_scope_key(request, user)
    profile = _load_companion_profile(storage_key)
    age_band = str(ctx.get("age_band") or "parent")
    return CompanionProfileResponse(
        custom_instructions=profile["custom_instructions"],
        personality_preset=profile["personality_preset"],
        security_expert_mode=bool(profile.get("security_expert_mode")),
        equipped_cosmetic_id=profile.get("equipped_cosmetic_id") or "",
        equipped_cosmetic_character_id=profile.get("equipped_cosmetic_character_id") or "unicorn",
        storage_scope=storage_key,
        available_presets=list(available_personality_presets(age_band)),
    )


@router.put("/profile", response_model=CompanionProfileResponse)
async def companion_update_profile(
    body: CompanionProfileUpdateRequest,
    request: Request,
    user: dict = Depends(get_current_user),
) -> CompanionProfileResponse:
    storage_key, ctx = _family_scope_key(request, user)
    if ctx["age_band"] in ("child", "teen"):
        raise HTTPException(
            status_code=403,
            detail="Only a parent account can set companion instructions.",
        )
    current = _load_companion_profile(storage_key)
    if body.custom_instructions is not None:
        current["custom_instructions"] = body.custom_instructions.strip()[:2000]
    if body.personality_preset is not None:
        preset = body.personality_preset.strip()
        if preset not in PERSONALITY_PRESET_HINTS:
            raise HTTPException(status_code=422, detail="invalid_personality_preset")
        if ctx["age_band"] == "child" and preset == "witty":
            raise HTTPException(status_code=422, detail="witty_not_allowed_for_child")
        current["personality_preset"] = preset
    if body.security_expert_mode is not None:
        current["security_expert_mode"] = bool(body.security_expert_mode)
    user_id = str(user.get("user_id") or "anonymous")
    if body.equipped_cosmetic_character_id is not None:
        char = body.equipped_cosmetic_character_id.strip()
        if char not in VALID_CHARACTER_IDS:
            raise HTTPException(status_code=422, detail="invalid_equipped_character")
        current["equipped_cosmetic_character_id"] = char
    if body.equipped_cosmetic_id is not None:
        cosmetic_id = body.equipped_cosmetic_id.strip()[:64]
        char_id = current.get("equipped_cosmetic_character_id") or "unicorn"
        if cosmetic_id and not _cosmetic_unlocked(char_id, cosmetic_id, user_id):
            raise HTTPException(status_code=403, detail="cosmetic_locked")
        current["equipped_cosmetic_id"] = cosmetic_id
    get_companion_store().set_profile(storage_key, current)
    age_band = str(ctx.get("age_band") or "parent")
    return CompanionProfileResponse(
        custom_instructions=current["custom_instructions"],
        personality_preset=current["personality_preset"],
        security_expert_mode=bool(current.get("security_expert_mode")),
        equipped_cosmetic_id=current.get("equipped_cosmetic_id") or "",
        equipped_cosmetic_character_id=current.get("equipped_cosmetic_character_id") or "unicorn",
        storage_scope=storage_key,
        available_presets=list(available_personality_presets(age_band)),
    )


@router.post("/feedback", response_model=CompanionFeedbackResponse)
async def companion_message_feedback(
    body: CompanionFeedbackRequest,
    request: Request,
    user: dict = Depends(get_current_user),
) -> CompanionFeedbackResponse:
    """Thumb up/down on a companion reply (B15)."""
    try:
        from security.services.ai_platform.ai_prompt_gate import redact_feedback_only
    except ImportError:
        def redact_feedback_only(t):  # type: ignore
            return redact_pii(t or "").text if t else None

    user_id = str(user.get("user_id") or "anonymous")
    storage_key, ctx = _family_scope_key(request, user)
    if not companion_access_allowed(ctx["age_band"], ctx["parent_consent"]):
        raise HTTPException(status_code=403, detail="Companion disabled by parental consent.")

    rating = 5 if body.vote == "up" else 1
    assistant_redacted = redact_feedback_only(body.assistant_text) if body.assistant_text else None
    user_redacted = redact_feedback_only(body.user_query_text) if body.user_query_text else None

    store = get_companion_store()
    feedback_id = store.record_feedback(
        storage_key=storage_key,
        user_id=user_id,
        character_id=body.character_id,
        vote=body.vote,
        rating=rating,
        thread_id=body.thread_id,
        assistant_excerpt=assistant_redacted,
        user_excerpt=user_redacted,
    )

    delta = _feedback_trust_delta(body.vote)
    old_score = _trust_score(user_id, body.character_id)
    new_score = _set_trust_score(user_id, body.character_id, old_score + delta)

    _record_companion_feedback_analytics(
        user_id=user_id,
        session_id=body.thread_id,
        rating=rating,
        query_redacted=user_redacted or assistant_redacted,
    )

    return CompanionFeedbackResponse(
        recorded=True,
        vote=body.vote,
        rating=rating,
        trust_delta=delta,
        trust_score=new_score,
        feedback_id=feedback_id or None,
    )


@router.get("/memory", response_model=CompanionMemoryResponse)
async def companion_get_memory(
    request: Request,
    user: dict = Depends(get_current_user),
) -> CompanionMemoryResponse:
    storage_key, enabled, _ = _memory_scope(request, user)
    return _memory_items_response(get_companion_store(), storage_key, enabled)


@router.get("/memory/export", response_model=CompanionMemoryExportResponse)
async def companion_export_memory(
    request: Request,
    user: dict = Depends(get_current_user),
) -> CompanionMemoryExportResponse:
    """GDPR-style export of redacted companion memory for the family scope."""
    storage_key, enabled, _ = _memory_scope(request, user)
    payload = _memory_items_response(get_companion_store(), storage_key, enabled)
    return CompanionMemoryExportResponse(
        exported_at=datetime.utcnow(),
        storage_scope=storage_key,
        memory_enabled=payload.memory_enabled,
        item_count=payload.item_count,
        items=payload.items,
    )


@router.delete("/memory")
async def companion_delete_memory(
    request: Request,
    user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    from security.services.ai_platform.consent_resolver import (
        family_consent_key,
        normalize_parent_consent,
    )

    storage_key, _, ctx = _memory_scope(request, user)
    store = get_companion_store()
    removed = store.delete_all_memory_items(storage_key)
    consent = normalize_parent_consent(ctx["parent_consent"])
    consent["memory_enabled"] = False
    consent["memory"] = False
    user_id = str(user.get("user_id") or "anonymous")
    fid = ctx.get("family_id")
    if fid:
        store.set_consent(family_consent_key(fid), consent)
    else:
        store.set_consent(user_id, consent)
    return {"deleted": True, "items_removed": removed, "memory_enabled": False}


@router.get("/cosmetics", response_model=CompanionCosmeticsResponse)
async def companion_cosmetics(
    character_id: str = Query(..., pattern=CHARACTER_ID_PATTERN),
    user: dict = Depends(get_current_user),
) -> CompanionCosmeticsResponse:
    user_id = user["user_id"] or "anonymous"
    score = _trust_score(user_id, character_id)
    level, _ = _trust_level_info(score)
    items: List[CompanionCosmeticDTO] = []
    for item in COSMETICS_CATALOG.get(character_id, []):
        items.append(
            CompanionCosmeticDTO(
                id=item["id"],
                title=item["title"],
                trust_level=item["trust_level"],
                unlocked=item["trust_level"] <= level,
            )
        )
    return CompanionCosmeticsResponse(character_id=character_id, cosmetics=items)


class CompanionLegalSection(BaseModel):
    id: str
    title: str
    body: str


class CompanionLegalResponse(BaseModel):
    version: str = "2026-05-30"
    locale: str = "ru"
    app_id: str = "aladdin_family"
    sections: List[CompanionLegalSection]


@router.get("/legal", response_model=CompanionLegalResponse)
async def companion_legal(
    locale: str = Query("ru", max_length=8),
) -> CompanionLegalResponse:
    """P1-09 — static legal copy for in-app disclosure (COPPA / 152-ФЗ)."""
    _ = locale
    sections = [
        CompanionLegalSection(
            id="ai_disclosure",
            title="Искусственный интеллект",
            body=(
                "Ответы героев генерируются ИИ на серверах ALADDIN. "
                "Это не живой человек. Ребёнок не должен передавать пароли, адрес, телефон "
                "или данные документов."
            ),
        ),
        CompanionLegalSection(
            id="parental_control",
            title="Родительский контроль",
            body=(
                "Родитель включает «Разговор с героем» в настройках семьи, выбирает героев "
                "и может отключить память компаньона. Без согласия ребёнок не получает доступ."
            ),
        ),
        CompanionLegalSection(
            id="coppa_152fz",
            title="COPPA и 152-ФЗ",
            body=(
                "Обработка данных детей — с согласия законного представителя (152-ФЗ). "
                "Мы не используем данные ребёнка для рекламы. Память компаньона — опциональна, "
                "экспорт и удаление доступны в настройках."
            ),
        ),
        CompanionLegalSection(
            id="data_retention",
            title="Хранение и безопасность",
            body=(
                "Диалоги и счётчики использования хранятся для лимитов тарифа и качества сервиса. "
                "Тексты проходят фильтрацию PII перед отправкой в облако."
            ),
        ),
        CompanionLegalSection(
            id="voice_recognition_primary",
            title="Голосовой ввод (основной путь)",
            body=(
                "Когда вы говорите с героем, речь сначала распознаётся на iPhone через сервисы Apple "
                "(Siri / «Распознавание речи»). Аудио обрабатывается по правилам Apple. "
                "ALADDIN получает только текст, если распознавание удалось."
            ),
        ),
        CompanionLegalSection(
            id="voice_stt_fallback",
            title="Запасное распознавание на сервере ALADDIN",
            body=(
                "Если на устройстве текст получить не удалось, приложение может один раз отправить "
                "короткую запись голоса (до 15 секунд) на сервер ALADDIN для преобразования в текст. "
                "Запись обрабатывается в памяти и не сохраняется после ответа (0 секунд хранения аудио). "
                "На сервер уходит только текст результата — как если бы вы напечатали сообщение. "
                "Запасной путь работает только при включённом «Облачном AI-помощнике» в настройках."
            ),
        ),
        CompanionLegalSection(
            id="voice_privacy_summary",
            title="Кратко о голосе",
            body=(
                "• Основной путь: Apple (Siri cloud) на телефоне.\n"
                "• Запасной путь: ALADDIN VPS — только если Apple не справилась.\n"
                "• Аудио на сервере ALADDIN не копится «навсегда» — обработали и удалили.\n"
                "• Текст диалога — по общим правилам компаньона (память, лимиты тарифа)."
            ),
        ),
        CompanionLegalSection(
            id="store_disclosure",
            title="Для App Store",
            body=(
                "Приложение содержит AI Companion для детей с родительским gate. "
                "Категория: Family / Kids. Возрастной рейтинг согласно политике Apple для "
                "приложений с пользовательским контентом и ИИ."
            ),
        ),
    ]
    return CompanionLegalResponse(sections=sections)
