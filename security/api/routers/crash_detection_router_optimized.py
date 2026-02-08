#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚗 Crash Detection Router - ОПТИМИЗИРОВАННАЯ ВЕРСИЯ
FastAPI router для Crash Detection Agent с оптимизацией производительности

Оптимизации:
- Redis кэширование для статусных эндпоинтов
- Оптимизированная работа с сессиями
- Connection pooling
- Минимизация вызовов datetime.utcnow()
- Декораторы кэширования

Дата создания: 6 февраля 2026
Версия: 2.0.0 (Optimized)
"""

import logging
import os
from typing import Optional, Dict, Set
from datetime import datetime

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

# Импорт модуля кэширования
try:
    from security.api.cache.crash_detection_cache import (
        cache_result,
        get_cached,
        set_cached,
        invalidate_cache,
        get_cache_key
    )
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    logger.warning("Модуль кэширования недоступен")

logger = logging.getLogger(__name__)

# Создаем FastAPI Router
router = APIRouter(prefix="/api/crash-detection", tags=["Crash Detection"])

# Глобальный экземпляр агента (инициализируется при первом запросе)
_agent_instance: Optional[CrashDetectionAgent] = None

# ОПТИМИЗИРОВАННАЯ СТРУКТУРА ДАННЫХ ДЛЯ СЕССИЙ
# Используем отдельные множества для быстрого поиска
_crash_detection_sessions: Dict[str, Dict] = {}
_active_session_ids: Set[str] = set()
_inactive_session_ids: Set[str] = set()

# Кэшированные счетчики (обновляются при изменении)
_cached_active_count: Optional[int] = None
_cached_total_count: Optional[int] = None
_cache_timestamp: Optional[float] = None
CACHE_COUNTERS_TTL = 1.0  # секунды


def get_agent() -> CrashDetectionAgent:
    """
    Получение экземпляра агента (singleton)
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


def get_cached_session_counters():
    """Получение кэшированных счетчиков сессий"""
    import time
    
    global _cached_active_count, _cached_total_count, _cache_timestamp
    
    current_time = time.time()
    
    # Проверяем актуальность кэша
    if (_cached_active_count is not None and 
        _cached_total_count is not None and 
        _cache_timestamp is not None and
        current_time - _cache_timestamp < CACHE_COUNTERS_TTL):
        return _cached_active_count, _cached_total_count
    
    # Пересчитываем счетчики
    _cached_active_count = len(_active_session_ids)
    _cached_total_count = len(_crash_detection_sessions)
    _cache_timestamp = current_time
    
    return _cached_active_count, _cached_total_count


def invalidate_session_counters():
    """Инвалидация кэшированных счетчиков"""
    global _cached_active_count, _cached_total_count, _cache_timestamp
    _cached_active_count = None
    _cached_total_count = None
    _cache_timestamp = None


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


# MARK: - API Endpoints (ОПТИМИЗИРОВАННЫЕ)

@router.post("/start", summary="Запуск мониторинга аварий")
async def start_monitoring(request: StartMonitoringRequest, agent: CrashDetectionAgent = Depends(get_agent)):
    """
    Запустить мониторинг аварий для пользователя (ОПТИМИЗИРОВАНО)
    """
    try:
        # Инвалидируем кэш при изменении состояния
        invalidate_cache("crash_detection:status:*")
        invalidate_session_counters()
        
        result = agent.start_monitoring(request.user_id)
        if result:
            # Используем один timestamp для всего ответа
            timestamp = datetime.utcnow().isoformat()
            
            return {
                "status": "success",
                "source": "real_sfm",
                "function": "start_crash_detection_monitoring",
                "message": f"Мониторинг запущен для пользователя {request.user_id}",
                "user_id": request.user_id,
                "timestamp": timestamp
            }
        else:
            raise HTTPException(status_code=400, detail="Не удалось запустить мониторинг")
    except Exception as e:
        logger.error(f"Ошибка запуска мониторинга: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop", summary="Остановка мониторинга аварий")
async def stop_monitoring(request: StopMonitoringRequest, agent: CrashDetectionAgent = Depends(get_agent)):
    """
    Остановить мониторинг аварий для пользователя (ОПТИМИЗИРОВАНО)
    """
    try:
        # Инвалидируем кэш при изменении состояния
        invalidate_cache("crash_detection:status:*")
        invalidate_session_counters()
        
        result = agent.stop_monitoring(request.user_id)
        if result:
            timestamp = datetime.utcnow().isoformat()
            
            return {
                "status": "success",
                "source": "real_sfm",
                "function": "stop_crash_detection_monitoring",
                "message": f"Мониторинг остановлен для пользователя {request.user_id}",
                "user_id": request.user_id,
                "timestamp": timestamp
            }
        else:
            raise HTTPException(status_code=404, detail="Мониторинг не был запущен для этого пользователя")
    except Exception as e:
        logger.error(f"Ошибка остановки мониторинга: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data", summary="Отправка данных сенсоров")
async def process_sensor_data(request: SensorDataRequest, agent: CrashDetectionAgent = Depends(get_agent)):
    """
    Обработать данные сенсоров и обнаружить аварию (если есть) (ОПТИМИЗИРОВАНО)
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
        
        # Добавляем SFM метаданные если их нет
        if "source" not in result:
            result["source"] = "real_sfm"
            result["function"] = "send_crash_detection_data"
            result["timestamp"] = datetime.utcnow().isoformat()

        return result
    except Exception as e:
        logger.error(f"Ошибка обработки данных сенсоров: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", summary="Статус мониторинга")
@cache_result(ttl=2, key_prefix="status")  # КЭШИРОВАНИЕ НА 2 СЕКУНДЫ
async def get_status(
    user_id: str = Query(..., description="ID пользователя", example="user123"),
    agent: CrashDetectionAgent = Depends(get_agent)
):
    """
    Получить статус мониторинга для пользователя (ОПТИМИЗИРОВАНО С КЭШИРОВАНИЕМ)
    """
    try:
        # Используем кэшированные счетчики
        active_sessions, total_sessions = get_cached_session_counters()
        
        # Получаем статус от агента
        status = agent.get_status(user_id)
        
        # Добавляем SFM метаданные
        timestamp = datetime.utcnow().isoformat()
        
        result = {
            "status": "success",
            "source": "real_sfm",
            "function": "get_crash_detection_status",
            "active_sessions": active_sessions,
            "total_sessions": total_sessions,
            "is_monitoring": active_sessions > 0,
            "timestamp": timestamp,
            **status
        }
        
        return result
    except Exception as e:
        logger.error(f"Ошибка получения статуса: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/emergency-call", summary="Ручной вызов экстренной службы")
async def call_emergency(request: EmergencyCallRequest, agent: CrashDetectionAgent = Depends(get_agent)):
    """
    Вызвать экстренную службу вручную (ОПТИМИЗИРОВАНО)
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
        import time as time_module
        
        crash_event = CrashEvent(
            event_id=last_crash.get("event_id", f"manual_call_{request.user_id}_{int(time_module.time())}"),
            user_id=request.user_id,
            timestamp=last_crash.get("timestamp", datetime.utcnow().isoformat()),
            severity=CrashSeverity(last_crash.get("severity", "high")),
            g_force=last_crash.get("g_force", 0.0),
            location=request.location or last_crash.get("location"),
            speed_before=last_crash.get("speed_before"),
            emergency_called=False
        )

        result = agent._call_emergency_service(crash_event)
        timestamp = datetime.utcnow().isoformat()

        if result:
            return {
                "status": "success",
                "source": "real_sfm",
                "function": "call_emergency_service",
                "message": "Экстренная служба вызвана",
                "call_id": crash_event.emergency_call_id,
                "emergency_number": agent.emergency_service_number,
                "timestamp": timestamp
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
    Отменить вызов экстренной службы (ОПТИМИЗИРОВАНО)
    """
    try:
        result = agent.cancel_emergency_call(request.user_id, request.call_id)
        timestamp = datetime.utcnow().isoformat()
        
        if result:
            return {
                "status": "success",
                "source": "real_sfm",
                "function": "cancel_emergency_call",
                "message": "Вызов экстренной службы отменен",
                "call_id": request.call_id,
                "timestamp": timestamp
            }
        else:
            raise HTTPException(status_code=404, detail="Вызов не найден")
    except Exception as e:
        logger.error(f"Ошибка отмены вызова: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", summary="История аварий")
@cache_result(ttl=5, key_prefix="history")  # КЭШИРОВАНИЕ НА 5 СЕКУНД
async def get_crash_history(
    user_id: str = Query(..., description="ID пользователя", example="user123"),
    limit: int = Query(10, ge=1, le=100, description="Максимальное количество записей"),
    agent: CrashDetectionAgent = Depends(get_agent)
):
    """
    Получить историю аварий для пользователя (ОПТИМИЗИРОВАНО С КЭШИРОВАНИЕМ)
    """
    try:
        history = agent.get_crash_history(user_id, limit=limit)
        timestamp = datetime.utcnow().isoformat()
        
        return {
            "status": "success",
            "source": "real_sfm",
            "function": "get_crash_history",
            "user_id": user_id,
            "count": len(history),
            "crashes": history,
            "timestamp": timestamp
        }
    except Exception as e:
        logger.error(f"Ошибка получения истории: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", summary="Health check")
@cache_result(ttl=5, key_prefix="health")  # КЭШИРОВАНИЕ НА 5 СЕКУНД
async def health_check(agent: CrashDetectionAgent = Depends(get_agent)):
    """
    Health check endpoint (ОПТИМИЗИРОВАНО С КЭШИРОВАНИЕМ)
    """
    try:
        timestamp = datetime.utcnow().isoformat()
        
        return {
            "status": "healthy",
            "source": "real_sfm",
            "function": "crash_detection_health",
            "agent": "crash_detection_agent",
            "version": "2.0.0",
            "emergency_service": agent.emergency_service_number,
            "auto_call_enabled": agent.auto_call_enabled,
            "g_force_threshold": agent.g_force_threshold,
            "prefer_gps": agent.prefer_gps,
            "cache_enabled": CACHE_AVAILABLE,
            "timestamp": timestamp
        }
    except Exception as e:
        logger.error(f"Ошибка health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))
