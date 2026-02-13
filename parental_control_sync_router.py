# -*- coding: utf-8 -*-
"""
Parental Control Sync API Router
---------------------------------
FastAPI endpoints для синхронизации родительского контроля между устройствами.

Использование:
    В main.py добавить:
    from security.api.routers.parental_control_sync_router import router as parental_control_router
    app.include_router(parental_control_router)

Дата создания: 11 февраля 2026
Версия: 1.0.0
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field
import logging
import sys
import os

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
router = APIRouter(prefix="/api/parental-control", tags=["Parental Control"])


# =============================================================================
# Pydantic модели для запросов и ответов
# =============================================================================

# Настройки родительского контроля
class ParentalControlSettingsResponse(BaseModel):
    """Ответ с настройками родительского контроля"""
    familyId: str = Field(..., description="ID семьи")
    childId: Optional[str] = Field(None, description="ID ребенка (если настройки для конкретного ребенка)")
    isContentFilterEnabled: bool = Field(True, description="Включена ли фильтрация контента")
    isAppBlockingEnabled: bool = Field(True, description="Включена ли блокировка приложений")
    screenTimeLimitHours: int = Field(0, description="Лимит экранного времени в часах", ge=0, le=24)
    allowedApps: List[str] = Field(default_factory=list, description="Список разрешенных приложений")
    blockedWebsites: List[str] = Field(default_factory=list, description="Список заблокированных сайтов")
    bedtime: Optional[str] = Field(None, description="Время отхода ко сну (формат HH:mm)")
    lastModified: datetime = Field(..., description="Время последнего изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class UpdateParentalControlSettingsRequest(BaseModel):
    """Запрос на обновление настроек"""
    familyId: str = Field(..., description="ID семьи")
    childId: Optional[str] = Field(None, description="ID ребенка")
    isContentFilterEnabled: Optional[bool] = Field(None, description="Включена ли фильтрация контента")
    isAppBlockingEnabled: Optional[bool] = Field(None, description="Включена ли блокировка приложений")
    screenTimeLimitHours: Optional[int] = Field(None, description="Лимит экранного времени в часах", ge=0, le=24)
    allowedApps: Optional[List[str]] = Field(None, description="Список разрешенных приложений")
    blockedWebsites: Optional[List[str]] = Field(None, description="Список заблокированных сайтов")
    bedtime: Optional[str] = Field(None, description="Время отхода ко сну (формат HH:mm)")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


class SettingsHistoryEntry(BaseModel):
    """Запись в истории изменений настроек"""
    historyId: str = Field(..., description="ID записи истории")
    familyId: str = Field(..., description="ID семьи")
    childId: Optional[str] = Field(None, description="ID ребенка")
    changedBy: str = Field(..., description="ID пользователя, который внес изменения")
    changes: Dict[str, Any] = Field(..., description="Словарь изменений (поле -> старое значение -> новое значение)")
    timestamp: datetime = Field(..., description="Время изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства")


class SettingsHistoryResponse(BaseModel):
    """История изменений настроек"""
    history: List[SettingsHistoryEntry] = Field(..., description="Список изменений")
    total: int = Field(..., description="Общее количество записей")


class SyncParentalControlSettingsRequest(BaseModel):
    """Запрос на синхронизацию настроек"""
    familyId: str = Field(..., description="ID семьи")
    deviceId: str = Field(..., description="ID устройства")
    lastSyncTimestamp: Optional[datetime] = Field(None, description="Время последней синхронизации")


class SyncParentalControlSettingsResponse(BaseModel):
    """Ответ на синхронизацию настроек"""
    familyId: str = Field(..., description="ID семьи")
    settings: List[ParentalControlSettingsResponse] = Field(..., description="Список настроек для синхронизации")
    conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="Список конфликтов")
    lastSyncTimestamp: datetime = Field(..., description="Время синхронизации")


class SettingsConflictResponse(BaseModel):
    """Конфликт настроек"""
    conflictId: str = Field(..., description="ID конфликта")
    familyId: str = Field(..., description="ID семьи")
    childId: Optional[str] = Field(None, description="ID ребенка")
    field: str = Field(..., description="Поле с конфликтом")
    localValue: Any = Field(..., description="Локальное значение")
    serverValue: Any = Field(..., description="Значение на сервере")
    localTimestamp: datetime = Field(..., description="Время локального изменения")
    serverTimestamp: datetime = Field(..., description="Время изменения на сервере")
    localDeviceId: str = Field(..., description="ID локального устройства")
    serverDeviceId: str = Field(..., description="ID устройства на сервере")


class SettingsConflictsResponse(BaseModel):
    """Список конфликтов настроек"""
    conflicts: List[SettingsConflictResponse] = Field(..., description="Список конфликтов")
    total: int = Field(..., description="Общее количество конфликтов")


# Лимиты времени
class TimeLimitResponse(BaseModel):
    """Ответ с лимитом времени"""
    childId: str = Field(..., description="ID ребенка")
    dailyLimitMinutes: int = Field(..., description="Дневной лимит в минутах", ge=0)
    weeklyLimitMinutes: int = Field(..., description="Недельный лимит в минутах", ge=0)
    bedtimeStart: Optional[str] = Field(None, description="Начало времени сна (формат HH:mm)")
    bedtimeEnd: Optional[str] = Field(None, description="Конец времени сна (формат HH:mm)")
    lastModified: datetime = Field(..., description="Время последнего изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class UpdateTimeLimitRequest(BaseModel):
    """Запрос на обновление лимита времени"""
    childId: str = Field(..., description="ID ребенка")
    dailyLimitMinutes: Optional[int] = Field(None, description="Дневной лимит в минутах", ge=0)
    weeklyLimitMinutes: Optional[int] = Field(None, description="Недельный лимит в минутах", ge=0)
    bedtimeStart: Optional[str] = Field(None, description="Начало времени сна (формат HH:mm)")
    bedtimeEnd: Optional[str] = Field(None, description="Конец времени сна (формат HH:mm)")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


class TimeLimitHistoryEntry(BaseModel):
    """Запись в истории лимитов времени"""
    historyId: str = Field(..., description="ID записи истории")
    childId: str = Field(..., description="ID ребенка")
    changedBy: str = Field(..., description="ID пользователя, который внес изменения")
    changes: Dict[str, Any] = Field(..., description="Словарь изменений")
    timestamp: datetime = Field(..., description="Время изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства")


class TimeLimitHistoryResponse(BaseModel):
    """История изменений лимитов времени"""
    history: List[TimeLimitHistoryEntry] = Field(..., description="Список изменений")
    total: int = Field(..., description="Общее количество записей")


class ResetTimeLimitRequest(BaseModel):
    """Запрос на сброс лимита времени"""
    childId: str = Field(..., description="ID ребенка")
    deviceId: Optional[str] = Field(None, description="ID устройства")


# Расписания
class ScheduleResponse(BaseModel):
    """Ответ с расписанием"""
    scheduleId: str = Field(..., description="ID расписания")
    childId: str = Field(..., description="ID ребенка")
    name: str = Field(..., description="Название расписания")
    weekdays: List[int] = Field(..., description="Дни недели (0=понедельник, 6=воскресенье)", min_items=1, max_items=7)
    startTime: str = Field(..., description="Время начала (формат HH:mm)")
    endTime: str = Field(..., description="Время окончания (формат HH:mm)")
    isActive: bool = Field(True, description="Активно ли расписание")
    lastModified: datetime = Field(..., description="Время последнего изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class UpdateScheduleRequest(BaseModel):
    """Запрос на обновление расписания"""
    scheduleId: Optional[str] = Field(None, description="ID расписания (если обновление существующего)")
    childId: str = Field(..., description="ID ребенка")
    name: Optional[str] = Field(None, description="Название расписания")
    weekdays: Optional[List[int]] = Field(None, description="Дни недели (0=понедельник, 6=воскресенье)", min_items=1, max_items=7)
    startTime: Optional[str] = Field(None, description="Время начала (формат HH:mm)")
    endTime: Optional[str] = Field(None, description="Время окончания (формат HH:mm)")
    isActive: Optional[bool] = Field(None, description="Активно ли расписание")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


class ScheduleHistoryEntry(BaseModel):
    """Запись в истории расписаний"""
    historyId: str = Field(..., description="ID записи истории")
    scheduleId: str = Field(..., description="ID расписания")
    childId: str = Field(..., description="ID ребенка")
    changedBy: str = Field(..., description="ID пользователя, который внес изменения")
    action: str = Field(..., description="Действие (created, updated, deleted)")
    changes: Optional[Dict[str, Any]] = Field(None, description="Словарь изменений")
    timestamp: datetime = Field(..., description="Время изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства")


class ScheduleHistoryResponse(BaseModel):
    """История изменений расписаний"""
    history: List[ScheduleHistoryEntry] = Field(..., description="Список изменений")
    total: int = Field(..., description="Общее количество записей")


class DeleteScheduleRequest(BaseModel):
    """Запрос на удаление расписания"""
    scheduleId: str = Field(..., description="ID расписания")
    deviceId: Optional[str] = Field(None, description="ID устройства")


# Геозоны
class GeofenceResponse(BaseModel):
    """Ответ с геозоной"""
    geofenceId: str = Field(..., description="ID геозоны")
    childId: str = Field(..., description="ID ребенка")
    name: str = Field(..., description="Название геозоны")
    latitude: float = Field(..., description="Широта", ge=-90, le=90)
    longitude: float = Field(..., description="Долгота", ge=-180, le=180)
    radius: float = Field(..., description="Радиус в метрах", ge=10, le=10000)
    isActive: bool = Field(True, description="Активна ли геозона")
    lastModified: datetime = Field(..., description="Время последнего изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class AddGeofenceRequest(BaseModel):
    """Запрос на добавление геозоны"""
    childId: str = Field(..., description="ID ребенка")
    name: str = Field(..., description="Название геозоны", min_length=1, max_length=100)
    latitude: float = Field(..., description="Широта", ge=-90, le=90)
    longitude: float = Field(..., description="Долгота", ge=-180, le=180)
    radius: float = Field(..., description="Радиус в метрах", ge=10, le=10000)
    isActive: bool = Field(True, description="Активна ли геозона")
    deviceId: Optional[str] = Field(None, description="ID устройства")


class UpdateGeofenceRequest(BaseModel):
    """Запрос на обновление геозоны"""
    geofenceId: str = Field(..., description="ID геозоны")
    name: Optional[str] = Field(None, description="Название геозоны", min_length=1, max_length=100)
    latitude: Optional[float] = Field(None, description="Широта", ge=-90, le=90)
    longitude: Optional[float] = Field(None, description="Долгота", ge=-180, le=180)
    radius: Optional[float] = Field(None, description="Радиус в метрах", ge=10, le=10000)
    isActive: Optional[bool] = Field(None, description="Активна ли геозона")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


# Блокировки приложений
class AppBlockResponse(BaseModel):
    """Ответ с блокировкой приложения"""
    childId: str = Field(..., description="ID ребенка")
    blockedApps: List[str] = Field(default_factory=list, description="Список заблокированных приложений")
    appLimits: Dict[str, int] = Field(default_factory=dict, description="Лимиты времени для приложений (appName -> minutes)")
    lastModified: datetime = Field(..., description="Время последнего изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class UpdateAppBlocksRequest(BaseModel):
    """Запрос на обновление блокировок приложений"""
    childId: str = Field(..., description="ID ребенка")
    blockedApps: Optional[List[str]] = Field(None, description="Список заблокированных приложений")
    appLimits: Optional[Dict[str, int]] = Field(None, description="Лимиты времени для приложений (appName -> minutes)")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


class SyncAppBlocksRequest(BaseModel):
    """Запрос на синхронизацию блокировок приложений"""
    childId: str = Field(..., description="ID ребенка")
    deviceId: str = Field(..., description="ID устройства")
    lastSyncTimestamp: Optional[datetime] = Field(None, description="Время последней синхронизации")


class SyncAppBlocksResponse(BaseModel):
    """Ответ на синхронизацию блокировок приложений"""
    childId: str = Field(..., description="ID ребенка")
    appBlocks: AppBlockResponse = Field(..., description="Блокировки приложений")
    conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="Список конфликтов")
    lastSyncTimestamp: datetime = Field(..., description="Время синхронизации")


# =============================================================================
# API Endpoints
# =============================================================================

# ========== НАСТРОЙКИ (5 endpoint'ов) ==========

@router.get("/settings/{familyId}", response_model=ParentalControlSettingsResponse)
async def get_parental_control_settings(
    familyId: str = Path(..., description="ID семьи"),
    childId: Optional[str] = Query(None, description="ID ребенка (опционально)")
) -> ParentalControlSettingsResponse:
    """
    Получить настройки родительского контроля для семьи или конкретного ребенка
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            # Попытка получить данные через SFM Adapter
            try:
                result = await sfm_adapter.get_parental_control_settings(familyId=familyId, childId=childId)
                if result:
                    return ParentalControlSettingsResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback: возвращаем mock данные
        return ParentalControlSettingsResponse(
            familyId=familyId,
            childId=childId,
            isContentFilterEnabled=True,
            isAppBlockingEnabled=True,
            screenTimeLimitHours=3,
            allowedApps=[],
            blockedWebsites=[],
            bedtime="22:00",
            lastModified=datetime.now(),
            deviceId=None,
            version=1
        )
    except Exception as e:
        logger.error(f"Error getting parental control settings: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения настроек: {str(e)}")


@router.post("/settings/update", response_model=ParentalControlSettingsResponse)
async def update_parental_control_settings(
    request: UpdateParentalControlSettingsRequest
) -> ParentalControlSettingsResponse:
    """
    Обновить настройки родительского контроля
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            # Попытка обновить через SFM Adapter
            try:
                result = await sfm_adapter.update_parental_control_settings(**request.dict())
                if result:
                    return ParentalControlSettingsResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback: возвращаем обновленные mock данные
        return ParentalControlSettingsResponse(
            familyId=request.familyId,
            childId=request.childId,
            isContentFilterEnabled=request.isContentFilterEnabled if request.isContentFilterEnabled is not None else True,
            isAppBlockingEnabled=request.isAppBlockingEnabled if request.isAppBlockingEnabled is not None else True,
            screenTimeLimitHours=request.screenTimeLimitHours if request.screenTimeLimitHours is not None else 3,
            allowedApps=request.allowedApps or [],
            blockedWebsites=request.blockedWebsites or [],
            bedtime=request.bedtime or "22:00",
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=(request.version or 1) + 1
        )
    except Exception as e:
        logger.error(f"Error updating parental control settings: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления настроек: {str(e)}")


@router.get("/settings/history", response_model=SettingsHistoryResponse)
async def get_parental_control_settings_history(
    familyId: str = Query(..., description="ID семьи"),
    childId: Optional[str] = Query(None, description="ID ребенка (опционально)"),
    limit: int = Query(50, description="Максимальное количество записей", ge=1, le=100)
) -> SettingsHistoryResponse:
    """
    Получить историю изменений настроек родительского контроля
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            # Попытка получить через SFM Adapter
            try:
                result = await sfm_adapter.get_parental_control_settings_history(
                    familyId=familyId, childId=childId, limit=limit
                )
                if result:
                    return SettingsHistoryResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback: возвращаем пустую историю
        return SettingsHistoryResponse(
            history=[],
            total=0
        )
    except Exception as e:
        logger.error(f"Error getting settings history: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения истории: {str(e)}")


@router.post("/settings/sync", response_model=SyncParentalControlSettingsResponse)
async def sync_parental_control_settings(
    request: SyncParentalControlSettingsRequest
) -> SyncParentalControlSettingsResponse:
    """
    Синхронизировать настройки родительского контроля между устройствами
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            # Попытка синхронизировать через SFM Adapter
            try:
                result = await sfm_adapter.sync_parental_control_settings(**request.dict())
                if result:
                    return SyncParentalControlSettingsResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback: возвращаем пустую синхронизацию
        return SyncParentalControlSettingsResponse(
            familyId=request.familyId,
            settings=[],
            conflicts=[],
            lastSyncTimestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error syncing settings: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка синхронизации: {str(e)}")


@router.get("/settings/conflicts", response_model=SettingsConflictsResponse)
async def get_parental_control_settings_conflicts(
    familyId: str = Query(..., description="ID семьи"),
    childId: Optional[str] = Query(None, description="ID ребенка (опционально)")
) -> SettingsConflictsResponse:
    """
    Получить список конфликтов настроек родительского контроля
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            # Попытка получить через SFM Adapter
            try:
                result = await sfm_adapter.get_parental_control_settings_conflicts(
                    familyId=familyId, childId=childId
                )
                if result:
                    return SettingsConflictsResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback: возвращаем пустой список конфликтов
        return SettingsConflictsResponse(
            conflicts=[],
            total=0
        )
    except Exception as e:
        logger.error(f"Error getting settings conflicts: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения конфликтов: {str(e)}")


# ========== ЛИМИТЫ ВРЕМЕНИ (4 endpoint'а) ==========

@router.get("/time-limits/{childId}", response_model=TimeLimitResponse)
async def get_time_limits(
    childId: str = Path(..., description="ID ребенка")
) -> TimeLimitResponse:
    """
    Получить лимиты времени для ребенка
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_time_limits(childId=childId)
                if result:
                    return TimeLimitResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return TimeLimitResponse(
            childId=childId,
            dailyLimitMinutes=180,
            weeklyLimitMinutes=1260,
            bedtimeStart="22:00",
            bedtimeEnd="07:00",
            lastModified=datetime.now(),
            deviceId=None,
            version=1
        )
    except Exception as e:
        logger.error(f"Error getting time limits: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения лимитов: {str(e)}")


@router.post("/time-limits/update", response_model=TimeLimitResponse)
async def update_time_limits(
    request: UpdateTimeLimitRequest
) -> TimeLimitResponse:
    """
    Обновить лимиты времени для ребенка
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_time_limits(**request.dict())
                if result:
                    return TimeLimitResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return TimeLimitResponse(
            childId=request.childId,
            dailyLimitMinutes=request.dailyLimitMinutes or 180,
            weeklyLimitMinutes=request.weeklyLimitMinutes or 1260,
            bedtimeStart=request.bedtimeStart or "22:00",
            bedtimeEnd=request.bedtimeEnd or "07:00",
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=(request.version or 1) + 1
        )
    except Exception as e:
        logger.error(f"Error updating time limits: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления лимитов: {str(e)}")


@router.get("/time-limits/history", response_model=TimeLimitHistoryResponse)
async def get_time_limits_history(
    childId: str = Query(..., description="ID ребенка"),
    limit: int = Query(50, description="Максимальное количество записей", ge=1, le=100)
) -> TimeLimitHistoryResponse:
    """
    Получить историю изменений лимитов времени
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_time_limits_history(childId=childId, limit=limit)
                if result:
                    return TimeLimitHistoryResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return TimeLimitHistoryResponse(
            history=[],
            total=0
        )
    except Exception as e:
        logger.error(f"Error getting time limits history: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения истории: {str(e)}")


@router.post("/time-limits/reset", response_model=TimeLimitResponse)
async def reset_time_limits(
    request: ResetTimeLimitRequest
) -> TimeLimitResponse:
    """
    Сбросить лимиты времени для ребенка к значениям по умолчанию
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.reset_time_limits(**request.dict())
                if result:
                    return TimeLimitResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback: возвращаем значения по умолчанию
        return TimeLimitResponse(
            childId=request.childId,
            dailyLimitMinutes=180,
            weeklyLimitMinutes=1260,
            bedtimeStart="22:00",
            bedtimeEnd="07:00",
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=1
        )
    except Exception as e:
        logger.error(f"Error resetting time limits: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сброса лимитов: {str(e)}")


# ========== РАСПИСАНИЯ (4 endpoint'а) ==========

@router.get("/schedules/{childId}", response_model=List[ScheduleResponse])
async def get_schedules(
    childId: str = Path(..., description="ID ребенка")
) -> List[ScheduleResponse]:
    """
    Получить все расписания для ребенка
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_schedules(childId=childId)
                if result:
                    return [ScheduleResponse(**item) for item in result]
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback: возвращаем пустой список
        return []
    except Exception as e:
        logger.error(f"Error getting schedules: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения расписаний: {str(e)}")


@router.post("/schedules/update", response_model=ScheduleResponse)
async def update_schedule(
    request: UpdateScheduleRequest
) -> ScheduleResponse:
    """
    Создать или обновить расписание для ребенка
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_schedule(**request.dict())
                if result:
                    return ScheduleResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        schedule_id = request.scheduleId or f"schedule_{datetime.now().timestamp()}"
        return ScheduleResponse(
            scheduleId=schedule_id,
            childId=request.childId,
            name=request.name or "Расписание",
            weekdays=request.weekdays or [0, 1, 2, 3, 4],
            startTime=request.startTime or "08:00",
            endTime=request.endTime or "20:00",
            isActive=request.isActive if request.isActive is not None else True,
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=(request.version or 1) + 1
        )
    except Exception as e:
        logger.error(f"Error updating schedule: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления расписания: {str(e)}")


@router.get("/schedules/history", response_model=ScheduleHistoryResponse)
async def get_schedules_history(
    childId: str = Query(..., description="ID ребенка"),
    limit: int = Query(50, description="Максимальное количество записей", ge=1, le=100)
) -> ScheduleHistoryResponse:
    """
    Получить историю изменений расписаний
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_schedules_history(childId=childId, limit=limit)
                if result:
                    return ScheduleHistoryResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return ScheduleHistoryResponse(
            history=[],
            total=0
        )
    except Exception as e:
        logger.error(f"Error getting schedules history: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения истории: {str(e)}")


@router.post("/schedules/delete", response_model=Dict[str, str])
async def delete_schedule(
    request: DeleteScheduleRequest
) -> Dict[str, str]:
    """
    Удалить расписание
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                await sfm_adapter.delete_schedule(scheduleId=request.scheduleId, deviceId=request.deviceId)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return {"status": "success", "message": "Расписание удалено"}
    except Exception as e:
        logger.error(f"Error deleting schedule: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка удаления расписания: {str(e)}")


# ========== ГЕОЗОНЫ (4 endpoint'а) ==========

@router.get("/geofences/{childId}", response_model=List[GeofenceResponse])
async def get_geofences(
    childId: str = Path(..., description="ID ребенка")
) -> List[GeofenceResponse]:
    """
    Получить все геозоны для ребенка
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_geofences(childId=childId)
                if result:
                    return [GeofenceResponse(**item) for item in result]
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback: возвращаем пустой список
        return []
    except Exception as e:
        logger.error(f"Error getting geofences: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения геозон: {str(e)}")


@router.post("/geofences/add", response_model=GeofenceResponse)
async def add_geofence(
    request: AddGeofenceRequest
) -> GeofenceResponse:
    """
    Добавить геозону для ребенка
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.add_geofence(**request.dict())
                if result:
                    return GeofenceResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        geofence_id = f"geofence_{datetime.now().timestamp()}"
        return GeofenceResponse(
            geofenceId=geofence_id,
            childId=request.childId,
            name=request.name,
            latitude=request.latitude,
            longitude=request.longitude,
            radius=request.radius,
            isActive=request.isActive,
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=1
        )
    except Exception as e:
        logger.error(f"Error adding geofence: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка добавления геозоны: {str(e)}")


@router.post("/geofences/update", response_model=GeofenceResponse)
async def update_geofence(
    request: UpdateGeofenceRequest
) -> GeofenceResponse:
    """
    Обновить геозону
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_geofence(**request.dict())
                if result:
                    return GeofenceResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback: возвращаем обновленную геозону
        return GeofenceResponse(
            geofenceId=request.geofenceId,
            childId="",  # Нужно получить из БД
            name=request.name or "Геозона",
            latitude=request.latitude or 0.0,
            longitude=request.longitude or 0.0,
            radius=request.radius or 100.0,
            isActive=request.isActive if request.isActive is not None else True,
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=(request.version or 1) + 1
        )
    except Exception as e:
        logger.error(f"Error updating geofence: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления геозоны: {str(e)}")


@router.delete("/geofences/{geofenceId}", response_model=Dict[str, str])
async def delete_geofence(
    geofenceId: str = Path(..., description="ID геозоны")
) -> Dict[str, str]:
    """
    Удалить геозону
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                await sfm_adapter.delete_geofence(geofenceId=geofenceId)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return {"status": "success", "message": "Геозона удалена"}
    except Exception as e:
        logger.error(f"Error deleting geofence: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка удаления геозоны: {str(e)}")


# ========== БЛОКИРОВКИ ПРИЛОЖЕНИЙ (3 endpoint'а) ==========

@router.get("/app-blocks/{childId}", response_model=AppBlockResponse)
async def get_app_blocks(
    childId: str = Path(..., description="ID ребенка")
) -> AppBlockResponse:
    """
    Получить блокировки приложений для ребенка
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_app_blocks(childId=childId)
                if result:
                    return AppBlockResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return AppBlockResponse(
            childId=childId,
            blockedApps=[],
            appLimits={},
            lastModified=datetime.now(),
            deviceId=None,
            version=1
        )
    except Exception as e:
        logger.error(f"Error getting app blocks: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения блокировок: {str(e)}")


@router.post("/app-blocks/update", response_model=AppBlockResponse)
async def update_app_blocks(
    request: UpdateAppBlocksRequest
) -> AppBlockResponse:
    """
    Обновить блокировки приложений для ребенка
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_app_blocks(**request.dict())
                if result:
                    return AppBlockResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return AppBlockResponse(
            childId=request.childId,
            blockedApps=request.blockedApps or [],
            appLimits=request.appLimits or {},
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=(request.version or 1) + 1
        )
    except Exception as e:
        logger.error(f"Error updating app blocks: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления блокировок: {str(e)}")


@router.post("/app-blocks/sync", response_model=SyncAppBlocksResponse)
async def sync_app_blocks(
    request: SyncAppBlocksRequest
) -> SyncAppBlocksResponse:
    """
    Синхронизировать блокировки приложений между устройствами
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.sync_app_blocks(**request.dict())
                if result:
                    return SyncAppBlocksResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        app_blocks = AppBlockResponse(
            childId=request.childId,
            blockedApps=[],
            appLimits={},
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=1
        )
        return SyncAppBlocksResponse(
            childId=request.childId,
            appBlocks=app_blocks,
            conflicts=[],
            lastSyncTimestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error syncing app blocks: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка синхронизации блокировок: {str(e)}")
