# -*- coding: utf-8 -*-
"""
Dark Web Monitoring API Router
-------------------------------
FastAPI endpoints для интеграции Dark Web Monitoring с мобильным приложением iOS.

Использование:
    В main.py добавить:
    from security.api.routers.dark_web_monitoring_router import router as dark_web_router
    app.include_router(dark_web_router)

Дата создания: 9 декабря 2025
Версия: 1.0.0
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Query, Header, Depends
from pydantic import BaseModel, Field, validator
import logging
import os
import re

# Импорты агента
try:
    from security.ai_agents.dark_web_monitoring_agent import DarkWebMonitoringAgent
except ImportError:
    DarkWebMonitoringAgent = None

logger = logging.getLogger(__name__)

# Создаем FastAPI Router
router = APIRouter(prefix="/api/darkweb", tags=["Dark Web Monitoring"])

# Глобальный экземпляр агента (инициализируется при первом запросе)
_agent_instance: Optional[DarkWebMonitoringAgent] = None


def get_agent() -> DarkWebMonitoringAgent:
    """
    Получение экземпляра агента (singleton)

    Returns:
        Экземпляр DarkWebMonitoringAgent

    Raises:
        HTTPException: Если агент не может быть инициализирован
    """
    global _agent_instance
    if _agent_instance is None:
        if DarkWebMonitoringAgent is None:
            raise HTTPException(
                status_code=503,
                detail="Dark Web Monitoring Agent не доступен. Проверьте установку модуля."
            )

        config = {
            "hibp_api_key": os.getenv("HIBP_API_KEY", ""),
            "breachdirectory_api_key": os.getenv("BREACHDIRECTORY_API_KEY", ""),
            "cache_ttl": int(os.getenv("DARK_WEB_CACHE_TTL", "86400")),
            "monitoring_interval": int(os.getenv("DARK_WEB_MONITORING_INTERVAL", "24"))
        }

        try:
            _agent_instance = DarkWebMonitoringAgent(config)
            logger.info("✅ Dark Web Monitoring Agent инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации агента: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка инициализации агента: {str(e)}"
            )

    return _agent_instance


# ═══════════════════════════════════════════════════════════════
# Pydantic модели для запросов и ответов
# ═══════════════════════════════════════════════════════════════


class CheckEmailRequest(BaseModel):
    """Запрос на проверку email"""
    email: str = Field(..., description="Email адрес для проверки")
    include_hibp: bool = Field(True, description="Включить проверку через Have I Been Pwned")
    include_breachdirectory: bool = Field(True, description="Включить проверку через BreachDirectory")
    include_russian: bool = Field(True, description="Включить проверку через российские базы")

    @validator('email')
    def validate_email(cls, v):
        """Валидация email адреса"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v


class BreachInfo(BaseModel):
    """Информация об утечке данных"""
    id: str = Field(..., description="Уникальный идентификатор утечки")
    email: str = Field(..., description="Email адрес")
    breach_name: str = Field(..., description="Название утечки")
    count: Optional[int] = Field(None, description="Количество затронутых записей")
    detected_at: str = Field(..., description="Дата обнаружения (ISO 8601)")
    severity: str = Field(..., description="Уровень серьезности (low/medium/high)")
    affected_data: Optional[List[str]] = Field(None, description="Типы затронутых данных")
    source: str = Field(..., description="Источник информации о утечке")


class CheckEmailResponse(BaseModel):
    """Ответ на проверку email"""
    success: bool = Field(..., description="Успешность операции")
    email: str = Field(..., description="Проверенный email")
    breaches_found: int = Field(..., description="Количество найденных утечек")
    breaches: List[BreachInfo] = Field(default_factory=list, description="Список утечек")
    checked_at: str = Field(..., description="Время проверки (ISO 8601)")
    sources: List[str] = Field(default_factory=list, description="Использованные источники")
    error: Optional[str] = Field(None, description="Описание ошибки, если есть")


class StartMonitoringRequest(BaseModel):
    """Запрос на запуск мониторинга"""
    user_id: str = Field(..., description="ID пользователя")
    email: Optional[str] = Field(None, description="Email для мониторинга")
    phone: Optional[str] = Field(None, description="Номер телефона для мониторинга")
    interval_hours: int = Field(24, ge=1, le=168, description="Интервал проверки в часах (1-168)")

    @validator('email')
    def validate_email(cls, v):
        """Валидация email адреса (если указан)"""
        if v is None:
            return v
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v


class StartMonitoringResponse(BaseModel):
    """Ответ на запуск мониторинга"""
    success: bool = Field(..., description="Успешность операции")
    user_id: str = Field(..., description="ID пользователя")
    next_check: str = Field(..., description="Время следующей проверки (ISO 8601)")
    interval_hours: int = Field(..., description="Интервал проверки в часах")
    error: Optional[str] = Field(None, description="Описание ошибки, если есть")


class StopMonitoringRequest(BaseModel):
    """Запрос на остановку мониторинга"""
    user_id: str = Field(..., description="ID пользователя")


class StopMonitoringResponse(BaseModel):
    """Ответ на остановку мониторинга"""
    success: bool = Field(..., description="Успешность операции")
    user_id: str = Field(..., description="ID пользователя")
    error: Optional[str] = Field(None, description="Описание ошибки, если есть")


class MonitoringStatusResponse(BaseModel):
    """Ответ со статусом мониторинга"""
    success: bool = Field(..., description="Успешность операции")
    is_monitoring: bool = Field(..., description="Активен ли мониторинг")
    user_id: Optional[str] = Field(None, description="ID пользователя")
    status: Optional[Dict[str, Any]] = Field(None, description="Детальный статус")
    total_active: Optional[int] = Field(None, description="Общее количество активных мониторингов")
    error: Optional[str] = Field(None, description="Описание ошибки, если есть")


class BreachesResponse(BaseModel):
    """Ответ со списком утечек"""
    success: bool = Field(..., description="Успешность операции")
    threats: List[Dict[str, Any]] = Field(default_factory=list, description="Собранные угрозы")
    analyzed_threats: List[Dict[str, Any]] = Field(default_factory=list, description="Проанализированные угрозы")
    total_threats: int = Field(0, description="Общее количество угроз")
    collected_at: str = Field(..., description="Время сбора (ISO 8601)")
    error: Optional[str] = Field(None, description="Описание ошибки, если есть")


class HealthResponse(BaseModel):
    """Ответ health check"""
    status: str = Field(..., description="Статус сервиса")
    agent_loaded: bool = Field(..., description="Загружен ли агент")
    cache_stats: Optional[Dict[str, Any]] = Field(None, description="Статистика кэша")
    timestamp: str = Field(..., description="Время проверки (ISO 8601)")


# ═══════════════════════════════════════════════════════════════
# Вспомогательные функции
# ═══════════════════════════════════════════════════════════════


def get_auth_token(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """
    Извлечение токена из заголовка Authorization

    TODO: Реализовать полноценную проверку JWT токена
    """
    if not authorization:
        return None

    # Формат: "Bearer <token>"
    if authorization.startswith("Bearer "):
        return authorization[7:]

    return authorization


def require_auth_dependency(authorization: Optional[str] = Header(None)) -> str:
    """
    Dependency для проверки авторизации

    Raises:
        HTTPException: Если токен отсутствует
    """
    token = get_auth_token(authorization)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Authorization required. Provide Bearer token in Authorization header."
        )
    # TODO: Проверка валидности токена
    return token


# ═══════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check(agent: DarkWebMonitoringAgent = Depends(get_agent)):
    """
    Health check endpoint (без авторизации)

    Проверяет доступность сервиса и статус агента.
    """
    try:
        cache_stats = agent.get_cache_stats() if hasattr(agent, 'get_cache_stats') else None

        return HealthResponse(
            status="healthy",
            agent_loaded=True,
            cache_stats=cache_stats,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Ошибка health check: {e}")
        return HealthResponse(
            status="unhealthy",
            agent_loaded=False,
            timestamp=datetime.now().isoformat()
        )


@router.post("/check", response_model=CheckEmailResponse, summary="Проверка email на утечки")
async def check_email_breach(
    request: CheckEmailRequest,
    token: str = Depends(require_auth_dependency),
    agent: DarkWebMonitoringAgent = Depends(get_agent)
):
    """
    Проверка email адреса на утечки данных через все доступные источники.

    Требует авторизации (Bearer token в заголовке Authorization).
    """
    try:
        result = agent.check_email_breach(
            email=request.email,
            include_hibp=request.include_hibp,
            include_breachdirectory=request.include_breachdirectory,
            include_russian=request.include_russian
        )

        # Конвертация BreachInfo в Pydantic модели
        breaches = [
            BreachInfo(**breach) if isinstance(breach, dict) else BreachInfo(
                id=breach.id,
                email=breach.email,
                breach_name=breach.breach_name,
                count=breach.count,
                detected_at=breach.detected_at,
                severity=breach.severity,
                affected_data=getattr(breach, 'affected_data', None),
                source=getattr(breach, 'source', 'unknown')
            )
            for breach in result.get("breaches", [])
        ]

        return CheckEmailResponse(
            success=True,
            email=request.email,
            breaches_found=result.get("breaches_found", 0),
            breaches=breaches,
            checked_at=result.get("checked_at", datetime.now().isoformat()),
            sources=result.get("sources", [])
        )
    except Exception as e:
        logger.error(f"Ошибка проверки email {request.email}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при проверке email: {str(e)}"
        )


@router.post("/start-monitoring", response_model=StartMonitoringResponse, summary="Запуск мониторинга")
async def start_monitoring(
    request: StartMonitoringRequest,
    token: str = Depends(require_auth_dependency),
    agent: DarkWebMonitoringAgent = Depends(get_agent)
):
    """
    Запуск автоматического мониторинга данных пользователя.

    Требует авторизации.
    """
    try:
        result = agent.start_monitoring(
            user_id=request.user_id,
            email=request.email,
            phone=request.phone,
            interval_hours=request.interval_hours
        )

        return StartMonitoringResponse(
            success=result.get("success", True),
            user_id=result.get("user_id", request.user_id),
            next_check=result.get("next_check", ""),
            interval_hours=result.get("interval_hours", request.interval_hours)
        )
    except Exception as e:
        logger.error(f"Ошибка запуска мониторинга для {request.user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при запуске мониторинга: {str(e)}"
        )


@router.post("/stop-monitoring", response_model=StopMonitoringResponse, summary="Остановка мониторинга")
async def stop_monitoring(
    request: StopMonitoringRequest,
    token: str = Depends(require_auth_dependency),
    agent: DarkWebMonitoringAgent = Depends(get_agent)
):
    """
    Остановка автоматического мониторинга.

    Требует авторизации.
    """
    try:
        result = agent.stop_monitoring(request.user_id)

        return StopMonitoringResponse(
            success=result.get("success", True),
            user_id=result.get("user_id", request.user_id)
        )
    except Exception as e:
        logger.error(f"Ошибка остановки мониторинга для {request.user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при остановке мониторинга: {str(e)}"
        )


@router.get("/status", response_model=MonitoringStatusResponse, summary="Статус мониторинга")
async def get_monitoring_status(
    user_id: Optional[str] = Query(None, description="ID пользователя (опционально, если None - статус всех)"),
    token: str = Depends(require_auth_dependency),
    agent: DarkWebMonitoringAgent = Depends(get_agent)
):
    """
    Получение статуса мониторинга для пользователя или всех активных мониторингов.

    Требует авторизации.
    """
    try:
        result = agent.get_monitoring_status(user_id)

        return MonitoringStatusResponse(
            success=True,
            is_monitoring=result.get("is_monitoring", False),
            user_id=result.get("user_id", user_id),
            status=result.get("status"),
            total_active=result.get("total_active")
        )
    except Exception as e:
        logger.error(f"Ошибка получения статуса для {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении статуса: {str(e)}"
        )


@router.get("/breaches", response_model=BreachesResponse, summary="Получение всех утечек")
async def get_breaches(
    token: str = Depends(require_auth_dependency),
    agent: DarkWebMonitoringAgent = Depends(get_agent)
):
    """
    Получение списка всех найденных утечек из активных мониторингов.

    Требует авторизации.
    """
    try:
        threats = agent.collect_threats()
        analyzed_threats = agent.analyze_threats(threats) if threats else []

        return BreachesResponse(
            success=True,
            threats=threats,
            analyzed_threats=analyzed_threats,
            total_threats=len(threats),
            collected_at=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Ошибка получения утечек: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении утечек: {str(e)}"
        )
