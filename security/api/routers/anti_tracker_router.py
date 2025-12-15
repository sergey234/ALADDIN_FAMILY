#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🛡️ Anti-Tracker Router
API endpoints для Anti-Tracker Agent

Дата создания: 12 декабря 2025
Версия: 1.0.0
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict

# Импорт агента
try:
    from security.ai_agents.anti_tracker_agent import (
        AntiTrackerAgent,
        TrackerType
    )
except ImportError:
    # Для локальной разработки
    AntiTrackerAgent = None
    TrackerType = None

router = APIRouter(prefix="/api/anti-tracker", tags=["anti-tracker"])

# Singleton агента
_agent_instance: Optional[AntiTrackerAgent] = None


def get_agent() -> AntiTrackerAgent:
    """Получить экземпляр агента (singleton)"""
    global _agent_instance
    if _agent_instance is None:
        # Конфигурация из переменных окружения
        import os
        config = {
            "strict_mode": os.getenv("ANTI_TRACKER_STRICT_MODE", "true").lower() == "true",
            "enable_analytics_blocking": os.getenv("ANTI_TRACKER_ANALYTICS", "true").lower() == "true",
            "enable_advertising_blocking": os.getenv("ANTI_TRACKER_ADVERTISING", "true").lower() == "true",
            "enable_social_blocking": os.getenv("ANTI_TRACKER_SOCIAL", "true").lower() == "true",
            "whitelist": os.getenv("ANTI_TRACKER_WHITELIST", "").split(",") if os.getenv("ANTI_TRACKER_WHITELIST") else [],
            "blacklist": os.getenv("ANTI_TRACKER_BLACKLIST", "").split(",") if os.getenv("ANTI_TRACKER_BLACKLIST") else []
        }
        _agent_instance = AntiTrackerAgent(config=config)
    return _agent_instance


# MARK: - Pydantic Models

class CheckRequestRequest(BaseModel):
    """Запрос на проверку URL"""
    url: str = Field(..., description="URL для проверки")
    headers: Optional[Dict[str, str]] = Field(None, description="HTTP заголовки (опционально)")
    user_id: Optional[str] = Field(None, description="ID пользователя (опционально)")


class BlockTrackerRequest(BaseModel):
    """Запрос на блокировку трекера"""
    domain: str = Field(..., description="Домен трекера")
    tracker_type: str = Field(..., description="Тип трекера (analytics, advertising, social, pattern)")
    reason: Optional[str] = Field(None, description="Причина блокировки")


class UnblockTrackerRequest(BaseModel):
    """Запрос на разблокировку трекера"""
    domain: str = Field(..., description="Домен трекера")


class SettingsRequest(BaseModel):
    """Запрос на обновление настроек"""
    strict_mode: Optional[bool] = Field(None, description="Строгий режим блокировки")
    enable_analytics_blocking: Optional[bool] = Field(None, description="Блокировать аналитику")
    enable_advertising_blocking: Optional[bool] = Field(None, description="Блокировать рекламу")
    enable_social_blocking: Optional[bool] = Field(None, description="Блокировать социальные трекеры")
    whitelist: Optional[list] = Field(None, description="Белый список доменов")
    blacklist: Optional[list] = Field(None, description="Черный список доменов")


# MARK: - API Endpoints

@router.post("/check", summary="Проверка URL на трекеры")
async def check_request(request: CheckRequestRequest):
    """
    Проверить URL на наличие трекеров

    Возвращает:
    - blocked: bool - заблокирован ли запрос
    - reason: str - причина блокировки (если заблокирован)
    - tracker_type: str - тип трекера (если заблокирован)
    """
    try:
        agent = get_agent()
        result = agent.check_request(request.url, request.headers)

        # Если запрос заблокирован, записываем в статистику
        if result.get("blocked", False):
            tracker_type_str = result.get("tracker_type", "unknown")
            try:
                tracker_type = TrackerType(tracker_type_str)
            except (ValueError, TypeError):
                tracker_type = TrackerType.UNKNOWN

            agent.record_blocked_request(
                url=request.url,
                tracker_type=tracker_type,
                user_id=request.user_id,
                reason=result.get("reason")
            )

        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", summary="Статистика блокировок")
async def get_statistics():
    """
    Получить статистику заблокированных запросов

    Возвращает:
    - total_blocked: общее количество заблокированных запросов
    - blocked_by_type: количество по типам трекеров
    - top_blocked_domains: топ заблокированных доменов
    - last_blocked: время последней блокировки
    - first_blocked: время первой блокировки
    """
    try:
        agent = get_agent()
        stats = agent.get_statistics()
        return {"status": "success", "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trackers", summary="Список известных трекеров")
async def get_tracker_lists():
    """
    Получить списки известных трекеров (для синхронизации с iOS)

    Возвращает:
    - analytics: список доменов аналитики
    - advertising: список доменов рекламы
    - social: список доменов социальных трекеров
    - patterns: список паттернов URL
    - all: объединенный список всех трекеров
    """
    try:
        agent = get_agent()
        trackers = agent.get_tracker_lists()
        return {"status": "success", "data": trackers}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/block", summary="Блокировка трекера")
async def block_tracker(request: BlockTrackerRequest):
    """
    Заблокировать трекер

    Args:
        domain: Домен трекера
        tracker_type: Тип трекера (analytics, advertising, social, pattern)
        reason: Причина блокировки (опционально)
    """
    try:
        agent = get_agent()

        # Преобразование tracker_type в Enum
        try:
            tracker_type_enum = TrackerType(request.tracker_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Неизвестный тип трекера: {request.tracker_type}"
            )

        result = agent.block_tracker(
            domain=request.domain,
            tracker_type=tracker_type_enum,
            reason=request.reason
        )

        if not result:
            raise HTTPException(status_code=400, detail="Не удалось заблокировать трекер")

        return {"status": "success", "message": f"Трекер {request.domain} заблокирован"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/unblock", summary="Разблокировка трекера")
async def unblock_tracker(request: UnblockTrackerRequest):
    """
    Разблокировать трекер

    Args:
        domain: Домен трекера
    """
    try:
        agent = get_agent()
        result = agent.unblock_tracker(request.domain)

        if not result:
            raise HTTPException(status_code=400, detail="Не удалось разблокировать трекер")

        return {"status": "success", "message": f"Трекер {request.domain} разблокирован"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", summary="Статус блокировки домена")
async def get_block_status(domain: str = Query(..., description="Домен для проверки")):
    """
    Проверить статус блокировки домена

    Args:
        domain: Домен для проверки

    Returns:
        - blocked: bool - заблокирован ли домен
        - tracker_type: str - тип трекера (если заблокирован)
    """
    try:
        agent = get_agent()
        is_blocked = agent.is_blocked(domain)

        result = {"blocked": is_blocked}
        if is_blocked:
            # Проверяем тип трекера
            tracker_type = agent.is_tracker_domain(domain)
            if tracker_type:
                result["tracker_type"] = tracker_type.value
            else:
                result["tracker_type"] = "blacklist"

        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings", summary="Получение настроек")
async def get_settings():
    """
    Получить текущие настройки блокировки

    Returns:
        - strict_mode: строгий режим
        - enable_analytics_blocking: блокировка аналитики
        - enable_advertising_blocking: блокировка рекламы
        - enable_social_blocking: блокировка социальных трекеров
        - whitelist: белый список
        - blacklist: черный список
    """
    try:
        agent = get_agent()
        settings = {
            "strict_mode": agent.strict_mode,
            "enable_analytics_blocking": agent.enable_analytics_blocking,
            "enable_advertising_blocking": agent.enable_advertising_blocking,
            "enable_social_blocking": agent.enable_social_blocking,
            "whitelist": list(agent.whitelist),
            "blacklist": list(agent.blacklist)
        }
        return {"status": "success", "data": settings}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/settings", summary="Обновление настроек")
async def update_settings(request: SettingsRequest):
    """
    Обновить настройки блокировки

    Args:
        strict_mode: Строгий режим блокировки
        enable_analytics_blocking: Блокировать аналитику
        enable_advertising_blocking: Блокировать рекламу
        enable_social_blocking: Блокировать социальные трекеры
        whitelist: Белый список доменов
        blacklist: Черный список доменов
    """
    try:
        agent = get_agent()

        if request.strict_mode is not None:
            agent.strict_mode = request.strict_mode
        if request.enable_analytics_blocking is not None:
            agent.enable_analytics_blocking = request.enable_analytics_blocking
        if request.enable_advertising_blocking is not None:
            agent.enable_advertising_blocking = request.enable_advertising_blocking
        if request.enable_social_blocking is not None:
            agent.enable_social_blocking = request.enable_social_blocking
        if request.whitelist is not None:
            agent.whitelist = set(request.whitelist)
        if request.blacklist is not None:
            agent.blacklist = set(request.blacklist)

        return {"status": "success", "message": "Настройки обновлены"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", summary="Health check")
async def health_check():
    """
    Проверка работоспособности агента

    Returns:
        - status: статус агента
        - agent_initialized: инициализирован ли агент
        - trackers_count: количество известных трекеров
    """
    try:
        agent = get_agent()
        trackers = agent.get_tracker_lists()
        return {
            "status": "healthy",
            "agent_initialized": True,
            "trackers_count": len(trackers.get("all", [])),
            "patterns_count": len(trackers.get("patterns", []))
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }
