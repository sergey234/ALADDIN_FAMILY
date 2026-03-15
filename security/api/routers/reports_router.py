# -*- coding: utf-8 -*-
"""
Reports API Router - Статистика отчетов безопасности
----------------------------------------------------
FastAPI endpoints для получения статистики по различным типам отчетов.

Использование:
    В main.py добавить:
    from security.api.routers.reports_router import router as reports_router
    app.include_router(reports_router)

Дата создания: 14 марта 2026
Версия: 1.0.0
✅ ВАРИАНТ 5: Гибридный подход - создание единого роутера для всех stats endpoints
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
import logging
import sys
import os

# SFM Adapter import
backend_path = "/opt/aladdin-backend"
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    # Пробуем импортировать как в других роутерах
    from sfm_adapter import sfm_adapter
    SFM_ADAPTER_AVAILABLE = True
    get_sfm_function_name = None
except ImportError:
    try:
        # Fallback: импортируем напрямую
        from sfm_adapter_server import SFMAdapter
        from complete_api_sfm_mapping import get_sfm_function_name
        sfm_adapter = SFMAdapter()
        SFM_ADAPTER_AVAILABLE = True
    except ImportError as e:
        SFM_ADAPTER_AVAILABLE = False
        sfm_adapter = None
        get_sfm_function_name = None
        print(f"⚠️ SFM Adapter not available: {e}")

logger = logging.getLogger(__name__)

# Создаем FastAPI Router
router = APIRouter(prefix="/api/reports", tags=["Reports"])


# =============================================================================
# Pydantic модели для запросов и ответов
# =============================================================================

class ReportStatsResponse(BaseModel):
    """Базовая модель ответа для статистики отчетов"""
    total: int = Field(0, description="Общее количество")
    blocked: int = Field(0, description="Заблокировано")
    allowed: int = Field(0, description="Разрешено")
    last_24h: int = Field(0, description="За последние 24 часа")
    last_7d: int = Field(0, description="За последние 7 дней")
    last_30d: int = Field(0, description="За последние 30 дней")
    source: str = Field("sfm", description="Источник данных")
    timestamp: Optional[datetime] = Field(None, description="Временная метка")


# =============================================================================
# Helper функции
# =============================================================================

def _get_fallback_stats() -> Dict[str, Any]:
    """Fallback статистика если SFM adapter недоступен"""
    return {
        "total": 0,
        "blocked": 0,
        "allowed": 0,
        "last_24h": 0,
        "last_7d": 0,
        "last_30d": 0,
        "source": "mock",
        "timestamp": datetime.now().isoformat()
    }


async def _call_sfm_function(func_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Вызвать SFM функцию через adapter
    
    Args:
        func_name: Имя функции API (например, "get_driving_reports_stats")
        params: Параметры для функции
    
    Returns:
        Результат выполнения функции
    """
    if not SFM_ADAPTER_AVAILABLE or not sfm_adapter:
        logger.warning(f"SFM Adapter недоступен, возвращаем fallback для {func_name}")
        return _get_fallback_stats()
    
    try:
        # Если есть get_sfm_function_name - используем маппинг
        if get_sfm_function_name:
            sfm_function_name = get_sfm_function_name(func_name)
            logger.info(f"🔄 Вызов SFM функции: {func_name} → {sfm_function_name}")
        else:
            # Используем имя функции как есть
            sfm_function_name = func_name
            logger.info(f"🔄 Вызов SFM функции: {func_name}")
        
        # Вызываем SFM функцию
        success, result, message = sfm_adapter.execute_function(sfm_function_name, params or {})
        
        if success:
            logger.info(f"✅ SFM функция выполнена успешно: {sfm_function_name}")
            # Убеждаемся, что результат имеет правильный формат
            if isinstance(result, dict):
                result.setdefault("source", "sfm_real")
                result.setdefault("timestamp", datetime.now().isoformat())
            return result
        else:
            logger.warning(f"⚠️ SFM функция не выполнена: {message}, используем fallback")
            return _get_fallback_stats()
    except Exception as e:
        logger.error(f"❌ Ошибка вызова SFM функции {func_name}: {e}")
        return _get_fallback_stats()


# =============================================================================
# API Endpoints (7 endpoints для stats)
# =============================================================================

# 1. GET /api/reports/driving/stats - Статистика отчетов о вождении
@router.get("/driving/stats", response_model=ReportStatsResponse)
async def get_driving_reports_stats(
    user_id: Optional[str] = Query(None, description="ID пользователя")
) -> ReportStatsResponse:
    """
    Получить статистику отчетов о вождении
    
    Returns:
        Статистика отчетов о вождении
    """
    params = {}
    if user_id:
        params["user_id"] = user_id
    
    result = await _call_sfm_function("get_driving_reports_stats", params)
    return ReportStatsResponse(**result)


# 2. GET /api/reports/dark-web/stats - Статистика мониторинга Dark Web
@router.get("/dark-web/stats", response_model=ReportStatsResponse)
async def get_dark_web_stats(
    user_id: Optional[str] = Query(None, description="ID пользователя")
) -> ReportStatsResponse:
    """
    Получить статистику мониторинга Dark Web
    
    Returns:
        Статистика мониторинга Dark Web
    """
    params = {}
    if user_id:
        params["user_id"] = user_id
    
    result = await _call_sfm_function("get_darkweb_stats", params)
    return ReportStatsResponse(**result)


# 3. GET /api/reports/identity-theft/stats - Статистика защиты от кражи личности
@router.get("/identity-theft/stats", response_model=ReportStatsResponse)
async def get_identity_theft_stats(
    user_id: Optional[str] = Query(None, description="ID пользователя")
) -> ReportStatsResponse:
    """
    Получить статистику защиты от кражи личности
    
    Returns:
        Статистика защиты от кражи личности
    """
    params = {}
    if user_id:
        params["user_id"] = user_id
    
    result = await _call_sfm_function("get_identity_theft_stats", params)
    return ReportStatsResponse(**result)


# 4. GET /api/reports/privacy/location/stats - Статистика геолокации
@router.get("/privacy/location/stats", response_model=ReportStatsResponse)
async def get_location_stats(
    user_id: Optional[str] = Query(None, description="ID пользователя")
) -> ReportStatsResponse:
    """
    Получить статистику геолокации
    
    Returns:
        Статистика геолокации
    """
    params = {}
    if user_id:
        params["user_id"] = user_id
    
    result = await _call_sfm_function("get_location_stats", params)
    return ReportStatsResponse(**result)


# 5. GET /api/reports/privacy/cleanup/stats - Статистика очистки данных
@router.get("/privacy/cleanup/stats", response_model=ReportStatsResponse)
async def get_cleanup_stats(
    user_id: Optional[str] = Query(None, description="ID пользователя")
) -> ReportStatsResponse:
    """
    Получить статистику очистки данных
    
    Returns:
        Статистика очистки данных
    """
    params = {}
    if user_id:
        params["user_id"] = user_id
    
    result = await _call_sfm_function("get_data_cleanup_stats", params)
    return ReportStatsResponse(**result)


# 6. GET /api/reports/privacy/tracker/stats - Статистика анти-трекера
@router.get("/privacy/tracker/stats", response_model=ReportStatsResponse)
async def get_tracker_stats(
    user_id: Optional[str] = Query(None, description="ID пользователя")
) -> ReportStatsResponse:
    """
    Получить статистику анти-трекера
    
    Returns:
        Статистика анти-трекера
    """
    params = {}
    if user_id:
        params["user_id"] = user_id
    
    result = await _call_sfm_function("get_anti_tracker_stats", params)
    return ReportStatsResponse(**result)


# 7. GET /api/reports/ai-categories/stats - Статистика AI категорий
@router.get("/ai-categories/stats", response_model=ReportStatsResponse)
async def get_ai_categories_stats(
    user_id: Optional[str] = Query(None, description="ID пользователя")
) -> ReportStatsResponse:
    """
    Получить статистику AI категорий
    
    Returns:
        Статистика AI категорий
    """
    params = {}
    if user_id:
        params["user_id"] = user_id
    
    result = await _call_sfm_function("get_ai_categories_stats", params)
    return ReportStatsResponse(**result)
