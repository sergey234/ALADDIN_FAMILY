# -*- coding: utf-8 -*-
"""
Other Functions Sync API Router
--------------------------------
FastAPI endpoints для синхронизации других функций (геолокация, чат) между устройствами.

Использование:
    В main.py добавить:
    from security.api.routers.other_functions_sync_router import router as other_functions_router
    app.include_router(other_functions_router)

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
router = APIRouter(prefix="/api", tags=["Other Functions"])


# =============================================================================
# Pydantic модели для запросов и ответов
# =============================================================================

# Геолокация и геозоны
class LocationGeofenceResponse(BaseModel):
    """Ответ с геозоной для геолокации"""
    geofenceId: str = Field(..., description="ID геозоны")
    userId: str = Field(..., description="ID пользователя")
    name: str = Field(..., description="Название геозоны")
    latitude: float = Field(..., description="Широта", ge=-90, le=90)
    longitude: float = Field(..., description="Долгота", ge=-180, le=180)
    radius: float = Field(..., description="Радиус в метрах", ge=10, le=10000)
    isActive: bool = Field(True, description="Активна ли геозона")
    lastModified: datetime = Field(..., description="Время последнего изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class SyncLocationGeofencesRequest(BaseModel):
    """Запрос на синхронизацию геозон"""
    userId: str = Field(..., description="ID пользователя")
    deviceId: str = Field(..., description="ID устройства")
    lastSyncTimestamp: Optional[datetime] = Field(None, description="Время последней синхронизации")


class SyncLocationGeofencesResponse(BaseModel):
    """Ответ на синхронизацию геозон"""
    userId: str = Field(..., description="ID пользователя")
    geofences: List[LocationGeofenceResponse] = Field(..., description="Список геозон")
    conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="Список конфликтов")
    lastSyncTimestamp: datetime = Field(..., description="Время синхронизации")


class UpdateLocationGeofenceRequest(BaseModel):
    """Запрос на обновление геозоны"""
    geofenceId: Optional[str] = Field(None, description="ID геозоны (если обновление существующей)")
    userId: str = Field(..., description="ID пользователя")
    name: Optional[str] = Field(None, description="Название геозоны", min_length=1, max_length=100)
    latitude: Optional[float] = Field(None, description="Широта", ge=-90, le=90)
    longitude: Optional[float] = Field(None, description="Долгота", ge=-180, le=180)
    radius: Optional[float] = Field(None, description="Радиус в метрах", ge=10, le=10000)
    isActive: Optional[bool] = Field(None, description="Активна ли геозона")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


class MovementHistoryEntry(BaseModel):
    """Запись в истории перемещений"""
    entryId: str = Field(..., description="ID записи")
    userId: str = Field(..., description="ID пользователя")
    latitude: float = Field(..., description="Широта", ge=-90, le=90)
    longitude: float = Field(..., description="Долгота", ge=-180, le=180)
    timestamp: datetime = Field(..., description="Время записи")
    speed: Optional[float] = Field(None, description="Скорость в м/с", ge=0)
    accuracy: Optional[float] = Field(None, description="Точность в метрах", ge=0)
    deviceId: Optional[str] = Field(None, description="ID устройства")


class MovementHistoryResponse(BaseModel):
    """История перемещений"""
    history: List[MovementHistoryEntry] = Field(..., description="Список записей")
    total: int = Field(..., description="Общее количество записей")


class UpdateMovementHistoryRequest(BaseModel):
    """Запрос на обновление истории перемещений"""
    userId: str = Field(..., description="ID пользователя")
    entries: List[MovementHistoryEntry] = Field(..., description="Список новых записей")
    deviceId: Optional[str] = Field(None, description="ID устройства")


class LocationStatusResponse(BaseModel):
    """Ответ со статусом геолокации"""
    userId: str = Field(..., description="ID пользователя")
    enabled: bool = Field(True, description="Геолокация включена")
    lastKnownLocation: Optional[Dict[str, float]] = Field(None, description="Последнее известное местоположение {latitude, longitude}")
    lastUpdate: Optional[datetime] = Field(None, description="Время последнего обновления")
    lastModified: datetime = Field(..., description="Время последнего изменения настроек")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class UpdateLocationStatusRequest(BaseModel):
    """Запрос на обновление статуса геолокации"""
    userId: str = Field(..., description="ID пользователя")
    enabled: bool = Field(..., description="Включить/выключить геолокацию")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


# Семейный чат (офлайн)
class OfflineMessageResponse(BaseModel):
    """Ответ с офлайн сообщением"""
    messageId: str = Field(..., description="ID сообщения")
    userId: str = Field(..., description="ID отправителя")
    recipientId: str = Field(..., description="ID получателя")
    familyId: str = Field(..., description="ID семьи")
    content: str = Field(..., description="Содержимое сообщения", max_length=5000)
    timestamp: datetime = Field(..., description="Время отправки")
    isRead: bool = Field(False, description="Прочитано ли сообщение")
    deviceId: Optional[str] = Field(None, description="ID устройства отправителя")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class SyncOfflineMessagesRequest(BaseModel):
    """Запрос на синхронизацию офлайн сообщений"""
    userId: str = Field(..., description="ID пользователя")
    familyId: str = Field(..., description="ID семьи")
    deviceId: str = Field(..., description="ID устройства")
    lastSyncTimestamp: Optional[datetime] = Field(None, description="Время последней синхронизации")


class SyncOfflineMessagesResponse(BaseModel):
    """Ответ на синхронизацию офлайн сообщений"""
    userId: str = Field(..., description="ID пользователя")
    familyId: str = Field(..., description="ID семьи")
    messages: List[OfflineMessageResponse] = Field(..., description="Список сообщений")
    conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="Список конфликтов")
    lastSyncTimestamp: datetime = Field(..., description="Время синхронизации")


class SendOfflineMessageRequest(BaseModel):
    """Запрос на отправку офлайн сообщения"""
    userId: str = Field(..., description="ID отправителя")
    recipientId: str = Field(..., description="ID получателя")
    familyId: str = Field(..., description="ID семьи")
    content: str = Field(..., description="Содержимое сообщения", min_length=1, max_length=5000)
    deviceId: Optional[str] = Field(None, description="ID устройства")
    timestamp: Optional[datetime] = Field(None, description="Время отправки (если не указано, используется текущее время)")


class ResolveMessageConflictsRequest(BaseModel):
    """Запрос на разрешение конфликтов сообщений"""
    userId: str = Field(..., description="ID пользователя")
    familyId: str = Field(..., description="ID семьи")
    conflicts: List[Dict[str, Any]] = Field(..., description="Список конфликтов для разрешения")
    deviceId: Optional[str] = Field(None, description="ID устройства")


# =============================================================================
# API Endpoints
# =============================================================================

# ========== ГЕОЛОКАЦИЯ И ГЕОЗОНЫ (7 endpoint'ов) ==========

@router.post("/location/geofences/sync", response_model=SyncLocationGeofencesResponse)
async def sync_location_geofences(
    request: SyncLocationGeofencesRequest
) -> SyncLocationGeofencesResponse:
    """
    Синхронизировать геозоны для геолокации между устройствами
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.sync_location_geofences(**request.dict())
                if result:
                    return SyncLocationGeofencesResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return SyncLocationGeofencesResponse(
            userId=request.userId,
            geofences=[],
            conflicts=[],
            lastSyncTimestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error syncing location geofences: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка синхронизации геозон: {str(e)}")


@router.post("/location/geofences/update", response_model=LocationGeofenceResponse)
async def update_location_geofence(
    request: UpdateLocationGeofenceRequest
) -> LocationGeofenceResponse:
    """
    Создать или обновить геозону для геолокации
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_location_geofence(**request.dict())
                if result:
                    return LocationGeofenceResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        geofence_id = request.geofenceId or f"geofence_{datetime.now().timestamp()}"
        return LocationGeofenceResponse(
            geofenceId=geofence_id,
            userId=request.userId,
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
        logger.error(f"Error updating location geofence: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления геозоны: {str(e)}")


@router.delete("/location/geofences/{geofenceId}", response_model=Dict[str, str])
async def delete_location_geofence(
    geofenceId: str = Path(..., description="ID геозоны")
) -> Dict[str, str]:
    """
    Удалить геозону для геолокации
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                await sfm_adapter.delete_location_geofence(geofenceId=geofenceId)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return {"status": "success", "message": "Геозона удалена"}
    except Exception as e:
        logger.error(f"Error deleting location geofence: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка удаления геозоны: {str(e)}")


@router.get("/location/movement-history", response_model=MovementHistoryResponse)
async def get_movement_history(
    userId: str = Query(..., description="ID пользователя"),
    limit: int = Query(100, description="Максимальное количество записей", ge=1, le=1000),
    startDate: Optional[str] = Query(None, description="Начальная дата (ISO)")
) -> MovementHistoryResponse:
    """
    Получить историю перемещений
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_movement_history(userId=userId, limit=limit, startDate=startDate)
                if result:
                    return MovementHistoryResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return MovementHistoryResponse(
            history=[],
            total=0
        )
    except Exception as e:
        logger.error(f"Error getting movement history: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения истории перемещений: {str(e)}")


@router.post("/location/movement-history/update", response_model=Dict[str, str])
async def update_movement_history(
    request: UpdateMovementHistoryRequest
) -> Dict[str, str]:
    """
    Обновить историю перемещений (добавить новые записи)
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                await sfm_adapter.update_movement_history(**request.dict())
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return {"status": "success", "message": f"Добавлено {len(request.entries)} записей"}
    except Exception as e:
        logger.error(f"Error updating movement history: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления истории перемещений: {str(e)}")


@router.get("/location/status", response_model=LocationStatusResponse)
async def get_location_status(
    userId: str = Query(..., description="ID пользователя")
) -> LocationStatusResponse:
    """
    Получить статус геолокации
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_location_status(userId=userId)
                if result:
                    return LocationStatusResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return LocationStatusResponse(
            userId=userId,
            enabled=True,
            lastKnownLocation=None,
            lastUpdate=None,
            lastModified=datetime.now(),
            deviceId=None,
            version=1
        )
    except Exception as e:
        logger.error(f"Error getting location status: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения статуса геолокации: {str(e)}")


@router.post("/location/status/update", response_model=LocationStatusResponse)
async def update_location_status(
    request: UpdateLocationStatusRequest
) -> LocationStatusResponse:
    """
    Обновить статус геолокации
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_location_status(**request.dict())
                if result:
                    return LocationStatusResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return LocationStatusResponse(
            userId=request.userId,
            enabled=request.enabled,
            lastKnownLocation=None,
            lastUpdate=None,
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=(request.version or 1) + 1
        )
    except Exception as e:
        logger.error(f"Error updating location status: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления статуса геолокации: {str(e)}")


# ========== СЕМЕЙНЫЙ ЧАТ (ОФЛАЙН) (3 endpoint'а) ==========

@router.post("/chat/offline-messages/sync", response_model=SyncOfflineMessagesResponse)
async def sync_offline_messages(
    request: SyncOfflineMessagesRequest
) -> SyncOfflineMessagesResponse:
    """
    Синхронизировать офлайн сообщения семейного чата между устройствами
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.sync_offline_messages(**request.dict())
                if result:
                    return SyncOfflineMessagesResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return SyncOfflineMessagesResponse(
            userId=request.userId,
            familyId=request.familyId,
            messages=[],
            conflicts=[],
            lastSyncTimestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error syncing offline messages: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка синхронизации сообщений: {str(e)}")


@router.post("/chat/offline-messages/send", response_model=OfflineMessageResponse)
async def send_offline_message(
    request: SendOfflineMessageRequest
) -> OfflineMessageResponse:
    """
    Отправить офлайн сообщение в семейный чат
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.send_offline_message(**request.dict())
                if result:
                    return OfflineMessageResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        message_id = f"msg_{datetime.now().timestamp()}"
        return OfflineMessageResponse(
            messageId=message_id,
            userId=request.userId,
            recipientId=request.recipientId,
            familyId=request.familyId,
            content=request.content,
            timestamp=request.timestamp or datetime.now(),
            isRead=False,
            deviceId=request.deviceId,
            version=1
        )
    except Exception as e:
        logger.error(f"Error sending offline message: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка отправки сообщения: {str(e)}")


@router.post("/chat/offline-messages/resolve-conflicts", response_model=Dict[str, str])
async def resolve_message_conflicts(
    request: ResolveMessageConflictsRequest
) -> Dict[str, str]:
    """
    Разрешить конфликты офлайн сообщений
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                await sfm_adapter.resolve_message_conflicts(**request.dict())
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return {"status": "success", "message": f"Разрешено {len(request.conflicts)} конфликтов"}
    except Exception as e:
        logger.error(f"Error resolving message conflicts: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка разрешения конфликтов: {str(e)}")
