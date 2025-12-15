#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚗 Crash Detection Router
FastAPI router для Crash Detection Agent

API endpoints:
- POST /start - Запуск мониторинга
- POST /stop - Остановка мониторинга
- GET /status - Статус мониторинга
- POST /data - Отправка данных сенсоров
- POST /emergency-call - Ручной вызов экстренной службы
- POST /cancel-emergency-call - Отмена вызова
- GET /history - История аварий
- GET /health - Health check

Дата создания: 12 декабря 2025
Версия: 1.0.0
"""

import logging
import os
from typing import Optional, Dict

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field, validator

# Импорты агента
try:
    from security.ai_agents.crash_detection_agent import (
        CrashDetectionAgent,
        CrashSeverity,
        AccelerometerData,
        GyroscopeData,
        CrashEvent
    )
except ImportError:
    CrashDetectionAgent = None
    CrashSeverity = None
    AccelerometerData = None
    GyroscopeData = None
    CrashEvent = None

logger = logging.getLogger(__name__)

# Создаем FastAPI Router
router = APIRouter(prefix="/api/crash-detection", tags=["Crash Detection"])

# Глобальный экземпляр агента (инициализируется при первом запросе)
_agent_instance: Optional[CrashDetectionAgent] = None


def get_agent() -> CrashDetectionAgent:
    """
    Получение экземпляра агента (singleton)

    Returns:
        Экземпляр CrashDetectionAgent

    Raises:
        HTTPException: Если агент не может быть инициализирован
    """
    global _agent_instance

    if _agent_instance is None:
        if CrashDetectionAgent is None:
            raise HTTPException(
                status_code=503,
                detail="Crash Detection Agent не доступен. Проверьте установку модуля."
            )

        config = {
            "g_force_threshold": float(os.getenv("CRASH_G_FORCE_THRESHOLD", "3.0")),
            "speed_change_threshold": float(os.getenv("CRASH_SPEED_CHANGE_THRESHOLD", "30.0")),
            "emergency_service_number": os.getenv("CRASH_EMERGENCY_NUMBER", "112"),
            "auto_call_enabled": os.getenv("CRASH_AUTO_CALL_ENABLED", "true").lower() == "true",
            "false_positive_filter": os.getenv("CRASH_FALSE_POSITIVE_FILTER", "true").lower() == "true",
            "use_geofence": os.getenv("CRASH_USE_GEOFENCE", "true").lower() == "true",
            "geofence_radius": int(os.getenv("CRASH_GEOFENCE_RADIUS", "500")),
            "prefer_gps": os.getenv("CRASH_PREFER_GPS", "true").lower() == "true",
        }

        try:
            _agent_instance = CrashDetectionAgent(config)
            logger.info("✅ Crash Detection Agent инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Crash Detection Agent: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка инициализации агента: {str(e)}"
            )

    return _agent_instance


# MARK: - Pydantic Models

class StartMonitoringRequest(BaseModel):
    """Запрос на запуск мониторинга"""
    user_id: str = Field(..., description="ID пользователя", example="user123")


class StopMonitoringRequest(BaseModel):
    """Запрос на остановку мониторинга"""
    user_id: str = Field(..., description="ID пользователя", example="user123")


class SensorDataRequest(BaseModel):
    """Запрос с данными сенсоров"""
    user_id: str = Field(..., description="ID пользователя", example="user123")
    accelerometer: Dict[str, float] = Field(
        ...,
        description="Данные акселерометра",
        example={"x": 0.5, "y": 0.3, "z": 9.8, "timestamp": 1234567890.123}
    )
    gyroscope: Optional[Dict[str, float]] = Field(
        None,
        description="Данные гироскопа (опционально)",
        example={"x": 0.1, "y": 0.2, "z": 0.05, "timestamp": 1234567890.123}
    )
    speed: Optional[float] = Field(
        None,
        description="Скорость из GPS/ГЛОНАСС (км/ч, опционально)",
        example=60.0
    )
    location: Optional[Dict[str, float]] = Field(
        None,
        description="Местоположение из GPS/ГЛОНАСС (опционально)",
        example={"latitude": 55.7558, "longitude": 37.6173}
    )
    geofence_center: Optional[Dict[str, float]] = Field(
        None,
        description="Центр геозоны (если используется геозона)",
        example={"latitude": 55.7558, "longitude": 37.6173}
    )

    @validator('accelerometer')
    def validate_accelerometer(cls, v):
        if not all(key in v for key in ['x', 'y', 'z']):
            raise ValueError('Акселерометр должен содержать x, y, z')
        return v

    @validator('gyroscope')
    def validate_gyroscope(cls, v):
        if v is not None and not all(key in v for key in ['x', 'y', 'z']):
            raise ValueError('Гироскоп должен содержать x, y, z')
        return v


class EmergencyCallRequest(BaseModel):
    """Запрос на вызов экстренной службы"""
    user_id: str = Field(..., description="ID пользователя", example="user123")
    location: Optional[Dict[str, float]] = Field(
        None,
        description="Местоположение (если не указано, используется из последней аварии)",
        example={"latitude": 55.7558, "longitude": 37.6173}
    )


class CancelEmergencyCallRequest(BaseModel):
    """Запрос на отмену вызова экстренной службы"""
    user_id: str = Field(..., description="ID пользователя", example="user123")
    call_id: str = Field(..., description="ID вызова", example="emergency_user123_1234567890")


# MARK: - API Endpoints

@router.post("/start", summary="Запуск мониторинга аварий")
async def start_monitoring(request: StartMonitoringRequest, agent: CrashDetectionAgent = Depends(get_agent)):
    """
    Запустить мониторинг аварий для пользователя

    Args:
        request: Запрос с ID пользователя

    Returns:
        Результат запуска мониторинга
    """
    try:
        result = agent.start_monitoring(request.user_id)
        if result:
            return {
                "status": "success",
                "message": f"Мониторинг запущен для пользователя {request.user_id}",
                "user_id": request.user_id
            }
        else:
            raise HTTPException(status_code=400, detail="Не удалось запустить мониторинг")
    except Exception as e:
        logger.error(f"Ошибка запуска мониторинга: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop", summary="Остановка мониторинга аварий")
async def stop_monitoring(request: StopMonitoringRequest, agent: CrashDetectionAgent = Depends(get_agent)):
    """
    Остановить мониторинг аварий для пользователя

    Args:
        request: Запрос с ID пользователя

    Returns:
        Результат остановки мониторинга
    """
    try:
        result = agent.stop_monitoring(request.user_id)
        if result:
            return {
                "status": "success",
                "message": f"Мониторинг остановлен для пользователя {request.user_id}",
                "user_id": request.user_id
            }
        else:
            raise HTTPException(status_code=404, detail="Мониторинг не был запущен для этого пользователя")
    except Exception as e:
        logger.error(f"Ошибка остановки мониторинга: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data", summary="Отправка данных сенсоров")
async def process_sensor_data(request: SensorDataRequest, agent: CrashDetectionAgent = Depends(get_agent)):
    """
    Обработать данные сенсоров и обнаружить аварию (если есть)

    Args:
        request: Запрос с данными акселерометра, гироскопа, скорости и местоположения

    Returns:
        Результат обработки с информацией об обнаруженной аварии (если есть)
    """
    try:
        result = agent.process_sensor_data(
            user_id=request.user_id,
            accelerometer_data=request.accelerometer,
            gyroscope_data=request.gyroscope,
            speed=request.speed,
            location=request.location,
            geofence_center=request.geofence_center
        )

        return result
    except Exception as e:
        logger.error(f"Ошибка обработки данных сенсоров: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", summary="Статус мониторинга")
async def get_status(
    user_id: str = Query(..., description="ID пользователя", example="user123"),
    agent: CrashDetectionAgent = Depends(get_agent)
):
    """
    Получить статус мониторинга для пользователя

    Args:
        user_id: ID пользователя

    Returns:
        Статус мониторинга
    """
    try:
        status = agent.get_status(user_id)
        return status
    except Exception as e:
        logger.error(f"Ошибка получения статуса: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/emergency-call", summary="Ручной вызов экстренной службы")
async def call_emergency(request: EmergencyCallRequest, agent: CrashDetectionAgent = Depends(get_agent)):
    """
    Вызвать экстренную службу вручную

    Args:
        request: Запрос с ID пользователя и местоположением

    Returns:
        Результат вызова
    """
    try:
        # Получаем последнюю аварию пользователя
        history = agent.get_crash_history(request.user_id, limit=1)
        if not history:
            raise HTTPException(
                status_code=404,
                detail="Не найдено событий аварии для этого пользователя"
            )

        last_crash = history[0]
        crash_event = CrashEvent(
            event_id=last_crash.get("event_id", f"manual_call_{request.user_id}_{int(__import__('time').time())}"),
            user_id=request.user_id,
            timestamp=last_crash.get("timestamp", __import__('datetime').datetime.now().isoformat()),
            severity=CrashSeverity(last_crash.get("severity", "high")),
            g_force=last_crash.get("g_force", 0.0),
            location=request.location or last_crash.get("location"),
            speed_before=last_crash.get("speed_before"),
            emergency_called=False
        )

        result = agent._call_emergency_service(crash_event)

        if result:
            return {
                "status": "success",
                "message": "Экстренная служба вызвана",
                "call_id": crash_event.emergency_call_id,
                "emergency_number": agent.emergency_service_number
            }
        else:
            raise HTTPException(status_code=500, detail="Не удалось вызвать экстренную службу")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка вызова экстренной службы: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancel-emergency-call", summary="Отмена вызова экстренной службы")
async def cancel_emergency_call(request: CancelEmergencyCallRequest, agent: CrashDetectionAgent = Depends(get_agent)):
    """
    Отменить вызов экстренной службы

    Args:
        request: Запрос с ID пользователя и ID вызова

    Returns:
        Результат отмены
    """
    try:
        result = agent.cancel_emergency_call(request.user_id, request.call_id)
        if result:
            return {
                "status": "success",
                "message": "Вызов экстренной службы отменен",
                "call_id": request.call_id
            }
        else:
            raise HTTPException(status_code=404, detail="Вызов не найден")
    except Exception as e:
        logger.error(f"Ошибка отмены вызова: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", summary="История аварий")
async def get_crash_history(
    user_id: str = Query(..., description="ID пользователя", example="user123"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество записей"),
    agent: CrashDetectionAgent = Depends(get_agent)
):
    """
    Получить историю аварий для пользователя

    Args:
        user_id: ID пользователя
        limit: Максимальное количество записей (1-100)

    Returns:
        История аварий
    """
    try:
        history = agent.get_crash_history(user_id, limit=limit)
        return {
            "status": "success",
            "user_id": user_id,
            "count": len(history),
            "crashes": history
        }
    except Exception as e:
        logger.error(f"Ошибка получения истории: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", summary="Health check")
async def health_check(agent: CrashDetectionAgent = Depends(get_agent)):
    """
    Health check endpoint

    Returns:
        Статус работы агента
    """
    try:
        return {
            "status": "healthy",
            "agent": "crash_detection_agent",
            "version": "1.0.0",
            "emergency_service": agent.emergency_service_number,
            "auto_call_enabled": agent.auto_call_enabled,
            "g_force_threshold": agent.g_force_threshold,
            "prefer_gps": agent.prefer_gps,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Ошибка health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))
