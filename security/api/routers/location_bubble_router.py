# -*- coding: utf-8 -*-
"""
Location Bubble API Router
-------------------------
FastAPI endpoints для интеграции Location Bubble Agent с мобильным приложением iOS.

Использование:
    В main.py добавить:
    from security.api.routers.location_bubble_router import router as location_bubble_router
    app.include_router(location_bubble_router)

Дата создания: 12 декабря 2025
Версия: 1.0.0
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field, validator
import logging
import os
import re

# Импорты агента
try:
    from security.ai_agents.location_bubble_agent import (
        LocationBubbleAgent,
        BubbleRadius,
        TimeBasedSettings,
        PersonBubbleSettings
    )
except ImportError:
    LocationBubbleAgent = None
    BubbleRadius = None
    TimeBasedSettings = None
    PersonBubbleSettings = None

logger = logging.getLogger(__name__)

# Создаем FastAPI Router
router = APIRouter(prefix="/api/location/bubble", tags=["Location Bubble"])

# Глобальный экземпляр агента (инициализируется при первом запросе)
_agent_instance: Optional[LocationBubbleAgent] = None


def get_agent() -> LocationBubbleAgent:
    """
    Получение экземпляра агента (singleton)

    Returns:
        Экземпляр LocationBubbleAgent

    Raises:
        HTTPException: Если агент не может быть инициализирован
    """
    global _agent_instance
    if _agent_instance is None:
        if LocationBubbleAgent is None:
            raise HTTPException(
                status_code=503,
                detail="Location Bubble Agent не доступен. Проверьте установку модуля."
            )

        config = {
            "default_radius": int(os.getenv("LOCATION_BUBBLE_DEFAULT_RADIUS", "500")),
            "enable_time_based": os.getenv("LOCATION_BUBBLE_ENABLE_TIME_BASED", "true").lower() == "true"
        }

        try:
            _agent_instance = LocationBubbleAgent(config)
            logger.info("✅ Location Bubble Agent инициализирован")
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


class TimeBasedSettingsModel(BaseModel):
    """Модель настроек по времени"""
    start_time: str = Field(..., description="Время начала (формат HH:MM)", example="09:00")
    end_time: str = Field(..., description="Время окончания (формат HH:MM)", example="18:00")
    radius: int = Field(..., description="Радиус в метрах (100, 500, 1000)", example=500)
    enabled: bool = Field(True, description="Включено ли ограничение")

    @validator('start_time', 'end_time')
    def validate_time_format(cls, v):
        """Валидация формата времени"""
        if not re.match(r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', v):
            raise ValueError('Время должно быть в формате HH:MM (например, 09:00)')
        return v

    @validator('radius')
    def validate_radius(cls, v):
        """Валидация радиуса"""
        if v not in [100, 500, 1000] and v < 50:
            raise ValueError('Радиус должен быть 100, 500, 1000 метров или >= 50 для пользовательского')
        return v


class GetBubbleLocationRequest(BaseModel):
    """Запрос на генерацию приблизительного местоположения"""
    user_id: str = Field(..., description="ID пользователя (родителя)")
    person_id: str = Field(..., description="ID человека, для которого генерируется пузырь")
    exact_latitude: float = Field(..., description="Точная широта", ge=-90, le=90)
    exact_longitude: float = Field(..., description="Точная долгота", ge=-180, le=180)
    radius: Optional[int] = Field(None, description="Радиус в метрах (опционально, если не указан - используется настройка)", ge=50)
    accuracy: Optional[float] = Field(None, description="Точность исходных координат в метрах (опционально)", ge=0)


class SetPersonSettingsRequest(BaseModel):
    """Запрос на установку настроек пузыря для человека"""
    user_id: str = Field(..., description="ID пользователя")
    person_id: str = Field(..., description="ID человека")
    default_radius: int = Field(..., description="Радиус по умолчанию (100, 500, 1000)", example=500)
    time_based_settings: Optional[List[TimeBasedSettingsModel]] = Field(None, description="Настройки по времени (опционально)")
    enabled: bool = Field(True, description="Включен ли пузырь")

    @validator('default_radius')
    def validate_default_radius(cls, v):
        """Валидация радиуса по умолчанию"""
        if v not in [100, 500, 1000] and v < 50:
            raise ValueError('Радиус по умолчанию должен быть 100, 500, 1000 метров или >= 50 для пользовательского')
        return v


# ═══════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════


@router.post("", summary="Генерировать приблизительное местоположение (пузырь)")
async def get_bubble_location(
    request: GetBubbleLocationRequest,
    agent: LocationBubbleAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Генерировать приблизительное местоположение (пузырь) для человека

    Args:
        request: Запрос с точными координатами и опциональным радиусом

    Returns:
        Приблизительное местоположение (без точных координат):
        {
            "approximate_latitude": float,
            "approximate_longitude": float,
            "radius": int,
            "accuracy": float,
            "generated_at": float
        }
    """
    try:
        result = agent.get_bubble_location(
            user_id=request.user_id,
            person_id=request.person_id,
            exact_latitude=request.exact_latitude,
            exact_longitude=request.exact_longitude,
            radius=request.radius,
            accuracy=request.accuracy
        )

        return {
            "status": "success",
            "bubble_location": result
        }
    except Exception as e:
        logger.error(f"Ошибка при генерации пузыря: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/settings", summary="Установить настройки пузыря для человека")
async def set_person_settings(
    request: SetPersonSettingsRequest,
    agent: LocationBubbleAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Установить настройки пузыря для конкретного человека

    Args:
        request: Запрос с настройками (радиус, настройки по времени)

    Returns:
        Результат установки настроек
    """
    try:
        # Конвертируем радиус в BubbleRadius
        if request.default_radius == 100:
            default_radius = BubbleRadius.SMALL
        elif request.default_radius == 500:
            default_radius = BubbleRadius.MEDIUM
        elif request.default_radius == 1000:
            default_radius = BubbleRadius.LARGE
        else:
            # Пользовательский радиус
            default_radius = BubbleRadius.CUSTOM
            # Для пользовательского радиуса нужно будет обработать отдельно
            # Пока используем MEDIUM как fallback
            default_radius = BubbleRadius.MEDIUM

        # Конвертируем настройки по времени
        time_based_settings = None
        if request.time_based_settings:
            time_based_settings = []
            for tbs in request.time_based_settings:
                # Определяем BubbleRadius для времени
                if tbs.radius == 100:
                    radius = BubbleRadius.SMALL
                elif tbs.radius == 500:
                    radius = BubbleRadius.MEDIUM
                elif tbs.radius == 1000:
                    radius = BubbleRadius.LARGE
                else:
                    radius = BubbleRadius.MEDIUM  # Fallback

                time_based_settings.append(TimeBasedSettings(
                    start_time=tbs.start_time,
                    end_time=tbs.end_time,
                    radius=radius,
                    enabled=tbs.enabled
                ))

        result = agent.set_person_settings(
            user_id=request.user_id,
            person_id=request.person_id,
            default_radius=default_radius,
            time_based_settings=time_based_settings,
            enabled=request.enabled
        )

        return {
            "status": "success",
            "settings": result
        }
    except Exception as e:
        logger.error(f"Ошибка при установке настроек: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings", summary="Получить настройки пузыря для человека")
async def get_person_settings(
    user_id: str = Query(..., description="ID пользователя"),
    person_id: str = Query(..., description="ID человека"),
    agent: LocationBubbleAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Получить настройки пузыря для конкретного человека

    Args:
        user_id: ID пользователя
        person_id: ID человека

    Returns:
        Настройки пузыря
    """
    try:
        settings = agent.get_person_settings(user_id=user_id, person_id=person_id)
        return {
            "status": "success",
            "settings": settings.to_dict()
        }
    except Exception as e:
        logger.error(f"Ошибка при получении настроек: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings/all", summary="Получить все настройки пузырей для пользователя")
async def get_all_person_settings(
    user_id: str = Query(..., description="ID пользователя"),
    agent: LocationBubbleAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Получить все настройки пузырей для пользователя

    Args:
        user_id: ID пользователя

    Returns:
        Словарь {person_id: settings}
    """
    try:
        settings = agent.get_all_person_settings(user_id=user_id)
        return {
            "status": "success",
            "user_id": user_id,
            "settings": settings,
            "total": len(settings)
        }
    except Exception as e:
        logger.error(f"Ошибка при получении всех настроек: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", summary="Получить историю генераций пузырей")
async def get_generation_history(
    user_id: str = Query(..., description="ID пользователя"),
    limit: int = Query(50, description="Максимальное количество записей", ge=1, le=100),
    agent: LocationBubbleAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Получить историю генераций пузырей

    Args:
        user_id: ID пользователя
        limit: Максимальное количество записей (1-100)

    Returns:
        История генераций
    """
    try:
        history = agent.get_generation_history(user_id=user_id, limit=limit)
        return {
            "status": "success",
            "user_id": user_id,
            "history": history,
            "total": len(history)
        }
    except Exception as e:
        logger.error(f"Ошибка при получении истории: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", summary="Health check")
async def health_check(agent: LocationBubbleAgent = Depends(get_agent)) -> Dict[str, Any]:
    """
    Health check endpoint

    Returns:
        Статус работы агента
    """
    try:
        return {
            "status": "healthy",
            "agent": "location_bubble_agent",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Ошибка при health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))
