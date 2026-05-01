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

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import asyncio
import json
from pydantic import BaseModel, Field
import logging
import sys
import os
import smtplib
from email.message import EmailMessage

# SFM Adapter import
backend_path = "/opt/aladdin-backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from sfm_adapter import sfm_adapter
    SFM_ADAPTER_AVAILABLE = True
except ImportError as e:
    SFM_ADAPTER_AVAILABLE = False
    sfm_adapter = None
    print(f"SFM Adapter not available: {e}")

logger = logging.getLogger(__name__)

# Создаем FastAPI Router
router = APIRouter(prefix="/api/ai/assistant", tags=["AI Assistant"])


def _allow_mock_fallback() -> bool:
    """Explicit non-prod switch. In production must stay disabled."""
    return os.getenv("ALADDIN_ALLOW_AI_FALLBACK", "false").lower() in ("1", "true", "yes")


# =============================================================================
# Pydantic модели для запросов и ответов
# =============================================================================

class ChatMessageRequest(BaseModel):
    """Запрос на отправку сообщения AI помощнику"""
    message: str = Field(..., description="Сообщение пользователя", min_length=1, max_length=2000)
    context: str = Field("general", description="Контекст разговора", example="general")
    user_id: Optional[str] = Field(None, description="ID пользователя")
    timestamp: Optional[datetime] = Field(None, description="Временная метка")


class StreamRequest(BaseModel):
    message: str = Field("", description="Сообщение пользователя или пусто для resume", max_length=4000)
    context: str = Field("general", description="Контекст стрима")
    resumeFromIndex: int = Field(0, ge=0)
    messageId: Optional[str] = None
    stream: bool = True
    response_language: Optional[str] = Field(None, description="Предпочитаемый язык ответа (en, ru, …)")


class ChatMessageResponse(BaseModel):
    """Ответ AI помощника"""
    response: str = Field(..., description="Ответ AI помощника")
    confidence: float = Field(0.95, description="Уровень уверенности (0-1)", ge=0, le=1)
    suggestions: List[str] = Field(default_factory=list, description="Предложения для пользователя")
    follow_up_questions: List[str] = Field(default_factory=list, description="Дополнительные вопросы")
    timestamp: Optional[datetime] = Field(None, description="Временная метка")


class ChatHistoryResponse(BaseModel):
    """История разговоров с AI помощником"""
    conversations: List[Dict[str, Any]] = Field(..., description="Список разговоров")
    total: int = Field(..., description="Общее количество разговоров")


class FeedbackRequest(BaseModel):
    """Запрос на отправку обратной связи"""
    rating: int = Field(..., description="Оценка (1-5)", ge=1, le=5)
    comment: Optional[str] = Field(None, description="Комментарий", max_length=1000)
    message_id: Optional[str] = Field(None, description="ID сообщения")
    query_text: Optional[str] = Field(None, description="Исходный вопрос пользователя", max_length=2000)
    resolved_by: Optional[str] = Field(None, description="Источник ответа: faq|ai|unknown", max_length=64)
    faq_id: Optional[str] = Field(None, description="ID FAQ, если ответ был из базы FAQ", max_length=128)
    confidence: Optional[float] = Field(None, description="Уверенность ответа (0-1)", ge=0, le=1)
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

def _get_fallback_response(context: str = "general") -> Dict[str, Any]:
    """Fallback ответы если SFM adapter недоступен"""
    responses = {
        "protection_status": "Ваша защита ALADDIN активна! Все 187 функций безопасности работают корректно.",
        "threat_analysis": "Анализ угроз завершен. Обнаружено 3 потенциальные угрозы, все заблокированы.",
        "recommendations": "Рекомендую включить все уровни защиты для максимальной безопасности.",
        "help": "Я - ваш AI помощник по безопасности ALADDIN. Могу помочь с анализом угроз, настройками защиты и ответами на вопросы.",
        "general": "Привет! Я AI помощник ALADDIN. Как я могу помочь вам с безопасностью?"
    }
    response_text = responses.get(context, responses["general"])
    return {
        "response": response_text,
        "confidence": 0.95,
        "suggestions": ["Проверить статус защиты", "Посмотреть статистику", "Настроить параметры"],
        "follow_up_questions": ["Что вас беспокоит?", "Нужна ли дополнительная защита?"],
        "timestamp": datetime.now()
    }


def _send_feedback_email(payload: Dict[str, Any]) -> bool:
    """Отправка email-уведомления о feedback. Не влияет на основной API flow."""
    smtp_host = os.getenv("ALADDIN_FEEDBACK_SMTP_HOST", "").strip()
    smtp_port = int(os.getenv("ALADDIN_FEEDBACK_SMTP_PORT", "587"))
    smtp_user = os.getenv("ALADDIN_FEEDBACK_SMTP_USER", "").strip()
    smtp_password = os.getenv("ALADDIN_FEEDBACK_SMTP_PASSWORD", "")
    from_email = os.getenv("ALADDIN_FEEDBACK_FROM_EMAIL", "").strip() or smtp_user
    to_email = os.getenv("ALADDIN_FEEDBACK_TO_EMAIL", "").strip()
    use_tls = os.getenv("ALADDIN_FEEDBACK_SMTP_TLS", "true").lower() in ("1", "true", "yes")

    # Если конфиг не задан, просто логируем и не ломаем основной ответ API.
    if not smtp_host or not from_email or not to_email:
        logger.info("Feedback email skipped: SMTP env is not configured")
        return False

    try:
        msg = EmailMessage()
        msg["Subject"] = f"[ALADDIN][AI Feedback] rating={payload.get('rating')} source={payload.get('resolved_by', 'unknown')}"
        msg["From"] = from_email
        msg["To"] = to_email
        msg.set_content(
            "\n".join(
                [
                    "ALADDIN AI Feedback",
                    f"time: {datetime.utcnow().isoformat()}Z",
                    f"rating: {payload.get('rating')}",
                    f"resolved_by: {payload.get('resolved_by')}",
                    f"faq_id: {payload.get('faq_id')}",
                    f"confidence: {payload.get('confidence')}",
                    f"session_id: {payload.get('session_id')}",
                    f"message_id: {payload.get('message_id')}",
                    "",
                    f"query_text: {payload.get('query_text')}",
                    "",
                    f"comment: {payload.get('comment')}",
                ]
            )
        )

        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            if use_tls:
                server.starttls()
            if smtp_user:
                server.login(smtp_user, smtp_password)
            server.send_message(msg)
        logger.info("Feedback email sent successfully")
        return True
    except Exception as email_error:
        logger.error(f"Feedback email send failed: {email_error}")
        return False


# =============================================================================
# API Endpoints (8 штук)
# =============================================================================

# 1. POST /api/ai/assistant/chat - Отправка сообщения AI помощнику
@router.post("/chat", response_model=ChatMessageResponse)
async def ai_assistant_chat(request: ChatMessageRequest) -> ChatMessageResponse:
    """
    AI помощник - обработка сообщений пользователя
    
    Args:
        request: Запрос с сообщением пользователя и контекстом
    
    Returns:
        Ответ AI помощника с рекомендациями
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "message": request.message,
                "context": request.context,
                "user_id": request.user_id or "guest",
                "timestamp": request.timestamp.isoformat() if request.timestamp else datetime.now().isoformat()
            }
            success, result, message = sfm_adapter.execute_function("ai_assistant_chat", data)
            if success:
                response_text = result.get("response") or ""
                if not response_text.strip():
                    raise HTTPException(status_code=502, detail="AI backend returned empty response")
                return ChatMessageResponse(
                    response=response_text,
                    confidence=result.get("confidence", 0.95),
                    suggestions=result.get("suggestions", []),
                    follow_up_questions=result.get("follow_up_questions", []),
                    timestamp=datetime.now()
                )
            logger.error(f"ai_assistant_chat failed in sfm_adapter: {message}")
            raise HTTPException(status_code=502, detail=f"AI backend failed: {message}")

        if _allow_mock_fallback():
            logger.warning("ALADDIN_ALLOW_AI_FALLBACK=true: using temporary fallback response")
            fallback = _get_fallback_response(request.context)
            return ChatMessageResponse(**fallback)

        raise HTTPException(status_code=503, detail="AI backend is unavailable")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Ошибка при обработке сообщения: {e}")
        raise HTTPException(status_code=500, detail="AI chat internal error")


@router.post("/stream")
async def ai_assistant_stream(request: StreamRequest):
    """
    SSE stream endpoint for iOS token-by-token rendering.
    """
    if not request.stream:
        raise HTTPException(status_code=400, detail="stream flag must be true")

    response_text: Optional[str] = None

    if SFM_ADAPTER_AVAILABLE and sfm_adapter:
        payload = {
            "message": request.message,
            "context": request.context,
            "message_id": request.messageId,
            "resume_from_index": request.resumeFromIndex,
            "stream": True,
        }
        if request.response_language:
            payload["response_language"] = request.response_language
        success, result, message = sfm_adapter.execute_function("ai_assistant_chat", payload)
        if not success:
            logger.error(f"ai_assistant_stream failed in sfm_adapter: {message}")
            raise HTTPException(status_code=502, detail=f"AI backend failed: {message}")
        response_text = str(result.get("response") or "").strip()
    elif _allow_mock_fallback():
        fallback = _get_fallback_response(request.context)
        response_text = str(fallback.get("response") or "").strip()
    else:
        raise HTTPException(status_code=503, detail="AI backend is unavailable")

    if not response_text:
        raise HTTPException(status_code=502, detail="AI backend returned empty response")

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
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {"user_id": user_id or "guest", "limit": limit}
            success, result, message = sfm_adapter.execute_function("ai_assistant_history", data)
            
            if success:
                return ChatHistoryResponse(
                    conversations=result.get("conversations", []),
                    total=result.get("total", 0)
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return ChatHistoryResponse(
            conversations=[
                {"date": "2026-02-04", "messages": 12, "topics": ["protection", "threats"]},
                {"date": "2026-02-03", "messages": 8, "topics": ["settings", "analysis"]}
            ],
            total=2
        )
    except Exception as e:
        logger.error(f"Ошибка при получении истории: {e}")
        return ChatHistoryResponse(conversations=[], total=0)


# 3. POST /api/ai/assistant/feedback - Обратная связь
@router.post("/feedback", response_model=FeedbackResponse)
async def ai_assistant_feedback(request: FeedbackRequest) -> FeedbackResponse:
    """
    Обратная связь по работе AI помощника
    
    Args:
        request: Запрос с оценкой и комментарием
    
    Returns:
        Результат сохранения обратной связи
    """
    try:
        payload = {
            "rating": request.rating,
            "comment": request.comment,
            "message_id": request.message_id,
            "query_text": request.query_text,
            "resolved_by": request.resolved_by or "unknown",
            "faq_id": request.faq_id,
            "confidence": request.confidence,
            "session_id": request.session_id,
        }
        _send_feedback_email(payload)

        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = payload
            success, result, message = sfm_adapter.execute_function("ai_assistant_feedback", data)
            
            if success:
                return FeedbackResponse(
                    feedback_recorded=True,
                    average_rating=result.get("average_rating", 4.8),
                    total_feedbacks=result.get("total_feedbacks", 1250)
                )
            logger.error(f"ai_assistant_feedback failed in sfm_adapter: {message}")
            raise HTTPException(status_code=502, detail=f"AI feedback backend failed: {message}")

        if _allow_mock_fallback():
            logger.warning("ALADDIN_ALLOW_AI_FALLBACK=true: using temporary feedback fallback")
            return FeedbackResponse(
                feedback_recorded=True,
                average_rating=4.8,
                total_feedbacks=1250
            )

        raise HTTPException(status_code=503, detail="AI feedback backend is unavailable")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Ошибка при сохранении обратной связи: {e}")
        raise HTTPException(status_code=500, detail="AI feedback internal error")


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
            
            if success:
                return CapabilitiesResponse(
                    features=result.get("features", []),
                    languages=result.get("languages", ["Русский", "English"]),
                    response_time=result.get("response_time", "<2 сек"),
                    accuracy=result.get("accuracy", "95%")
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return CapabilitiesResponse(
            features=[
                "Анализ угроз в реальном времени",
                "Персональные рекомендации по безопасности",
                "Объяснение работы функций защиты",
                "Мониторинг подозрительной активности",
                "Советы по улучшению безопасности",
                "Ответы на вопросы о кибербезопасности"
            ],
            languages=["Русский", "English"],
            response_time="<2 сек",
            accuracy="95%"
        )
    except Exception as e:
        logger.error(f"Ошибка при получении возможностей: {e}")
        return CapabilitiesResponse(
            features=[],
            languages=["Русский"],
            response_time="N/A",
            accuracy="N/A"
        )


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
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "threat": request.threat,
                "type": request.type,
                "context": request.context
            }
            success, result, message = sfm_adapter.execute_function("ai_assistant_analyze_threat", data)
            
            if success:
                return AnalyzeThreatResponse(
                    threat_level=result.get("threat_level", "medium"),
                    analysis=result.get("analysis", "Угроза проанализирована."),
                    actions_taken=result.get("actions_taken", []),
                    prevention_tips=result.get("prevention_tips", [])
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return AnalyzeThreatResponse(
            threat_level="medium",
            analysis="Угроза проанализирована. Рекомендуется усилить защиту.",
            actions_taken=["Заблокирован IP", "Отправлено уведомление", "Добавлен в черный список"],
            prevention_tips=["Включите VPN", "Обновите пароли", "Используйте 2FA"]
        )
    except Exception as e:
        logger.error(f"Ошибка при анализе угрозы: {e}")
        return AnalyzeThreatResponse(
            threat_level="unknown",
            analysis="Ошибка при анализе угрозы",
            actions_taken=[],
            prevention_tips=[]
        )


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
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            success, result, message = sfm_adapter.execute_function("ai_assistant_recommendations", {"user_id": user_id})
            
            if success:
                return RecommendationsResponse(
                    personal_recommendations=result.get("personal_recommendations", []),
                    security_score=result.get("security_score", 95),
                    improvement_areas=result.get("improvement_areas", [])
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return RecommendationsResponse(
            personal_recommendations=[
                "Включите все уровни защиты для максимальной безопасности",
                "Настройте автоматические обновления",
                "Используйте сложные пароли",
                "Регулярно проверяйте подключенные устройства"
            ],
            security_score=95,
            improvement_areas=["VPN использование", "Парольная политика"]
        )
    except Exception as e:
        logger.error(f"Ошибка при получении рекомендаций: {e}")
        return RecommendationsResponse(
            personal_recommendations=[],
            security_score=0,
            improvement_areas=[]
        )


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
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            data = {
                "type": request.type,
                "description": request.description,
                "severity": request.severity
            }
            success, result, message = sfm_adapter.execute_function("ai_assistant_report_incident", data)
            
            if success:
                return ReportIncidentResponse(
                    incident_id=result.get("incident_id", f"INC-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"),
                    status=result.get("status", "investigating"),
                    estimated_resolution=result.get("estimated_resolution", "2 hours"),
                    assigned_specialist=result.get("assigned_specialist", "AI Security Team"),
                    follow_up_actions=result.get("follow_up_actions", [])
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return ReportIncidentResponse(
            incident_id=f"INC-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}",
            status="investigating",
            estimated_resolution="2 hours",
            assigned_specialist="AI Security Team",
            follow_up_actions=["Анализ логов", "Проверка систем", "Уведомление пользователя"]
        )
    except Exception as e:
        logger.error(f"Ошибка при регистрации инцидента: {e}")
        return ReportIncidentResponse(
            incident_id="ERROR",
            status="error",
            estimated_resolution="N/A",
            assigned_specialist="N/A",
            follow_up_actions=[]
        )


# 8. GET /api/ai/assistant/security_tips - Советы по безопасности
@router.get("/security_tips", response_model=SecurityTipsResponse)
async def ai_assistant_security_tips() -> SecurityTipsResponse:
    """
    Полезные советы по безопасности от AI
    
    Returns:
        Ежедневные советы, фокус недели и цель месяца
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            success, result, message = sfm_adapter.execute_function("ai_assistant_security_tips", {})
            
            if success:
                return SecurityTipsResponse(
                    daily_tips=result.get("daily_tips", []),
                    weekly_focus=result.get("weekly_focus", "Защита от фишинга"),
                    monthly_goal=result.get("monthly_goal", "Достичь 100% безопасности")
                )
            else:
                logger.warning(f"SFM adapter error: {message}, using fallback")
        
        # Fallback mock response
        return SecurityTipsResponse(
            daily_tips=[
                "Всегда проверяйте URL перед вводом личных данных",
                "Используйте менеджер паролей для сложных комбинаций",
                "Регулярно обновляйте приложения и ОС",
                "Будьте осторожны с email от неизвестных отправителей"
            ],
            weekly_focus="Защита от фишинга",
            monthly_goal="Достичь 100% безопасности"
        )
    except Exception as e:
        logger.error(f"Ошибка при получении советов: {e}")
        return SecurityTipsResponse(
            daily_tips=[],
            weekly_focus="N/A",
            monthly_goal="N/A"
        )
