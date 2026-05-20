# -*- coding: utf-8 -*-
"""
AI Assistant API Router
-----------------------
FastAPI endpoints для интеграции AI Assistant с мобильным приложением iOS.

Использование:
    В main.py добавить:
    from security.api.routers.ai_assistant_router import router as ai_assistant_router
    app.include_router(ai_assistant_router)

Дата создания: 10 февраля 2026
Версия: 1.0.0
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Query, Depends, Request
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import jwt
import logging
import sys
import os
import asyncio
import json

# SFM Adapter import
backend_path = "/opt/aladdin-backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Add current directory to path for local development
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from sfm_adapter import sfm_adapter
    SFM_ADAPTER_AVAILABLE = True
    print("✅ SFM Adapter loaded successfully")
except ImportError as e:
    SFM_ADAPTER_AVAILABLE = False
    sfm_adapter = None
    print("❌ SFM Adapter not available: {}".format(e))
    print("   Current sys.path: {}".format(sys.path))

try:
    from security.services.ai_response_helpers import (
        dev_fallback_chat,
        is_probable_mock_response,
        mock_allowed,
        raise_service_unavailable,
        require_sfm_adapter,
    )
    from security.services.ai_capabilities_manifest import static_capabilities_payload
    from security.services.ai_intent_router import classify_intent, intent_requires_live_sfm, KB_ONLY_INTENTS
    from security.services.hermes_client import chat_once as hermes_chat_once, hermes_available
except ImportError:
    from ai_response_helpers import (  # type: ignore
        dev_fallback_chat,
        is_probable_mock_response,
        mock_allowed,
        raise_service_unavailable,
        require_sfm_adapter,
    )
    from ai_capabilities_manifest import static_capabilities_payload  # type: ignore
    from ai_intent_router import classify_intent, intent_requires_live_sfm, KB_ONLY_INTENTS  # type: ignore
    from hermes_client import chat_once as hermes_chat_once, hermes_available  # type: ignore

try:
    from security.services.ai_prompt_gate import (
        PIIPromptBlockedError,
        prepare_for_llm_prompt,
        prepare_optional_for_llm,
        redact_feedback_only,
    )
    from security.services.ai_llm_prompt_builder import (
        attach_sfm_aggregates_to_params,
        build_ai_chat_sfm_payload,
    )
except ImportError:
    from ai_prompt_gate import (  # type: ignore
        PIIPromptBlockedError,
        prepare_for_llm_prompt,
        prepare_optional_for_llm,
        redact_feedback_only,
    )
    from ai_llm_prompt_builder import (  # type: ignore
        attach_sfm_aggregates_to_params,
        build_ai_chat_sfm_payload,
    )

# JWT Configuration (single source: app.auth)
try:
    from app.auth import JWT_SECRET, JWT_ALGORITHM
except ImportError:
    JWT_SECRET = os.environ["JWT_SECRET"]
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
security = HTTPBearer()

logger = logging.getLogger(__name__)

AI_BACKEND = os.getenv("AI_BACKEND", "sfm").strip().lower()

# Создаем FastAPI Router
router = APIRouter(prefix="/api/ai/assistant", tags=["AI Assistant"])


# =============================================================================
# JWT Authentication & Rate Limiting
# =============================================================================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Проверяет JWT токен и возвращает данные пользователя с уровнем подписки"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # Извлекаем subscription данные из payload
        subscription = payload.get("subscription", {})
        level = subscription.get("level", "free")
        limits = subscription.get("limits", {})

        return {
            "user_id": payload.get("sub"),
            "email": payload.get("email"),
            "subscription_level": level,
            "limits": limits,
            "payload": payload
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Rate limiting storage (in production use Redis)
rate_limit_storage = {}

def check_rate_limit(user_id: str, subscription_level: str) -> bool:
    """Проверяет rate limit для пользователя"""
    now = datetime.now()
    today = now.date()

    if user_id not in rate_limit_storage:
        rate_limit_storage[user_id] = {"date": today, "count": 0}

    user_data = rate_limit_storage[user_id]

    # Сбрасываем счетчик каждый день
    if user_data["date"] != today:
        user_data["date"] = today
        user_data["count"] = 0

    # Проверяем лимиты по уровню подписки
    if subscription_level == "free":
        limit = 10  # 10 сообщений в день
    elif subscription_level == "trial":
        limit = 50  # 50 сообщений в день для trial
    else:  # premium
        limit = float('inf')  # unlimited

    if user_data["count"] >= limit:
        return False

    user_data["count"] += 1
    return True

# =============================================================================
# Pydantic модели для запросов и ответов
# =============================================================================

class ChatMessageRequest(BaseModel):
    """Запрос на отправку сообщения AI помощнику"""
    message: str = Field(..., description="Сообщение пользователя", min_length=1, max_length=2000)
    context: str = Field("general", description="Контекст разговора", example="general")
    user_id: Optional[str] = Field(None, description="ID пользователя")
    timestamp: Optional[datetime] = Field(None, description="Временная метка")
    response_language: Optional[str] = Field(None, description="Предпочитаемый язык ответа (ru, en, …)")


class StreamRequest(BaseModel):
    message: str = Field("", description="Сообщение пользователя или пусто для resume", max_length=4000)
    context: str = Field("general", description="Контекст стрима")
    resumeFromIndex: int = Field(0, ge=0)
    messageId: Optional[str] = None
    stream: bool = True
    response_language: Optional[str] = Field(None, description="Предпочитаемый язык ответа (en, ru, …)")


class SuggestedAction(BaseModel):
    id: str = Field(..., description="Action id for iOS deep link")
    title: str = Field(..., description="Button label")


class ChatMessageResponse(BaseModel):
    """Ответ AI помощника"""
    response: str = Field(..., description="Ответ AI помощника")
    confidence: float = Field(0.95, description="Уровень уверенности (0-1)", ge=0, le=1)
    suggestions: List[str] = Field(default_factory=list, description="Предложения для пользователя")
    follow_up_questions: List[str] = Field(default_factory=list, description="Дополнительные вопросы")
    timestamp: Optional[datetime] = Field(None, description="Временная метка")
    intent: Optional[str] = Field(None, description="Classified intent id")
    grounded: Optional[bool] = Field(None, description="Answer used SFM/tools")
    tools_used: List[str] = Field(default_factory=list, description="SFM tools invoked")
    suggested_actions: List[SuggestedAction] = Field(default_factory=list, description="Deep link actions")


class ChatHistoryResponse(BaseModel):
    """История разговоров с AI помощником"""
    conversations: List[Dict[str, Any]] = Field(..., description="Список разговоров")
    total: int = Field(..., description="Общее количество разговоров")


class FeedbackRequest(BaseModel):
    """Запрос на отправку обратной связи"""
    rating: int = Field(..., description="Оценка (1-5)", ge=1, le=5)
    comment: Optional[str] = Field(None, description="Комментарий", max_length=1000)
    message_id: Optional[str] = Field(None, description="ID сообщения")
    query_text: Optional[str] = Field(None, description="Исходный вопрос", max_length=2000)
    resolved_by: Optional[str] = Field(None, description="faq|ai|unknown", max_length=64)
    faq_id: Optional[str] = Field(None, description="FAQ id", max_length=128)
    session_id: Optional[str] = Field(None, description="ID сессии клиента", max_length=128)


class FeedbackResponse(BaseModel):
    """Ответ на отправку обратной связи"""
    feedback_recorded: bool = Field(..., description="Обратная связь записана")
    average_rating: float = Field(..., description="Средняя оценка")
    total_feedbacks: int = Field(..., description="Общее количество отзывов")


class CapabilitiesResponse(BaseModel):
    """Возможности AI помощника"""
    features: List[str] = Field(..., description="Список возможностей")
    languages: List[str] = Field(..., description="Поддерживаемые языки")
    response_time: str = Field(..., description="Время отклика")
    accuracy: str = Field(..., description="Точность ответов")


class AnalyzeThreatRequest(BaseModel):
    """Запрос на анализ угрозы"""
    threat: str = Field(..., description="Описание угрозы", min_length=1, max_length=1000)
    type: Optional[str] = Field(None, description="Тип угрозы")
    context: Optional[str] = Field(None, description="Дополнительный контекст")


class AnalyzeThreatResponse(BaseModel):
    """Результат анализа угрозы"""
    threat_level: str = Field(..., description="Уровень угрозы (low, medium, high, critical)")
    analysis: str = Field(..., description="Анализ угрозы")
    actions_taken: List[str] = Field(default_factory=list, description="Предпринятые действия")
    prevention_tips: List[str] = Field(default_factory=list, description="Советы по предотвращению")


class RecommendationsResponse(BaseModel):
    """Персональные рекомендации"""
    personal_recommendations: List[str] = Field(..., description="Персональные рекомендации")
    security_score: int = Field(..., description="Оценка безопасности (0-100)", ge=0, le=100)
    improvement_areas: List[str] = Field(default_factory=list, description="Области для улучшения")


class ReportIncidentRequest(BaseModel):
    """Запрос на сообщение об инциденте"""
    type: str = Field(..., description="Тип инцидента", min_length=1)
    description: str = Field(..., description="Описание инцидента", min_length=1, max_length=2000)
    severity: str = Field("medium", description="Серьезность (low, medium, high, critical)")


class ReportIncidentResponse(BaseModel):
    """Ответ на сообщение об инциденте"""
    incident_id: str = Field(..., description="ID инцидента")
    status: str = Field(..., description="Статус обработки")
    estimated_resolution: str = Field(..., description="Оценка времени решения")
    assigned_specialist: str = Field(..., description="Назначенный специалист")
    follow_up_actions: List[str] = Field(default_factory=list, description="Последующие действия")


class SecurityTipsResponse(BaseModel):
    """Советы по безопасности"""
    daily_tips: List[str] = Field(..., description="Ежедневные советы")
    weekly_focus: str = Field(..., description="Фокус недели")
    monthly_goal: str = Field(..., description="Цель месяца")


# =============================================================================
# Helper функции
# =============================================================================

def _hermes_skill_for_intent(intent_id: str) -> Optional[str]:
    if intent_id in KB_ONLY_INTENTS or intent_id in (
        "general",
        "app_help",
        "e2ee_howto",
        "tariff_explain",
        "parental_howto",
    ):
        return "aladdin-security-kb"
    return None


def _route_via_hermes(intent_id: str, kb_only: bool) -> bool:
    """KB / open questions → Hermes skill aladdin-security-kb when available."""
    if kb_only:
        return True
    if intent_id in ("general", "app_help"):
        return True
    return AI_BACKEND == "hermes" and intent_id in KB_ONLY_INTENTS


def _try_hermes_answer(
    *,
    cloud_message: str,
    intent_id: str,
) -> Optional[ChatMessageResponse]:
    if not hermes_available():
        return None
    skill = _hermes_skill_for_intent(intent_id)
    ok, text, err = hermes_chat_once(cloud_message, skill=skill)
    if not ok or not text.strip() or is_probable_mock_response(text):
        logger.warning("Hermes fallback unavailable intent=%s err=%s", intent_id, err)
        return None
    tools = [f"hermes:{skill}"] if skill else ["hermes"]
    return _chat_response_from_hermes(
        response_text=text,
        intent_id=intent_id,
        tools_used=tools,
    )


def _chat_response_from_hermes(
    *,
    response_text: str,
    intent_id: str,
    tools_used: List[str],
) -> ChatMessageResponse:
    return ChatMessageResponse(
        response=response_text,
        confidence=0.8,
        suggestions=[],
        follow_up_questions=[],
        timestamp=datetime.now(),
        intent=intent_id,
        grounded=False,
        tools_used=tools_used,
        suggested_actions=_suggested_actions_for_intent(intent_id),
    )


def _suggested_actions_for_intent(intent_id: str) -> List[SuggestedAction]:
    mapping = {
        "protection_status": [SuggestedAction(id="open_main", title="Главная")],
        "threats_summary": [SuggestedAction(id="open_analytics", title="Аналитика")],
        "family_overview": [SuggestedAction(id="open_family", title="Семья")],
        "network_vpn_status": [SuggestedAction(id="open_network", title="Защита сети")],
        "tariff_explain": [SuggestedAction(id="open_tariffs", title="Тарифы")],
        "e2ee_howto": [SuggestedAction(id="open_family_chat", title="Семейный чат")],
        "incident_analyze": [SuggestedAction(id="open_threats", title="Угрозы")],
        "recommendations": [SuggestedAction(id="open_settings", title="Настройки")],
    }
    return mapping.get(intent_id, [])


def _chat_response_from_sfm(
    *,
    result: dict,
    intent_id: str,
    tools_used: List[str],
) -> ChatMessageResponse:
    response_text = str(result.get("response") or "").strip()
    if not response_text and not mock_allowed():
        raise_service_unavailable()
    grounded = bool(tools_used) and bool(response_text)
    return ChatMessageResponse(
        response=response_text or dev_fallback_chat(intent_id)["response"],
        confidence=float(result.get("confidence", 0.85 if grounded else 0.5)),
        suggestions=result.get("suggestions") or [],
        follow_up_questions=result.get("follow_up_questions") or [],
        timestamp=datetime.now(),
        intent=intent_id,
        grounded=grounded,
        tools_used=tools_used,
        suggested_actions=_suggested_actions_for_intent(intent_id),
    )


def _llm_message_or_http422(raw: str, *, field: str, allow_empty: bool = False) -> str:
    """E2.2: redact + block residual PII before SFM/LLM."""
    if allow_empty and not (raw or "").strip():
        return ""
    try:
        return prepare_for_llm_prompt(raw, field_name=field).text
    except PIIPromptBlockedError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _safe_record_chat_exchange(
    *,
    user_id: Optional[str],
    user_message_redacted: str,
    assistant_message: str,
    ui_context: str,
    session_id: Optional[str] = None,
    message_id: Optional[str] = None,
    sfm_aggregates: Optional[dict] = None,
) -> None:
    if not user_message_redacted.strip():
        return
    try:
        from security.services.ai_history_store import record_chat_exchange

        record_chat_exchange(
            user_id=user_id,
            user_message_redacted=user_message_redacted,
            assistant_message=assistant_message,
            ui_context=ui_context,
            session_id=session_id,
            message_id=message_id,
            sfm_aggregates=sfm_aggregates,
        )
    except Exception as exc:
        logger.warning("AI history persist failed: %s", exc)


def _safe_record_feedback_analytics(
    *,
    user_id: Optional[str],
    query_redacted: Optional[str],
    ui_context: str = "feedback",
    session_id: Optional[str] = None,
    rating: Optional[int] = None,
    faq_id: Optional[str] = None,
    resolved_by: Optional[str] = None,
) -> None:
    try:
        from security.services.ai_history_store import record_analytics_event

        record_analytics_event(
            user_id=user_id,
            question_redacted=query_redacted,
            ui_context=ui_context,
            session_id=session_id,
            rating=rating,
            faq_id=faq_id,
            resolved_by=resolved_by,
        )
    except Exception as exc:
        logger.warning("AI feedback analytics persist failed: %s", exc)


# =============================================================================
# API Endpoints (8 штук)
# =============================================================================

# 1. POST /api/ai/assistant/chat - Отправка сообщения AI помощнику
@router.post("/chat", response_model=ChatMessageResponse)
async def ai_assistant_chat(request: ChatMessageRequest, user: dict = Depends(get_current_user)) -> ChatMessageResponse:
    """
    AI помощник - обработка сообщений пользователя
    """
    user_id = user["user_id"] or "anonymous"
    subscription_level = user["subscription_level"]

    if not check_rate_limit(user_id, subscription_level):
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded for {subscription_level} subscription. Please upgrade or try again tomorrow."
        )

    try:
        intent = classify_intent(request.message, request.context)
        cloud_message = _llm_message_or_http422(request.message, field="message")

        if _route_via_hermes(intent.intent_id, intent.kb_only) and hermes_available():
            skill = _hermes_skill_for_intent(intent.intent_id)
            ok, text, err = hermes_chat_once(cloud_message, skill=skill)
            if ok and text.strip() and not is_probable_mock_response(text):
                tools = [f"hermes:{skill}"] if skill else ["hermes"]
                response = _chat_response_from_hermes(
                    response_text=text,
                    intent_id=intent.intent_id,
                    tools_used=tools,
                )
                if cloud_message.strip():
                    _safe_record_chat_exchange(
                        user_id=user_id,
                        user_message_redacted=cloud_message,
                        assistant_message=response.response,
                        ui_context=request.context,
                    )
                return response
            logger.warning("Hermes primary path failed intent=%s err=%s", intent.intent_id, err)
            if intent.kb_only and not mock_allowed():
                raise_service_unavailable()

        if intent_requires_live_sfm(intent.intent_id):
            require_sfm_adapter(SFM_ADAPTER_AVAILABLE and sfm_adapter is not None)

        if not SFM_ADAPTER_AVAILABLE or not sfm_adapter:
            if mock_allowed():
                fb = dev_fallback_chat(request.context)
                return ChatMessageResponse(
                    response=fb["response"],
                    confidence=fb["confidence"],
                    suggestions=fb.get("suggestions", []),
                    follow_up_questions=fb.get("follow_up_questions", []),
                    timestamp=datetime.now(),
                    intent=intent.intent_id,
                    grounded=False,
                )
            raise_service_unavailable()

        cloud_message = _llm_message_or_http422(request.message, field="message")
        data = build_ai_chat_sfm_payload(
            message=cloud_message,
            ui_context=request.context,
            user_id=request.user_id or user_id,
            execute_fn=sfm_adapter.execute_function,
            timestamp=request.timestamp,
            response_language=request.response_language,
        )
        success, result, message = sfm_adapter.execute_function("ai_assistant_chat", data)

        if not success:
            logger.warning("SFM ai_assistant_chat failed: %s", message)
            hermes_resp = _try_hermes_answer(cloud_message=cloud_message, intent_id=intent.intent_id)
            if hermes_resp:
                return hermes_resp
            raise_service_unavailable()

        if not isinstance(result, dict):
            raise_service_unavailable()

        tools_used = list(data.get("sfm_context_sources") or []) or ["ai_assistant_chat"]
        response = _chat_response_from_sfm(
            result=result,
            intent_id=intent.intent_id,
            tools_used=tools_used,
        )
        if is_probable_mock_response(response.response):
            logger.warning("SFM returned probable mock for intent=%s", intent.intent_id)
            hermes_resp = _try_hermes_answer(cloud_message=cloud_message, intent_id=intent.intent_id)
            if hermes_resp:
                response = hermes_resp
            elif not mock_allowed():
                raise_service_unavailable()
        if cloud_message.strip() and response.response.strip():
            _safe_record_chat_exchange(
                user_id=user_id,
                user_message_redacted=cloud_message,
                assistant_message=response.response,
                ui_context=request.context,
                sfm_aggregates=data.get("sfm_aggregates"),
            )
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Ошибка при обработке сообщения: %s", e)
        raise_service_unavailable()


@router.post("/stream")
async def ai_assistant_stream(request: StreamRequest, user: dict = Depends(get_current_user)):
    """
    SSE stream endpoint for iOS token-by-token rendering.
    """
    if not request.stream:
        raise HTTPException(status_code=400, detail="stream flag must be true")

    user_id = user["user_id"] or "anonymous"
    response_text = ""
    cloud_message = ""
    sfm_aggregates_snapshot: Optional[dict] = None

    intent = classify_intent(request.message or "", request.context)
    if _route_via_hermes(intent.intent_id, intent.kb_only):
        if not hermes_available():
            raise_service_unavailable()
        cloud_message = _llm_message_or_http422(
            request.message,
            field="message",
            allow_empty=(request.context == "resume" or request.resumeFromIndex > 0),
        )
        skill = _hermes_skill_for_intent(intent.intent_id)
        ok, text, err = hermes_chat_once(cloud_message, skill=skill)
        if not ok or not text.strip():
            logger.warning("Hermes stream path failed: %s", err)
            raise_service_unavailable()
        response_text = text
    elif intent_requires_live_sfm(intent.intent_id):
        require_sfm_adapter(SFM_ADAPTER_AVAILABLE and sfm_adapter is not None)

    if not response_text and (not SFM_ADAPTER_AVAILABLE or not sfm_adapter):
        if mock_allowed():
            response_text = dev_fallback_chat(request.context)["response"]
        else:
            raise_service_unavailable()
    elif not response_text:
        cloud_message = _llm_message_or_http422(
            request.message,
            field="message",
            allow_empty=(request.context == "resume" or request.resumeFromIndex > 0),
        )
        data = build_ai_chat_sfm_payload(
            message=cloud_message,
            ui_context=request.context,
            user_id=user_id,
            execute_fn=sfm_adapter.execute_function,
            stream=True,
            message_id=request.messageId,
            resume_from_index=request.resumeFromIndex,
            response_language=request.response_language,
        )
        success, result, message = sfm_adapter.execute_function("ai_assistant_chat", data)
        if not success:
            logger.warning("SFM stream failed: %s", message)
            raise_service_unavailable()
        response_text = str((result or {}).get("response") or "").strip()
        if not response_text and not mock_allowed():
            raise_service_unavailable()
        if not response_text:
            response_text = dev_fallback_chat(request.context)["response"]
        sfm_aggregates_snapshot = data.get("sfm_aggregates")

    if cloud_message.strip() and response_text.strip():
        _safe_record_chat_exchange(
            user_id=user_id,
            user_message_redacted=cloud_message,
            assistant_message=response_text,
            ui_context=request.context,
            message_id=request.messageId,
            sfm_aggregates=sfm_aggregates_snapshot,
        )

    tokens = response_text.split()
    start_index = min(request.resumeFromIndex, len(tokens))
    stream_tokens = tokens[start_index:]

    async def _event_generator():
        for token in stream_tokens:
            payload = {"token": f"{token} ", "done": False, "messageId": request.messageId}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            await asyncio.sleep(0.02)
        yield "data: {\"done\": true}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        _event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# 2. GET /api/ai/assistant/history - История разговоров
@router.get("/history", response_model=ChatHistoryResponse)
async def ai_assistant_history(
    user_id: Optional[str] = Query(None, description="ID пользователя"),
    limit: int = Query(50, description="Максимальное количество записей", ge=1, le=100)
) -> ChatHistoryResponse:
    """
    История разговоров с AI помощником
    
    Args:
        user_id: ID пользователя (опционально)
        limit: Максимальное количество записей
    
    Returns:
        История разговоров
    """
    try:
        from security.services.ai_history_store import list_conversation_summaries

        conversations = list_conversation_summaries(user_id, limit)
        return ChatHistoryResponse(conversations=conversations, total=len(conversations))
    except Exception as e:
        logger.warning("AI history store unavailable: %s", e)
        return ChatHistoryResponse(conversations=[], total=0)


# 3. POST /api/ai/assistant/feedback - Обратная связь
@router.post("/feedback", response_model=FeedbackResponse)
async def ai_assistant_feedback(
    request: FeedbackRequest,
    user: dict = Depends(get_current_user),
) -> FeedbackResponse:
    """
    Обратная связь по работе AI помощника
    
    Args:
        request: Запрос с оценкой и комментарием
    
    Returns:
        Результат сохранения обратной связи
    """
    try:
        user_id = user["user_id"] or "anonymous"
        query_redacted = redact_feedback_only(request.query_text) if request.query_text else None
        comment_redacted = redact_feedback_only(request.comment) if request.comment else None

        _safe_record_feedback_analytics(
            user_id=user_id,
            query_redacted=query_redacted or comment_redacted,
            ui_context="feedback",
            session_id=request.session_id,
            rating=request.rating,
            faq_id=request.faq_id,
            resolved_by=request.resolved_by,
        )

        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "rating": request.rating,
                "comment": comment_redacted,
                "message_id": request.message_id
            }
            success, result, message = sfm_adapter.execute_function("ai_assistant_feedback", data)
            
            if success and isinstance(result, dict):
                return FeedbackResponse(
                    feedback_recorded=True,
                    average_rating=float(result.get("average_rating", 0.0)),
                    total_feedbacks=int(result.get("total_feedbacks", 0)),
                )
            logger.warning("SFM ai_assistant_feedback failed: %s", message)

        return FeedbackResponse(feedback_recorded=True, average_rating=0.0, total_feedbacks=0)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Ошибка при сохранении обратной связи: %s", e)
        return FeedbackResponse(feedback_recorded=False, average_rating=0.0, total_feedbacks=0)


# 4. GET /api/ai/assistant/capabilities - Возможности AI помощника
@router.get("/capabilities", response_model=CapabilitiesResponse)
async def ai_assistant_capabilities() -> CapabilitiesResponse:
    """
    Возможности AI помощника
    
    Returns:
        Список возможностей и характеристик AI помощника
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            success, result, message = sfm_adapter.execute_function("ai_assistant_capabilities", {})
            if success and isinstance(result, dict) and result.get("features"):
                return CapabilitiesResponse(
                    features=result.get("features", []),
                    languages=result.get("languages", ["Русский", "English"]),
                    response_time=result.get("response_time", "variable"),
                    accuracy=result.get("accuracy", "SFM-backed"),
                )
            logger.warning("SFM capabilities unavailable: %s", message)

        manifest = static_capabilities_payload()
        return CapabilitiesResponse(**manifest)
    except Exception as e:
        logger.error("Ошибка при получении возможностей: %s", e)
        manifest = static_capabilities_payload()
        return CapabilitiesResponse(**manifest)


# 5. POST /api/ai/assistant/analyze_threat - Анализ угрозы
@router.post("/analyze_threat", response_model=AnalyzeThreatResponse)
async def ai_assistant_analyze_threat(request: AnalyzeThreatRequest) -> AnalyzeThreatResponse:
    """
    AI анализ конкретной угрозы
    
    Args:
        request: Запрос с описанием угрозы
    
    Returns:
        Результат анализа угрозы
    """
    try:
        require_sfm_adapter(SFM_ADAPTER_AVAILABLE and sfm_adapter is not None)
        if not SFM_ADAPTER_AVAILABLE or not sfm_adapter:
            raise_service_unavailable()

        data = attach_sfm_aggregates_to_params(
            {
                "threat": _llm_message_or_http422(request.threat, field="threat"),
                "type": request.type,
                "context": prepare_optional_for_llm(request.context, field_name="context"),
            },
            sfm_adapter.execute_function,
        )
        success, result, message = sfm_adapter.execute_function("ai_assistant_analyze_threat", data)

        if not success or not isinstance(result, dict):
            logger.warning("SFM analyze_threat failed: %s", message)
            raise_service_unavailable()

        return AnalyzeThreatResponse(
            threat_level=result.get("threat_level", "unknown"),
            analysis=result.get("analysis", ""),
            actions_taken=result.get("actions_taken", []),
            prevention_tips=result.get("prevention_tips", []),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Ошибка при анализе угрозы: %s", e)
        raise_service_unavailable()


# 6. GET /api/ai/assistant/recommendations - Персональные рекомендации
@router.get("/recommendations", response_model=RecommendationsResponse)
async def ai_assistant_recommendations(
    user_id: Optional[str] = Query(None, description="ID пользователя")
) -> RecommendationsResponse:
    """
    Персональные рекомендации по безопасности
    
    Args:
        user_id: ID пользователя (опционально)
    
    Returns:
        Персональные рекомендации и оценка безопасности
    """
    try:
        require_sfm_adapter(SFM_ADAPTER_AVAILABLE and sfm_adapter is not None)
        if not SFM_ADAPTER_AVAILABLE or not sfm_adapter:
            raise_service_unavailable()

        success, result, message = sfm_adapter.execute_function(
            "ai_assistant_recommendations", {"user_id": user_id}
        )
        if not success or not isinstance(result, dict):
            logger.warning("SFM recommendations failed: %s", message)
            raise_service_unavailable()

        return RecommendationsResponse(
            personal_recommendations=result.get("personal_recommendations", []),
            security_score=int(result.get("security_score", 0)),
            improvement_areas=result.get("improvement_areas", []),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Ошибка при получении рекомендаций: %s", e)
        raise_service_unavailable()


# 7. POST /api/ai/assistant/report_incident - Сообщить об инциденте
@router.post("/report_incident", response_model=ReportIncidentResponse)
async def ai_assistant_report_incident(request: ReportIncidentRequest) -> ReportIncidentResponse:
    """
    Сообщить о инциденте через AI помощника
    
    Args:
        request: Запрос с описанием инцидента
    
    Returns:
        Информация о зарегистрированном инциденте
    """
    try:
        require_sfm_adapter(SFM_ADAPTER_AVAILABLE and sfm_adapter is not None)
        if not SFM_ADAPTER_AVAILABLE or not sfm_adapter:
            raise_service_unavailable()

        data = attach_sfm_aggregates_to_params(
            {
                "type": request.type,
                "description": _llm_message_or_http422(request.description, field="description"),
                "severity": request.severity,
            },
            sfm_adapter.execute_function,
        )
        success, result, message = sfm_adapter.execute_function("ai_assistant_report_incident", data)

        if not success or not isinstance(result, dict):
            logger.warning("SFM report_incident failed: %s", message)
            raise_service_unavailable()

        return ReportIncidentResponse(
            incident_id=result.get("incident_id", f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            status=result.get("status", "received"),
            estimated_resolution=result.get("estimated_resolution", "pending"),
            assigned_specialist=result.get("assigned_specialist", "security-team"),
            follow_up_actions=result.get("follow_up_actions", []),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Ошибка при регистрации инцидента: %s", e)
        raise_service_unavailable()


# 8. GET /api/ai/assistant/security_tips - Советы по безопасности
@router.get("/security_tips", response_model=SecurityTipsResponse)
async def ai_assistant_security_tips() -> SecurityTipsResponse:
    """
    Полезные советы по безопасности от AI
    
    Returns:
        Ежедневные советы, фокус недели и цель месяца
    """
    try:
        require_sfm_adapter(SFM_ADAPTER_AVAILABLE and sfm_adapter is not None)
        if not SFM_ADAPTER_AVAILABLE or not sfm_adapter:
            raise_service_unavailable()

        success, result, message = sfm_adapter.execute_function("ai_assistant_security_tips", {})
        if not success or not isinstance(result, dict):
            logger.warning("SFM security_tips failed: %s", message)
            raise_service_unavailable()

        return SecurityTipsResponse(
            daily_tips=result.get("daily_tips", []),
            weekly_focus=result.get("weekly_focus", ""),
            monthly_goal=result.get("monthly_goal", ""),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Ошибка при получении советов: %s", e)
        raise_service_unavailable()
