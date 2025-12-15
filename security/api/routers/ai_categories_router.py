# -*- coding: utf-8 -*-
"""
AI Categories API Router
-------------------------
FastAPI endpoints для интеграции AI Categories Agent с мобильным приложением iOS.

Использование:
    В main.py добавить:
    from security.api.routers.ai_categories_router import router as ai_categories_router
    app.include_router(ai_categories_router)

Дата создания: 11 декабря 2025
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
    from security.ai_agents.ai_categories_agent import (
        AICategoriesAgent,
        AISite,
        TimeRestriction,
        AgeRestriction,
        AISiteStatus,
        AccessAttempt
    )
except ImportError:
    AICategoriesAgent = None
    AISite = None
    TimeRestriction = None
    AgeRestriction = None
    AISiteStatus = None
    AccessAttempt = None

logger = logging.getLogger(__name__)

# Создаем FastAPI Router
router = APIRouter(prefix="/api/ai-categories", tags=["AI Categories"])

# Глобальный экземпляр агента (инициализируется при первом запросе)
_agent_instance: Optional[AICategoriesAgent] = None


def get_agent() -> AICategoriesAgent:
    """
    Получение экземпляра агента (singleton)

    Returns:
        Экземпляр AICategoriesAgent

    Raises:
        HTTPException: Если агент не может быть инициализирован
    """
    global _agent_instance
    if _agent_instance is None:
        if AICategoriesAgent is None:
            raise HTTPException(
                status_code=503,
                detail="AI Categories Agent не доступен. Проверьте установку модуля."
            )

        config = {
            "notify_parents": os.getenv("AI_CATEGORIES_NOTIFY_PARENTS", "true").lower() == "true",
            "default_block_all": os.getenv("AI_CATEGORIES_DEFAULT_BLOCK_ALL", "false").lower() == "true"
        }

        try:
            _agent_instance = AICategoriesAgent(config)
            logger.info("✅ AI Categories Agent инициализирован")
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


class TimeRestrictionModel(BaseModel):
    """Модель ограничения по времени"""
    start_time: str = Field(..., description="Время начала (формат HH:MM)", example="09:00")
    end_time: str = Field(..., description="Время окончания (формат HH:MM)", example="18:00")
    days_of_week: List[int] = Field(..., description="Дни недели [0-6] где 0=понедельник", example=[0, 1, 2, 3, 4])
    enabled: bool = Field(True, description="Включено ли ограничение")

    @validator('start_time', 'end_time')
    def validate_time_format(cls, v):
        """Валидация формата времени"""
        if not re.match(r'^([0-1][0-9]|2[0-3]):[0-5][0-9]$', v):
            raise ValueError('Время должно быть в формате HH:MM (например, 09:00)')
        return v

    @validator('days_of_week')
    def validate_days_of_week(cls, v):
        """Валидация дней недели"""
        if not all(0 <= day <= 6 for day in v):
            raise ValueError('Дни недели должны быть в диапазоне 0-6 (0=понедельник, 6=воскресенье)')
        return v


class AgeRestrictionModel(BaseModel):
    """Модель ограничения по возрасту"""
    min_age: int = Field(..., description="Минимальный возраст в годах", ge=0, le=18, example=13)
    require_parental_approval: bool = Field(True, description="Требуется ли одобрение родителей")
    block_completely: bool = Field(False, description="Полная блокировка для этого возраста")


class BlockSitesRequest(BaseModel):
    """Запрос на блокировку AI-сайтов"""
    user_id: str = Field(..., description="ID пользователя")
    site_ids: List[str] = Field(..., description="Список ID сайтов для блокировки", example=["chatgpt", "midjourney"])
    time_restriction: Optional[TimeRestrictionModel] = Field(None, description="Ограничение по времени (опционально)")

    @validator('site_ids')
    def validate_site_ids(cls, v):
        """Валидация списка сайтов"""
        if not v:
            raise ValueError('Список сайтов не может быть пустым')
        return v


class AllowSitesRequest(BaseModel):
    """Запрос на разрешение доступа к AI-сайтам"""
    user_id: str = Field(..., description="ID пользователя")
    site_ids: List[str] = Field(..., description="Список ID сайтов для разрешения", example=["chatgpt"])

    @validator('site_ids')
    def validate_site_ids(cls, v):
        """Валидация списка сайтов"""
        if not v:
            raise ValueError('Список сайтов не может быть пустым')
        return v


class CheckAccessRequest(BaseModel):
    """Запрос на проверку доступа к AI-сайту"""
    user_id: str = Field(..., description="ID пользователя")
    site_id: str = Field(..., description="ID сайта")
    user_age: Optional[int] = Field(None, description="Возраст пользователя (опционально)", ge=0, le=100)


class SetAgeRestrictionRequest(BaseModel):
    """Запрос на установку ограничения по возрасту"""
    user_id: str = Field(..., description="ID пользователя")
    site_id: str = Field(..., description="ID сайта")
    age_restriction: AgeRestrictionModel = Field(..., description="Ограничение по возрасту")


# ═══════════════════════════════════════════════════════════════
# API Endpoints
# ═══════════════════════════════════════════════════════════════


@router.get("/sites", summary="Получить список всех AI-сайтов")
async def get_sites(agent: AICategoriesAgent = Depends(get_agent)) -> Dict[str, Any]:
    """
    Получить список всех доступных AI-сайтов

    Returns:
        Список AI-сайтов с информацией о категориях и ограничениях
    """
    try:
        sites = agent.get_ai_sites()
        return {
            "status": "success",
            "sites": sites,
            "total": len(sites)
        }
    except Exception as e:
        logger.error(f"Ошибка при получении списка сайтов: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/block", summary="Заблокировать AI-сайты")
async def block_sites(
    request: BlockSitesRequest,
    agent: AICategoriesAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Заблокировать AI-сайты для пользователя

    Args:
        request: Запрос с ID пользователя, списком сайтов и опциональным ограничением по времени

    Returns:
        Результат блокировки
    """
    try:
        # Конвертируем TimeRestrictionModel в TimeRestriction
        time_restriction = None
        if request.time_restriction:
            time_restriction = TimeRestriction(
                start_time=request.time_restriction.start_time,
                end_time=request.time_restriction.end_time,
                days_of_week=request.time_restriction.days_of_week,
                enabled=request.time_restriction.enabled
            )

        result = agent.block_sites(
            user_id=request.user_id,
            site_ids=request.site_ids,
            time_restriction=time_restriction
        )

        return result
    except Exception as e:
        logger.error(f"Ошибка при блокировке сайтов: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/allow", summary="Разрешить доступ к AI-сайтам")
async def allow_sites(
    request: AllowSitesRequest,
    agent: AICategoriesAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Разрешить доступ к AI-сайтам для пользователя

    Args:
        request: Запрос с ID пользователя и списком сайтов

    Returns:
        Результат разрешения
    """
    try:
        result = agent.allow_sites(
            user_id=request.user_id,
            site_ids=request.site_ids
        )

        return result
    except Exception as e:
        logger.error(f"Ошибка при разрешении доступа к сайтам: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check", summary="Проверить доступ к AI-сайту")
async def check_access(
    request: CheckAccessRequest,
    agent: AICategoriesAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Проверить доступ пользователя к AI-сайту

    Args:
        request: Запрос с ID пользователя, ID сайта и опциональным возрастом

    Returns:
        Результат проверки доступа (allowed, blocked, reason)
    """
    try:
        result = agent.check_access(
            user_id=request.user_id,
            site_id=request.site_id,
            user_age=request.user_age
        )

        return result
    except Exception as e:
        logger.error(f"Ошибка при проверке доступа: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", summary="Получить статус всех AI-сайтов для пользователя")
async def get_status(
    user_id: str = Query(..., description="ID пользователя"),
    agent: AICategoriesAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Получить статус всех AI-сайтов для пользователя

    Args:
        user_id: ID пользователя

    Returns:
        Статус всех сайтов с информацией о блокировках и разрешениях
    """
    try:
        result = agent.get_status(user_id=user_id)
        return result
    except Exception as e:
        logger.error(f"Ошибка при получении статуса: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", summary="Получить историю попыток доступа")
async def get_access_history(
    user_id: str = Query(..., description="ID пользователя"),
    limit: int = Query(50, description="Максимальное количество записей", ge=1, le=100),
    agent: AICategoriesAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Получить историю попыток доступа к AI-сайтам

    Args:
        user_id: ID пользователя
        limit: Максимальное количество записей (1-100)

    Returns:
        История попыток доступа
    """
    try:
        history = agent.get_access_history(user_id=user_id, limit=limit)
        return {
            "status": "success",
            "user_id": user_id,
            "history": history,
            "total": len(history)
        }
    except Exception as e:
        logger.error(f"Ошибка при получении истории: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/age-restriction", summary="Установить ограничение по возрасту")
async def set_age_restriction(
    request: SetAgeRestrictionRequest,
    agent: AICategoriesAgent = Depends(get_agent)
) -> Dict[str, Any]:
    """
    Установить ограничение по возрасту для AI-сайта

    Args:
        request: Запрос с ID пользователя, ID сайта и ограничением по возрасту

    Returns:
        Результат установки ограничения
    """
    try:
        age_restriction = AgeRestriction(
            min_age=request.age_restriction.min_age,
            require_parental_approval=request.age_restriction.require_parental_approval,
            block_completely=request.age_restriction.block_completely
        )

        result = agent.set_age_restriction(
            user_id=request.user_id,
            site_id=request.site_id,
            age_restriction=age_restriction
        )

        return result
    except Exception as e:
        logger.error(f"Ошибка при установке ограничения по возрасту: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", summary="Health check")
async def health_check(agent: AICategoriesAgent = Depends(get_agent)) -> Dict[str, Any]:
    """
    Health check endpoint

    Returns:
        Статус работы агента
    """
    try:
        sites_count = len(agent.ai_sites)
        return {
            "status": "healthy",
            "agent": "ai_categories_agent",
            "version": "1.0.0",
            "sites_count": sites_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Ошибка при health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))
