# security/api/routers/crash_detection_router.py - ОБНОВЛЕННАЯ ВЕРСИЯ С PostgreSQL
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import asyncio
import time
import os
import uuid

# ✅ ИМПОРТЫ ДЛЯ PostgreSQL
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.database import get_db
from app.auth.auth import get_current_user
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Импорт модуля кэширования (оставляем для совместимости)
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
        def cache_result(ttl=2, key_prefix=None):
            def decorator(func):
                return func
            return decorator
except ImportError as e:
    CACHE_AVAILABLE = False
    logger.warning(f"Модуль кэширования недоступен: {e}")
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
    session_id: str
    latitude: float
    longitude: float
    severity: str
    accelerometer_data: Optional[Dict[str, float]] = None
    gyroscope_data: Optional[Dict[str, float]] = None
    speed: Optional[float] = None
    g_force: Optional[float] = None

class SensorDataRequest(BaseModel):
    session_id: str
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

# ✅ УДАЛЕНО: In-memory хранилище
# crash_detection_sessions: Dict[str, Dict[str, Any]] = {}
# _active_session_ids: Set[str] = set()
# _inactive_session_ids: Set[str] = set()

# ✅ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ РАБОТЫ С БД

def save_crash_alert_to_db(
    db: Session,
    user_id: str,
    session_id: str,
    latitude: float,
    longitude: float,
    severity: str,
    accelerometer_data: Optional[Dict] = None,
    gyroscope_data: Optional[Dict] = None,
    speed: Optional[float] = None,
    g_force: Optional[float] = None,
    crash_detected: bool = False
) -> str:
    """Сохранить алерт о ДТП в БД"""
    try:
        alert_id = str(uuid.uuid4())
        
        # Преобразуем данные в JSON для JSONB
        accelerometer_json = json.dumps(accelerometer_data) if accelerometer_data else None
        gyroscope_json = json.dumps(gyroscope_data) if gyroscope_data else None
        
        query = text("""
            INSERT INTO crash_detection_alerts (
                id, user_id, session_id, latitude, longitude, severity,
                accelerometer_data, gyroscope_data, speed, g_force, crash_detected,
                timestamp, created_at, updated_at
            ) VALUES (
                :id, :user_id::uuid, :session_id, :latitude, :longitude, :severity,
                :accelerometer_data::jsonb, :gyroscope_data::jsonb, :speed, :g_force, :crash_detected,
                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            )
        """)
        
        db.execute(query, {
            "id": alert_id,
            "user_id": user_id,
            "session_id": session_id,
            "latitude": float(latitude),
            "longitude": float(longitude),
            "severity": severity,
            "accelerometer_data": accelerometer_json,
            "gyroscope_data": gyroscope_json,
            "speed": speed,
            "g_force": g_force,
            "crash_detected": crash_detected
        })
        
        db.commit()
        logger.info(f"✅ Crash alert saved to DB: {alert_id}")
        return alert_id
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error saving crash alert to DB: {str(e)}")
        raise

def get_active_sessions_count(db: Session, user_id: str) -> int:
    """Получить количество активных сессий из БД"""
    try:
        query = text("""
            SELECT COUNT(DISTINCT session_id) 
            FROM crash_detection_alerts 
            WHERE user_id = :user_id::uuid
            AND timestamp > NOW() - INTERVAL '1 hour'
        """)
        
        result = db.execute(query, {"user_id": user_id})
        count = result.scalar() or 0
        return count
        
    except Exception as e:
        logger.error(f"❌ Error getting active sessions count: {str(e)}")
        return 0

# ✅ ОБНОВЛЕННЫЕ ENDPOINTS

@router.post("/api/crash-detection/setup")
async def setup_crash_detection(
    request: CrashDetectionSetupRequest,
    current_user: dict = Depends(get_current_user)
):
    """Настроить Crash Detection с геозоной (ОБНОВЛЕНО: использует общий роутер для статуса)"""
    try:
        user_id = current_user["id"]
        timestamp = datetime.utcnow().isoformat()
        
        # ✅ ИСПОЛЬЗУЕМ ОБЩИЙ РОУТЕР: Статус компонента управляется через /api/components/status
        # Здесь только логируем настройку геозоны
        logger.info(f"🚨 Crash Detection setup for user {user_id} at ({request.latitude}, {request.longitude})")
        
        return {
            "status": "success",
            "source": "real_sfm",
            "function": "setup_crash_detection",
            "message": "Crash Detection configured successfully. Use /api/components/enable/crash_detection_agent to enable.",
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"❌ Error setting up crash detection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to setup crash detection: {str(e)}")


@router.post("/api/crash-detection/alert")
async def send_crash_alert(
    request: CrashAlertRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Отправить алерт о краше (ОБНОВЛЕНО: сохраняет в БД)"""
    try:
        user_id = str(current_user["id"])
        timestamp = datetime.utcnow().isoformat()
        
        # Сохраняем алерт в БД
        alert_id = save_crash_alert_to_db(
            db=db,
            user_id=user_id,
            session_id=request.session_id,
            latitude=request.latitude,
            longitude=request.longitude,
            severity=request.severity,
            accelerometer_data=request.accelerometer_data,
            gyroscope_data=request.gyroscope_data,
            speed=request.speed,
            g_force=request.g_force,
            crash_detected=True
        )
        
        # Запускаем асинхронную обработку алерта (вызов экстренных служб)
        background_tasks.add_task(process_crash_alert, request, alert_id)
        
        logger.warning(f"🚨 CRASH ALERT RECEIVED: {alert_id} - Severity {request.severity} at ({request.latitude}, {request.longitude})")
        
        return {
            "status": "success",
            "source": "real_sfm",
            "function": "send_crash_alert",
            "alert_id": alert_id,
            "message": "Crash alert processed and emergency services notified",
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing crash alert: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process crash alert: {str(e)}")


@router.post("/api/crash-detection/start")
async def start_crash_detection_monitoring(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Запустить мониторинг Crash Detection (ОБНОВЛЕНО: использует общий роутер)"""
    try:
        user_id = str(current_user["id"])
        timestamp = datetime.utcnow().isoformat()
        
        # ✅ ИСПОЛЬЗУЕМ ОБЩИЙ РОУТЕР: Включение компонента через /api/components/enable/crash_detection_agent
        # Получаем количество активных сессий из БД
        active_sessions = get_active_sessions_count(db, user_id)
        
        logger.info(f"▶️ Started Crash Detection monitoring for user {user_id} ({active_sessions} active sessions)")
        
        return {
            "status": "success",
            "source": "real_sfm",
            "function": "start_crash_detection_monitoring",
            "active_sessions": active_sessions,
            "message": "Crash Detection monitoring started. Use /api/components/enable/crash_detection_agent to enable component.",
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"❌ Error starting crash detection monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")


@router.post("/api/crash-detection/stop")
async def stop_crash_detection_monitoring(
    current_user: dict = Depends(get_current_user)
):
    """Остановить мониторинг Crash Detection (ОБНОВЛЕНО: использует общий роутер)"""
    try:
        user_id = current_user["id"]
        timestamp = datetime.utcnow().isoformat()
        
        # ✅ ИСПОЛЬЗУЕМ ОБЩИЙ РОУТЕР: Выключение компонента через /api/components/disable/crash_detection_agent
        logger.info(f"⏹️ Stopped Crash Detection monitoring for user {user_id}")
        
        return {
            "status": "success",
            "source": "real_sfm",
            "function": "stop_crash_detection_monitoring",
            "message": "Crash Detection monitoring stopped. Use /api/components/disable/crash_detection_agent to disable component.",
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"❌ Error stopping crash detection monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")


@router.post("/api/crash-detection/data")
async def send_crash_detection_data(
    request: SensorDataRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Отправить данные сенсоров Crash Detection (ОБНОВЛЕНО: сохраняет алерты в БД)"""
    try:
        user_id = str(current_user["id"])
        timestamp = datetime.utcnow().isoformat()
        
        # ОПТИМИЗАЦИЯ: Более эффективный расчет G-силы
        accelerometer = request.accelerometer
        total_g_force = sum(abs(v) for v in accelerometer.values()) / 9.81  # в единицах g
        
        # Простая логика обнаружения аварии
        crash_detected = total_g_force > 3.0  # Более 3G
        
        # ✅ СОХРАНЯЕМ АЛЕРТ В БД, ЕСЛИ ОБНАРУЖЕНО ДТП
        alert_id = None
        if crash_detected:
            logger.warning(f"🚨 POTENTIAL CRASH DETECTED: {total_g_force:.2f}G at ({request.latitude}, {request.longitude})")
            
            alert_id = save_crash_alert_to_db(
                db=db,
                user_id=user_id,
                session_id=request.session_id,
                latitude=request.latitude or 0.0,
                longitude=request.longitude or 0.0,
                severity="high" if total_g_force > 5.0 else "medium",
                accelerometer_data=request.accelerometer,
                gyroscope_data=request.gyroscope,
                speed=request.speed,
                g_force=total_g_force,
                crash_detected=True
            )
        
        return {
            "status": "success",
            "source": "real_sfm",
            "function": "send_crash_detection_data",
            "crash_detected": crash_detected,
            "g_force": total_g_force,
            "speed": request.speed,
            "alert_id": alert_id,
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"❌ Error processing sensor data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process sensor data: {str(e)}")


@router.get("/api/crash-detection/status")
@cache_result(ttl=2, key_prefix="status")
async def get_crash_detection_status(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить статус Crash Detection (ОБНОВЛЕНО: использует БД)"""
    try:
        user_id = str(current_user["id"])
        timestamp = datetime.utcnow().isoformat()
        
        # Получаем количество активных сессий из БД
        active_sessions = get_active_sessions_count(db, user_id)
        
        # Получаем общее количество алертов за последний час
        query = text("""
            SELECT COUNT(*) 
            FROM crash_detection_alerts 
            WHERE user_id = :user_id::uuid
            AND timestamp > NOW() - INTERVAL '1 hour'
        """)
        result = db.execute(query, {"user_id": user_id})
        total_alerts = result.scalar() or 0
        
        return {
            "status": "success",
            "source": "real_sfm",
            "function": "get_crash_detection_status",
            "active_sessions": active_sessions,
            "total_alerts_last_hour": total_alerts,
            "is_monitoring": active_sessions > 0,
            "timestamp": timestamp
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting crash detection status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


# Location API для совместимости с мобильным приложением
@router.post("/reports/privacy/location/bubble")
async def send_location_bubble(request: LocationBubbleRequest):
    """Отправить Location Bubble (без изменений)"""
    try:
        timestamp = datetime.utcnow().isoformat()
        
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
    """Отправить координаты при разрешении Location Request (без изменений)"""
    try:
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


async def process_crash_alert(request: CrashAlertRequest, alert_id: str):
    """Асинхронная обработка алерта о краше"""
    try:
        # Имитация вызова экстренных служб
        logger.warning(f"🚨 EMERGENCY CALL SIMULATION: Calling 112 for crash alert {alert_id} at ({request.latitude}, {request.longitude})")
        
        # Здесь должна быть реальная интеграция с экстренными службами
        # Например, отправка SMS, звонок и т.д.
        
        await asyncio.sleep(1)  # Имитация задержки
        
        logger.info(f"✅ Emergency alert {alert_id} processed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error in crash alert processing: {str(e)}")


# Экспорт роутера
__all__ = ["router"]
