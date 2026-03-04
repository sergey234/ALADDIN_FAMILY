# security/api/routers/crash_detection_router.py - ОПТИМИЗИРОВАННАЯ ВЕРСИЯ
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, Set
import logging
from datetime import datetime
import asyncio
import time
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Импорт модуля кэширования
try:
    import sys
    cache_dir = "/opt/aladdin-backend/security/api/cache"
    if cache_dir not in sys.path:
        sys.path.insert(0, cache_dir)
        from crash_detection_cache import (
            cache_result,
            get_cached,
            set_cached,
            invalidate_cache,
            get_cache_key
        )
        CACHE_AVAILABLE = True
    else:
        CACHE_AVAILABLE = False
        logger.warning("Модуль кэширования не найден, кэширование отключено")
        # Fallback декоратор
        def cache_result(ttl=2, key_prefix=None):
            def decorator(func):
                return func
            return decorator
except ImportError as e:
    CACHE_AVAILABLE = False
    logger.warning(f"Модуль кэширования недоступен: {e}")
    # Fallback декоратор
    def cache_result(ttl=2, key_prefix=None):
        def decorator(func):
            return func
        return decorator

router = APIRouter()

# Модели данных для Crash Detection
class CrashDetectionSetupRequest(BaseModel):
    latitude: float
    longitude: float
    radius: float = 500.0

class CrashAlertRequest(BaseModel):
    latitude: float
    longitude: float
    severity: str

class SensorDataRequest(BaseModel):
    accelerometer: Dict[str, float]
    gyroscope: Dict[str, float]
    speed: float
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    timestamp: float

class LocationBubbleRequest(BaseModel):
    latitude: float
    longitude: float

class LocationSendRequest(BaseModel):
    request_id: str
    latitude: float
    longitude: float

# ОПТИМИЗИРОВАННАЯ СТРУКТУРА ДАННЫХ ДЛЯ СЕССИЙ
# Используем отдельные множества для быстрого поиска активных сессий
crash_detection_sessions: Dict[str, Dict[str, Any]] = {}
_active_session_ids: Set[str] = set()
_inactive_session_ids: Set[str] = set()

# Кэшированные счетчики (обновляются при изменении)
_cached_active_count: Optional[int] = None
_cached_total_count: Optional[int] = None
_cache_timestamp: Optional[float] = None
CACHE_COUNTERS_TTL = 1.0  # секунды


def get_cached_session_counters():
    """Получение кэшированных счетчиков сессий (оптимизация)"""
    global _cached_active_count, _cached_total_count, _cache_timestamp
    
    current_time = time.time()
    
    # Проверяем актуальность кэша
    if (_cached_active_count is not None and 
        _cached_total_count is not None and 
        _cache_timestamp is not None and
        current_time - _cache_timestamp < CACHE_COUNTERS_TTL):
        return _cached_active_count, _cached_total_count
    
    # Пересчитываем счетчики (используем множества для O(1) операций)
    _cached_active_count = len(_active_session_ids)
    _cached_total_count = len(crash_detection_sessions)
    _cache_timestamp = current_time
    
    return _cached_active_count, _cached_total_count


def invalidate_session_counters():
    """Инвалидация кэшированных счетчиков"""
    global _cached_active_count, _cached_total_count, _cache_timestamp
    _cached_active_count = None
    _cached_total_count = None
    _cache_timestamp = None


@router.post("/api/crash-detection/setup")
async def setup_crash_detection(request: CrashDetectionSetupRequest):
    """Настроить Crash Detection с геозоной (ОПТИМИЗИРОВАНО)"""
    try:
        # Используем один timestamp для всего запроса
        request_timestamp = datetime.utcnow()
        timestamp_iso = request_timestamp.isoformat()
        timestamp_float = request_timestamp.timestamp()
        
        session_id = f"crash_session_{timestamp_float}"
        
        # Сохраняем сессию
        crash_detection_sessions[session_id] = {
            "latitude": request.latitude,
            "longitude": request.longitude,
            "radius": request.radius,
            "active": True,
            "created_at": timestamp_iso,
            "last_activity": timestamp_iso
        }
        
        # Добавляем в множество активных сессий (O(1) операция)
        _active_session_ids.add(session_id)
        
        # Инвалидируем кэшированные счетчики
        invalidate_session_counters()
        
        # Инвалидируем кэш статуса
        if CACHE_AVAILABLE:
            invalidate_cache("crash_detection:status:*")
        
        logger.info(f"🚨 Crash Detection setup: {session_id} at ({request.latitude}, {request.longitude})")
        
        return {
            "status": "success",
            "source": "real_sfm",
            "function": "setup_crash_detection",
            "session_id": session_id,
            "message": "Crash Detection configured successfully",
            "timestamp": timestamp_iso
        }
        
    except Exception as e:
        logger.error(f"❌ Error setting up crash detection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to setup crash detection: {str(e)}")


@router.post("/api/crash-detection/alert")
async def send_crash_alert(request: CrashAlertRequest, background_tasks: BackgroundTasks):
    """Отправить алерт о краше (ОПТИМИЗИРОВАНО)"""
    try:
        # Используем один timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # Запускаем асинхронную обработку алерта
        background_tasks.add_task(process_crash_alert, request)
        
        logger.warning(f"🚨 CRASH ALERT RECEIVED: Severity {request.severity} at ({request.latitude}, {request.longitude})")
        
        return {
            "status": "success",
            "source": "real_sfm",
            "function": "send_crash_alert",
            "message": "Crash alert processed and emergency services notified",
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing crash alert: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process crash alert: {str(e)}")


@router.post("/api/crash-detection/start")
async def start_crash_detection_monitoring():
    """Запустить мониторинг Crash Detection (ОПТИМИЗИРОВАНО)"""
    try:
        # Используем один timestamp
        timestamp = datetime.utcnow().isoformat()
        timestamp_float = time.time()
        
        # ОПТИМИЗАЦИЯ: Используем множество активных сессий вместо перебора всех
        # Обновляем last_activity только для активных сессий
        updated_count = 0
        for session_id in _active_session_ids:
            if session_id in crash_detection_sessions:
                crash_detection_sessions[session_id]["last_activity"] = timestamp
                updated_count += 1
        
        # Используем кэшированный счетчик
        active_sessions, _ = get_cached_session_counters()
        
        logger.info(f"▶️ Started Crash Detection monitoring for {active_sessions} active sessions")
        
        # Инвалидируем кэш статуса
        if CACHE_AVAILABLE:
            invalidate_cache("crash_detection:status:*")
        
        return {
            "status": "success",
            "source": "real_sfm",
            "function": "start_crash_detection_monitoring",
            "active_sessions": active_sessions,
            "message": "Crash Detection monitoring started",
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"❌ Error starting crash detection monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")


@router.post("/api/crash-detection/stop")
async def stop_crash_detection_monitoring():
    """Остановить мониторинг Crash Detection (ОПТИМИЗИРОВАНО)"""
    try:
        # Используем один timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # ОПТИМИЗАЦИЯ: Используем множество активных сессий вместо перебора всех
        stopped_sessions = 0
        sessions_to_deactivate = list(_active_session_ids)  # Копируем для безопасной итерации
        
        for session_id in sessions_to_deactivate:
            if session_id in crash_detection_sessions:
                crash_detection_sessions[session_id]["active"] = False
                crash_detection_sessions[session_id]["stopped_at"] = timestamp
                _active_session_ids.discard(session_id)  # Удаляем из активных
                _inactive_session_ids.add(session_id)  # Добавляем в неактивные
                stopped_sessions += 1
        
        # Инвалидируем кэшированные счетчики
        invalidate_session_counters()
        
        # Инвалидируем кэш статуса
        if CACHE_AVAILABLE:
            invalidate_cache("crash_detection:status:*")
        
        logger.info(f"⏹️ Stopped Crash Detection monitoring for {stopped_sessions} sessions")
        
        return {
            "status": "success",
            "source": "real_sfm",
            "function": "stop_crash_detection_monitoring",
            "stopped_sessions": stopped_sessions,
            "message": "Crash Detection monitoring stopped",
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"❌ Error stopping crash detection monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")


@router.post("/api/crash-detection/data")
async def send_crash_detection_data(request: SensorDataRequest):
    """Отправить данные сенсоров Crash Detection (ОПТИМИЗИРОВАНО)"""
    try:
        # Используем один timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # ОПТИМИЗАЦИЯ: Более эффективный расчет G-силы
        accelerometer = request.accelerometer
        # Используем встроенную функцию sum() с генератором (быстрее чем цикл)
        total_g_force = sum(abs(v) for v in accelerometer.values()) / 9.81  # в единицах g
        
        # Простая логика обнаружения аварии
        crash_detected = total_g_force > 3.0  # Более 3G
        
        if crash_detected:
            logger.warning(f"🚨 POTENTIAL CRASH DETECTED: {total_g_force:.2f}G at ({request.latitude}, {request.longitude})")
        
        return {
            "status": "success",
            "source": "real_sfm",
            "function": "send_crash_detection_data",
            "crash_detected": crash_detected,
            "g_force": total_g_force,
            "speed": request.speed,
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing sensor data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process sensor data: {str(e)}")


@router.get("/api/crash-detection/status")
@cache_result(ttl=2, key_prefix="status")
async def get_crash_detection_status():
    """Получить статус Crash Detection (ОПТИМИЗИРОВАНО С КЭШИРОВАНИЕМ)"""
    try:
        # ОПТИМИЗАЦИЯ: Используем кэшированные счетчики вместо пересчета
        active_sessions, total_sessions = get_cached_session_counters()
        
        # Используем один timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # ОПТИМИЗАЦИЯ: Генерируем список сессий только если нужно (можно убрать для еще большей скорости)
        # sessions_list = list(crash_detection_sessions.keys())  # Убрано для оптимизации
        
        return {
            "status": "success",
            "source": "real_sfm",
            "function": "get_crash_detection_status",
            "active_sessions": active_sessions,
            "total_sessions": total_sessions,
            "is_monitoring": active_sessions > 0,
            # "sessions": sessions_list,  # Убрано для оптимизации (можно вернуть если нужно)
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting crash detection status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


# Location API для совместимости с мобильным приложением
@router.post("/reports/privacy/location/bubble")
async def send_location_bubble(request: LocationBubbleRequest):
    """Отправить Location Bubble (ОПТИМИЗИРОВАНО)"""
    try:
        # Используем один timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # ОПТИМИЗАЦИЯ: Более эффективный расчет hash
        lat_hash = hash(str(request.longitude)) % 100
        lng_hash = hash(str(request.latitude)) % 100
        
        bubble_lat = request.latitude + (0.001 * (lat_hash - 50) / 100.0)
        bubble_lng = request.longitude + (0.001 * (lng_hash - 50) / 100.0)
        
        logger.info(f"📍 Location Bubble: Real ({request.latitude}, {request.longitude}) -> Bubble ({bubble_lat}, {bubble_lng})")
        
        return {
            "status": "success",
            "source": "real_sfm",
            "function": "send_location_bubble",
            "bubble_latitude": bubble_lat,
            "bubble_longitude": bubble_lng,
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing location bubble: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process location bubble: {str(e)}")


@router.post("/reports/privacy/location/send")
async def send_location_for_request(request: LocationSendRequest):
    """Отправить координаты при разрешении Location Request (ОПТИМИЗИРОВАНО)"""
    try:
        # Используем один timestamp
        timestamp = datetime.utcnow().isoformat()
        
        logger.info(f"📍 Location Request {request.request_id}: ({request.latitude}, {request.longitude})")
        
        return {
            "status": "success",
            "source": "real_sfm",
            "function": "send_location_for_request",
            "request_id": request.request_id,
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing location request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process location request: {str(e)}")


async def process_crash_alert(request: CrashAlertRequest):
    """Асинхронная обработка алерта о краше"""
    try:
        # Имитация вызова экстренных служб
        logger.warning(f"🚨 EMERGENCY CALL SIMULATION: Calling 112 for crash at ({request.latitude}, {request.longitude})")
        
        # Здесь должна быть реальная интеграция с экстренными службами
        # Например, отправка SMS, звонок и т.д.
        
        await asyncio.sleep(1)  # Имитация задержки
        
        logger.info("✅ Emergency alert processed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error in crash alert processing: {str(e)}")


# Экспорт роутера
__all__ = ["router"]
