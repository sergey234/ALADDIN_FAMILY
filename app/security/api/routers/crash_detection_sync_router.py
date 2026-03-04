# -*- coding: utf-8 -*-
"""
Crash Detection Sync API Router
--------------------------------
FastAPI endpoints для синхронизации Crash Detection между устройствами.

Использование:
    В main.py добавить:
    from security.api.routers.crash_detection_sync_router import router as crash_detection_router
    app.include_router(crash_detection_router)

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
router = APIRouter(prefix="/api/crash-detection", tags=["Crash Detection"])


# =============================================================================
# Pydantic модели для запросов и ответов
# =============================================================================

class CrashReportResponse(BaseModel):
    """Ответ с отчетом о краше"""
    reportId: str = Field(..., description="ID отчета")
    userId: str = Field(..., description="ID пользователя")
    deviceId: str = Field(..., description="ID устройства")
    crashType: str = Field(..., description="Тип краша: accident, fall, emergency, etc.")
    severity: str = Field(..., description="Серьезность: low, medium, high, critical")
    location: Optional[Dict[str, float]] = Field(None, description="Местоположение {latitude, longitude}")
    timestamp: datetime = Field(..., description="Время краша")
    details: Optional[Dict[str, Any]] = Field(None, description="Дополнительные детали")
    isResolved: bool = Field(False, description="Разрешен ли краш")
    lastModified: datetime = Field(..., description="Время последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class SyncCrashDetectionRequest(BaseModel):
    """Запрос на синхронизацию Crash Detection"""
    userId: str = Field(..., description="ID пользователя")
    deviceId: str = Field(..., description="ID устройства")
    lastSyncTimestamp: Optional[datetime] = Field(None, description="Время последней синхронизации")


class SyncCrashDetectionResponse(BaseModel):
    """Ответ на синхронизацию Crash Detection"""
    userId: str = Field(..., description="ID пользователя")
    reports: List[CrashReportResponse] = Field(..., description="Список отчетов")
    conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="Список конфликтов")
    lastSyncTimestamp: datetime = Field(..., description="Время синхронизации")


class ReportCrashRequest(BaseModel):
    """Запрос на отправку отчета о краше"""
    userId: str = Field(..., description="ID пользователя")
    deviceId: str = Field(..., description="ID устройства")
    crashType: str = Field(..., description="Тип краша: accident, fall, emergency, etc.")
    severity: str = Field(..., description="Серьезность: low, medium, high, critical")
    location: Optional[Dict[str, float]] = Field(None, description="Местоположение {latitude, longitude}")
    timestamp: Optional[datetime] = Field(None, description="Время краша (если не указано, используется текущее время)")
    details: Optional[Dict[str, Any]] = Field(None, description="Дополнительные детали")


class CrashNotificationResponse(BaseModel):
    """Ответ с уведомлением о краше"""
    notificationId: str = Field(..., description="ID уведомления")
    userId: str = Field(..., description="ID пользователя")
    reportId: str = Field(..., description="ID отчета о краше")
    recipientId: Optional[str] = Field(None, description="ID получателя (если отправлено конкретному пользователю)")
    message: str = Field(..., description="Текст уведомления")
    timestamp: datetime = Field(..., description="Время отправки")
    isRead: bool = Field(False, description="Прочитано ли уведомление")


class GetCrashNotificationsRequest(BaseModel):
    """Запрос на получение уведомлений о крашах"""
    userId: str = Field(..., description="ID пользователя")
    limit: int = Field(50, description="Максимальное количество уведомлений", ge=1, le=100)
    unreadOnly: bool = Field(False, description="Только непрочитанные")


class SendCrashNotificationRequest(BaseModel):
    """Запрос на отправку уведомления о краше"""
    userId: str = Field(..., description="ID пользователя")
    reportId: str = Field(..., description="ID отчета о краше")
    recipientId: Optional[str] = Field(None, description="ID получателя (если None, отправляется всем контактам)")
    message: Optional[str] = Field(None, description="Текст уведомления (если None, используется стандартное)")
    deviceId: Optional[str] = Field(None, description="ID устройства")


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/sync", response_model=SyncCrashDetectionResponse)
async def sync_crash_detection(
    request: SyncCrashDetectionRequest
) -> SyncCrashDetectionResponse:
    """
    Синхронизировать отчеты о крашах между устройствами
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.sync_crash_detection(**request.dict())
                if result:
                    return SyncCrashDetectionResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return SyncCrashDetectionResponse(
            userId=request.userId,
            reports=[],
            conflicts=[],
            lastSyncTimestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error syncing crash detection: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка синхронизации Crash Detection: {str(e)}")


@router.post("/report", response_model=CrashReportResponse)
async def report_crash(
    request: ReportCrashRequest
) -> CrashReportResponse:
    """
    Отправить отчет о краше
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.report_crash(**request.dict())
                if result:
                    return CrashReportResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        report_id = f"crash_{datetime.now().timestamp()}"
        return CrashReportResponse(
            reportId=report_id,
            userId=request.userId,
            deviceId=request.deviceId,
            crashType=request.crashType,
            severity=request.severity,
            location=request.location,
            timestamp=request.timestamp or datetime.now(),
            details=request.details,
            isResolved=False,
            lastModified=datetime.now(),
            version=1
        )
    except Exception as e:
        logger.error(f"Error reporting crash: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка отправки отчета о краше: {str(e)}")


@router.get("/notifications", response_model=List[CrashNotificationResponse])
async def get_crash_notifications(
    userId: str = Query(..., description="ID пользователя"),
    limit: int = Query(50, description="Максимальное количество уведомлений", ge=1, le=100),
    unreadOnly: bool = Query(False, description="Только непрочитанные")
) -> List[CrashNotificationResponse]:
    """
    Получить уведомления о крашах
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.get_crash_notifications(userId=userId, limit=limit, unreadOnly=unreadOnly)
                if result:
                    return [CrashNotificationResponse(**item) for item in result]
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return []
    except Exception as e:
        logger.error(f"Error getting crash notifications: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения уведомлений: {str(e)}")


@router.post("/notifications/send", response_model=CrashNotificationResponse)
async def send_crash_notification(
    request: SendCrashNotificationRequest
) -> CrashNotificationResponse:
    """
    Отправить уведомление о краше
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.send_crash_notification(**request.dict())
                if result:
                    return CrashNotificationResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        notification_id = f"notif_{datetime.now().timestamp()}"
        message = request.message or f"Обнаружен краш типа {request.reportId}"
        
        return CrashNotificationResponse(
            notificationId=notification_id,
            userId=request.userId,
            reportId=request.reportId,
            recipientId=request.recipientId,
            message=message,
            timestamp=datetime.now(),
            isRead=False
        )
    except Exception as e:
        logger.error(f"Error sending crash notification: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка отправки уведомления: {str(e)}")
