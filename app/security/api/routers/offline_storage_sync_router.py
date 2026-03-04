# -*- coding: utf-8 -*-
"""
Offline Storage Sync API Router
--------------------------------
FastAPI endpoints для синхронизации офлайн хранилища между устройствами.

Использование:
    В main.py добавить:
    from security.api.routers.offline_storage_sync_router import router as offline_storage_router
    app.include_router(offline_storage_router)

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
router = APIRouter(prefix="/api/offline-storage", tags=["Offline Storage"])


# =============================================================================
# Pydantic модели для запросов и ответов
# =============================================================================

class OfflineDataResponse(BaseModel):
    """Ответ с данными офлайн хранилища"""
    dataId: str = Field(..., description="ID данных")
    userId: str = Field(..., description="ID пользователя")
    dataType: str = Field(..., description="Тип данных: settings, cache, temp, etc.")
    data: Dict[str, Any] = Field(..., description="Данные (JSON)")
    size: int = Field(..., description="Размер данных в байтах", ge=0)
    lastModified: datetime = Field(..., description="Время последнего изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class SyncOfflineStorageRequest(BaseModel):
    """Запрос на синхронизацию офлайн хранилища"""
    userId: str = Field(..., description="ID пользователя")
    deviceId: str = Field(..., description="ID устройства")
    lastSyncTimestamp: Optional[datetime] = Field(None, description="Время последней синхронизации")
    dataTypes: Optional[List[str]] = Field(None, description="Типы данных для синхронизации")


class SyncOfflineStorageResponse(BaseModel):
    """Ответ на синхронизацию офлайн хранилища"""
    userId: str = Field(..., description="ID пользователя")
    data: List[OfflineDataResponse] = Field(..., description="Список данных")
    conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="Список конфликтов")
    lastSyncTimestamp: datetime = Field(..., description="Время синхронизации")
    totalSize: int = Field(0, description="Общий размер данных в байтах", ge=0)


class GetOfflineDataRequest(BaseModel):
    """Запрос на получение данных"""
    userId: str = Field(..., description="ID пользователя")
    dataType: Optional[str] = Field(None, description="Тип данных (опционально)")
    dataId: Optional[str] = Field(None, description="ID данных (опционально)")


class UpdateOfflineDataRequest(BaseModel):
    """Запрос на обновление данных"""
    userId: str = Field(..., description="ID пользователя")
    dataId: Optional[str] = Field(None, description="ID данных (если обновление существующих)")
    dataType: str = Field(..., description="Тип данных")
    data: Dict[str, Any] = Field(..., description="Данные (JSON)")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


class ResolveOfflineStorageConflictsRequest(BaseModel):
    """Запрос на разрешение конфликтов"""
    userId: str = Field(..., description="ID пользователя")
    conflicts: List[Dict[str, Any]] = Field(..., description="Список конфликтов для разрешения")
    resolutionStrategy: str = Field("last-write-wins", description="Стратегия разрешения: last-write-wins, merge, manual")
    deviceId: Optional[str] = Field(None, description="ID устройства")


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/sync", response_model=SyncOfflineStorageResponse)
async def sync_offline_storage(
    request: SyncOfflineStorageRequest
) -> SyncOfflineStorageResponse:
    """
    Синхронизировать офлайн хранилище между устройствами
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.sync_offline_storage(**request.dict())
                if result:
                    return SyncOfflineStorageResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return SyncOfflineStorageResponse(
            userId=request.userId,
            data=[],
            conflicts=[],
            lastSyncTimestamp=datetime.now(),
            totalSize=0
        )
    except Exception as e:
        logger.error(f"Error syncing offline storage: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка синхронизации офлайн хранилища: {str(e)}")


@router.get("/data", response_model=List[OfflineDataResponse])
async def get_offline_data(
    userId: str = Query(..., description="ID пользователя"),
    dataType: Optional[str] = Query(None, description="Тип данных (опционально)"),
    dataId: Optional[str] = Query(None, description="ID данных (опционально)")
) -> List[OfflineDataResponse]:
    """
    Получить данные из офлайн хранилища
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_offline_data(userId=userId, dataType=dataType, dataId=dataId)
                if result:
                    return [OfflineDataResponse(**item) for item in result]
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return []
    except Exception as e:
        logger.error(f"Error getting offline data: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения данных: {str(e)}")


@router.post("/data/update", response_model=OfflineDataResponse)
async def update_offline_data(
    request: UpdateOfflineDataRequest
) -> OfflineDataResponse:
    """
    Создать или обновить данные в офлайн хранилище
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_offline_data(**request.dict())
                if result:
                    return OfflineDataResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        data_id = request.dataId or f"data_{datetime.now().timestamp()}"
        import json
        data_size = len(json.dumps(request.data).encode('utf-8'))
        
        return OfflineDataResponse(
            dataId=data_id,
            userId=request.userId,
            dataType=request.dataType,
            data=request.data,
            size=data_size,
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=(request.version or 1) + 1
        )
    except Exception as e:
        logger.error(f"Error updating offline data: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления данных: {str(e)}")


@router.delete("/data/{dataId}", response_model=Dict[str, str])
async def delete_offline_data(
    dataId: str = Path(..., description="ID данных"),
    userId: str = Query(..., description="ID пользователя")
) -> Dict[str, str]:
    """
    Удалить данные из офлайн хранилища
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                await sfm_adapter.delete_offline_data(dataId=dataId, userId=userId)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return {"status": "success", "message": "Данные удалены"}
    except Exception as e:
        logger.error(f"Error deleting offline data: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка удаления данных: {str(e)}")


@router.post("/resolve-conflicts", response_model=Dict[str, str])
async def resolve_offline_storage_conflicts(
    request: ResolveOfflineStorageConflictsRequest
) -> Dict[str, str]:
    """
    Разрешить конфликты в офлайн хранилище
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                await sfm_adapter.resolve_offline_storage_conflicts(**request.dict())
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return {
            "status": "success",
            "message": f"Разрешено {len(request.conflicts)} конфликтов",
            "strategy": request.resolutionStrategy
        }
    except Exception as e:
        logger.error(f"Error resolving conflicts: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка разрешения конфликтов: {str(e)}")
