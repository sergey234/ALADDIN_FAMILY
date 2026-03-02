# -*- coding: utf-8 -*-
"""
Elderly Interface Sync API Router
----------------------------------
FastAPI endpoints для синхронизации интерфейса для пожилых между устройствами.

Использование:
    В main.py добавить:
    from security.api.routers.elderly_interface_sync_router import router as elderly_interface_router
    app.include_router(elderly_interface_router)

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
router = APIRouter(prefix="/api/elderly", tags=["Elderly Interface"])


# =============================================================================
# Pydantic модели для запросов и ответов
# =============================================================================

class MedicationResponse(BaseModel):
    """Ответ с информацией о лекарстве"""
    medicationId: str = Field(..., description="ID лекарства")
    userId: str = Field(..., description="ID пользователя")
    name: str = Field(..., description="Название лекарства", max_length=200)
    dosage: str = Field(..., description="Дозировка", max_length=100)
    frequency: str = Field(..., description="Частота приема: daily, weekly, as_needed, etc.")
    timeOfDay: Optional[str] = Field(None, description="Время приема (HH:MM)")
    startDate: datetime = Field(..., description="Дата начала приема")
    endDate: Optional[datetime] = Field(None, description="Дата окончания приема")
    notes: Optional[str] = Field(None, description="Заметки", max_length=1000)
    lastModified: datetime = Field(..., description="Время последнего изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class SyncMedicationsRequest(BaseModel):
    """Запрос на синхронизацию лекарств"""
    userId: str = Field(..., description="ID пользователя")
    deviceId: str = Field(..., description="ID устройства")
    lastSyncTimestamp: Optional[datetime] = Field(None, description="Время последней синхронизации")


class SyncMedicationsResponse(BaseModel):
    """Ответ на синхронизацию лекарств"""
    userId: str = Field(..., description="ID пользователя")
    medications: List[MedicationResponse] = Field(..., description="Список лекарств")
    conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="Список конфликтов")
    lastSyncTimestamp: datetime = Field(..., description="Время синхронизации")


class UpdateMedicationRequest(BaseModel):
    """Запрос на обновление лекарства"""
    medicationId: Optional[str] = Field(None, description="ID лекарства (если обновление существующего)")
    userId: str = Field(..., description="ID пользователя")
    name: Optional[str] = Field(None, description="Название лекарства", max_length=200)
    dosage: Optional[str] = Field(None, description="Дозировка", max_length=100)
    frequency: Optional[str] = Field(None, description="Частота приема")
    timeOfDay: Optional[str] = Field(None, description="Время приема (HH:MM)")
    startDate: Optional[datetime] = Field(None, description="Дата начала приема")
    endDate: Optional[datetime] = Field(None, description="Дата окончания приема")
    notes: Optional[str] = Field(None, description="Заметки", max_length=1000)
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


class AppointmentResponse(BaseModel):
    """Ответ с информацией о встрече"""
    appointmentId: str = Field(..., description="ID встречи")
    userId: str = Field(..., description="ID пользователя")
    title: str = Field(..., description="Название встречи", max_length=200)
    description: Optional[str] = Field(None, description="Описание", max_length=1000)
    dateTime: datetime = Field(..., description="Дата и время встречи")
    location: Optional[str] = Field(None, description="Место встречи", max_length=500)
    contactName: Optional[str] = Field(None, description="Имя контакта", max_length=200)
    contactPhone: Optional[str] = Field(None, description="Телефон контакта", max_length=20)
    reminderMinutes: Optional[int] = Field(None, description="Напоминание за N минут до встречи", ge=0)
    isCompleted: bool = Field(False, description="Завершена ли встреча")
    lastModified: datetime = Field(..., description="Время последнего изменения")
    deviceId: Optional[str] = Field(None, description="ID устройства последнего изменения")
    version: int = Field(1, description="Версия для оптимистичной блокировки", ge=1)


class SyncAppointmentsRequest(BaseModel):
    """Запрос на синхронизацию встреч"""
    userId: str = Field(..., description="ID пользователя")
    deviceId: str = Field(..., description="ID устройства")
    lastSyncTimestamp: Optional[datetime] = Field(None, description="Время последней синхронизации")


class SyncAppointmentsResponse(BaseModel):
    """Ответ на синхронизацию встреч"""
    userId: str = Field(..., description="ID пользователя")
    appointments: List[AppointmentResponse] = Field(..., description="Список встреч")
    conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="Список конфликтов")
    lastSyncTimestamp: datetime = Field(..., description="Время синхронизации")


class UpdateAppointmentRequest(BaseModel):
    """Запрос на обновление встречи"""
    appointmentId: Optional[str] = Field(None, description="ID встречи (если обновление существующей)")
    userId: str = Field(..., description="ID пользователя")
    title: Optional[str] = Field(None, description="Название встречи", max_length=200)
    description: Optional[str] = Field(None, description="Описание", max_length=1000)
    dateTime: Optional[datetime] = Field(None, description="Дата и время встречи")
    location: Optional[str] = Field(None, description="Место встречи", max_length=500)
    contactName: Optional[str] = Field(None, description="Имя контакта", max_length=200)
    contactPhone: Optional[str] = Field(None, description="Телефон контакта", max_length=20)
    reminderMinutes: Optional[int] = Field(None, description="Напоминание за N минут", ge=0)
    isCompleted: Optional[bool] = Field(None, description="Завершена ли встреча")
    deviceId: Optional[str] = Field(None, description="ID устройства")
    version: Optional[int] = Field(None, description="Версия для оптимистичной блокировки", ge=1)


# =============================================================================
# API Endpoints
# =============================================================================

@router.post("/medications/sync", response_model=SyncMedicationsResponse)
async def sync_medications(
    request: SyncMedicationsRequest
) -> SyncMedicationsResponse:
    """
    Синхронизировать лекарства между устройствами
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.sync_medications(**request.dict())
                if result:
                    return SyncMedicationsResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return SyncMedicationsResponse(
            userId=request.userId,
            medications=[],
            conflicts=[],
            lastSyncTimestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error syncing medications: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка синхронизации лекарств: {str(e)}")


@router.post("/medications/update", response_model=MedicationResponse)
async def update_medication(
    request: UpdateMedicationRequest
) -> MedicationResponse:
    """
    Создать или обновить лекарство
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_medication(**request.dict())
                if result:
                    return MedicationResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        medication_id = request.medicationId or f"med_{datetime.now().timestamp()}"
        return MedicationResponse(
            medicationId=medication_id,
            userId=request.userId,
            name=request.name or "Лекарство",
            dosage=request.dosage or "1 таблетка",
            frequency=request.frequency or "daily",
            timeOfDay=request.timeOfDay,
            startDate=request.startDate or datetime.now(),
            endDate=request.endDate,
            notes=request.notes,
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=(request.version or 1) + 1
        )
    except Exception as e:
        logger.error(f"Error updating medication: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления лекарства: {str(e)}")


@router.post("/appointments/sync", response_model=SyncAppointmentsResponse)
async def sync_appointments(
    request: SyncAppointmentsRequest
) -> SyncAppointmentsResponse:
    """
    Синхронизировать встречи между устройствами
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.sync_appointments(**request.dict())
                if result:
                    return SyncAppointmentsResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        return SyncAppointmentsResponse(
            userId=request.userId,
            appointments=[],
            conflicts=[],
            lastSyncTimestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error syncing appointments: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка синхронизации встреч: {str(e)}")


@router.post("/appointments/update", response_model=AppointmentResponse)
async def update_appointment(
    request: UpdateAppointmentRequest
) -> AppointmentResponse:
    """
    Создать или обновить встречу
    """
    try:
        if SFM_ADAPTER_AVAILABLE and sfm_adapter:
            try:
                result = await sfm_adapter.update_appointment(**request.dict())
                if result:
                    return AppointmentResponse(**result)
            except Exception as e:
                logger.warning(f"SFM Adapter error: {e}, using fallback")
        
        # Fallback
        appointment_id = request.appointmentId or f"appt_{datetime.now().timestamp()}"
        return AppointmentResponse(
            appointmentId=appointment_id,
            userId=request.userId,
            title=request.title or "Встреча",
            description=request.description,
            dateTime=request.dateTime or datetime.now(),
            location=request.location,
            contactName=request.contactName,
            contactPhone=request.contactPhone,
            reminderMinutes=request.reminderMinutes,
            isCompleted=request.isCompleted if request.isCompleted is not None else False,
            lastModified=datetime.now(),
            deviceId=request.deviceId,
            version=(request.version or 1) + 1
        )
    except Exception as e:
        logger.error(f"Error updating appointment: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка обновления встречи: {str(e)}")
