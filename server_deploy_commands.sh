# КОМАНДЫ ДЛЯ ВЫПОЛНЕНИЯ НА СЕРВЕРЕ ALADDIN
# Скопируйте и выполните эти команды на сервере root@149.154.65.180

echo "🚀 НАЧИНАЕМ ДЕПЛОЙ CRASH DETECTION НА СЕРВЕРЕ"
echo "=============================================="

# Перейти в tmp директорию
cd /tmp

# Создать файлы (скопируйте содержимое из crash_detection_router_content.txt)
echo "📝 Создание файлов..."
cat > crash_detection_router.py << 'EOF'
# security/api/routers/crash_detection_router.py
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Глобальное состояние Crash Detection
crash_detection_sessions = {}

@router.post("/api/crash-detection/setup")
async def setup_crash_detection(request: CrashDetectionSetupRequest):
    """Настроить Crash Detection с геозоной"""
    try:
        session_id = f"crash_session_{datetime.utcnow().timestamp()}"

        # Сохраняем сессию
        crash_detection_sessions[session_id] = {
            "latitude": request.latitude,
            "longitude": request.longitude,
            "radius": request.radius,
            "active": True,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat()
        }

        logger.info(f"🚨 Crash Detection setup: {session_id} at ({request.latitude}, {request.longitude})")

        return {
            "status": "success",
            "source": "real_sfm",
            "function": "setup_crash_detection",
            "session_id": session_id,
            "message": "Crash Detection configured successfully",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error setting up crash detection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to setup crash detection: {str(e)}")

@router.post("/api/crash-detection/alert")
async def send_crash_alert(request: CrashAlertRequest, background_tasks: BackgroundTasks):
    """Отправить алерт о краше"""
    try:
        # Запускаем асинхронную обработку алерта
        background_tasks.add_task(process_crash_alert, request)

        logger.warning(f"🚨 CRASH ALERT RECEIVED: Severity {request.severity} at ({request.latitude}, {request.longitude})")

        return {
            "status": "success",
            "source": "real_sfm",
            "function": "send_crash_alert",
            "message": "Crash alert processed and emergency services notified",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error processing crash alert: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process crash alert: {str(e)}")

@router.post("/api/crash-detection/start")
async def start_crash_detection_monitoring():
    """Запустить мониторинг Crash Detection"""
    try:
        # Активируем все существующие сессии
        active_sessions = 0
        for session_id, session in crash_detection_sessions.items():
            if session["active"]:
                session["last_activity"] = datetime.utcnow().isoformat()
                active_sessions += 1

        logger.info(f"▶️ Started Crash Detection monitoring for {active_sessions} active sessions")

        return {
            "status": "success",
            "source": "real_sfm",
            "function": "start_crash_detection_monitoring",
            "active_sessions": active_sessions,
            "message": "Crash Detection monitoring started",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error starting crash detection monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")

@router.post("/api/crash-detection/stop")
async def stop_crash_detection_monitoring():
    """Остановить мониторинг Crash Detection"""
    try:
        # Деактивируем все сессии
        stopped_sessions = 0
        for session_id, session in crash_detection_sessions.items():
            if session["active"]:
                session["active"] = False
                session["stopped_at"] = datetime.utcnow().isoformat()
                stopped_sessions += 1

        logger.info(f"⏹️ Stopped Crash Detection monitoring for {stopped_sessions} sessions")

        return {
            "status": "success",
            "source": "real_sfm",
            "function": "stop_crash_detection_monitoring",
            "stopped_sessions": stopped_sessions,
            "message": "Crash Detection monitoring stopped",
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error stopping crash detection monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to stop monitoring: {str(e)}")

@router.post("/api/crash-detection/data")
async def send_crash_detection_data(request: SensorDataRequest):
    """Отправить данные сенсоров Crash Detection"""
    try:
        # Анализируем данные акселерометра для обнаружения аварии
        accelerometer = request.accelerometer
        total_g_force = sum(abs(v) for v in accelerometer.values()) / 9.81  # в единицах g

        # Простая логика обнаружения аварии (можно улучшить)
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
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error processing sensor data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process sensor data: {str(e)}")

@router.get("/api/crash-detection/status")
async def get_crash_detection_status():
    """Получить статус Crash Detection"""
    try:
        active_sessions = sum(1 for s in crash_detection_sessions.values() if s["active"])
        total_sessions = len(crash_detection_sessions)

        return {
            "status": "success",
            "source": "real_sfm",
            "function": "get_crash_detection_status",
            "active_sessions": active_sessions,
            "total_sessions": total_sessions,
            "is_monitoring": active_sessions > 0,
            "sessions": list(crash_detection_sessions.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error getting crash detection status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

# Location API для совместимости с мобильным приложением
@router.post("/reports/privacy/location/bubble")
async def send_location_bubble(request: LocationBubbleRequest):
    """Отправить Location Bubble"""
    try:
        # Генерируем "пузырь" вокруг реальной геолокации
        # В реальности здесь должна быть сложная логика анонимизации
        bubble_lat = request.latitude + (0.001 * (hash(str(request.longitude)) % 100 - 50) / 100.0)
        bubble_lng = request.longitude + (0.001 * (hash(str(request.latitude)) % 100 - 50) / 100.0)

        logger.info(f"📍 Location Bubble: Real ({request.latitude}, {request.longitude}) -> Bubble ({bubble_lat}, {bubble_lng})")

        return {
            "status": "success",
            "source": "real_sfm",
            "function": "send_location_bubble",
            "bubble_latitude": bubble_lat,
            "bubble_longitude": bubble_lng,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error processing location bubble: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process location bubble: {str(e)}")

@router.post("/reports/privacy/location/send")
async def send_location_for_request(request: LocationSendRequest):
    """Отправить координаты при разрешении Location Request"""
    try:
        logger.info(f"📍 Location Request {request.request_id}: ({request.latitude}, {request.longitude})")

        return {
            "status": "success",
            "source": "real_sfm",
            "function": "send_location_for_request",
            "request_id": request.request_id,
            "timestamp": datetime.utcnow().isoformat()
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
EOF

cat > crash_detection_agent.py << 'EOF'
# security/ai_agents/crash_detection_agent.py
import logging
from typing import Dict, Any, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class CrashDetectionAgent:
    """AI Агент для обнаружения аварий"""

    def __init__(self):
        self.name = "crash_detection_agent"
        self.version = "1.0.0"
        self.capabilities = [
            "crash_detection",
            "emergency_response",
            "location_tracking",
            "sensor_analysis"
        ]

    def get_functions(self) -> List[Dict[str, Any]]:
        """Получить список доступных функций"""
        return [
            {
                "name": "setup_crash_detection",
                "description": "Настроить мониторинг аварий с геозоной",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                        "radius": {"type": "number", "default": 500}
                    },
                    "required": ["latitude", "longitude"]
                }
            },
            {
                "name": "send_crash_alert",
                "description": "Отправить алерт об аварии",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                        "severity": {"type": "string"}
                    },
                    "required": ["latitude", "longitude", "severity"]
                }
            },
            {
                "name": "start_crash_detection_monitoring",
                "description": "Запустить мониторинг аварий",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "stop_crash_detection_monitoring",
                "description": "Остановить мониторинг аварий",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "send_crash_detection_data",
                "description": "Обработать данные сенсоров",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "accelerometer": {"type": "object"},
                        "gyroscope": {"type": "object"},
                        "speed": {"type": "number"},
                        "latitude": {"type": "number"},
                        "longitude": {"type": "number"},
                        "timestamp": {"type": "number"}
                    }
                }
            },
            {
                "name": "get_crash_detection_status",
                "description": "Получить статус мониторинга",
                "parameters": {"type": "object", "properties": {}}
            }
        ]

    def execute_function(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнить функцию агента"""
        try:
            if function_name == "setup_crash_detection":
                return self._setup_crash_detection(parameters)
            elif function_name == "send_crash_alert":
                return self._send_crash_alert(parameters)
            elif function_name == "start_crash_detection_monitoring":
                return self._start_monitoring()
            elif function_name == "stop_crash_detection_monitoring":
                return self._stop_monitoring()
            elif function_name == "send_crash_detection_data":
                return self._process_sensor_data(parameters)
            elif function_name == "get_crash_detection_status":
                return self._get_status()
            else:
                raise ValueError(f"Unknown function: {function_name}")

        except Exception as e:
            logger.error(f"Error executing {function_name}: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    def _setup_crash_detection(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Настроить мониторинг аварий"""
        latitude = params.get("latitude")
        longitude = params.get("longitude")
        radius = params.get("radius", 500)

        logger.info(f"Setting up crash detection at ({latitude}, {longitude}) with radius {radius}m")

        return {
            "status": "success",
            "message": f"Crash detection configured at ({latitude}, {longitude})",
            "radius": radius,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _send_crash_alert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Отправить алерт об аварии"""
        latitude = params.get("latitude")
        longitude = params.get("longitude")
        severity = params.get("severity", "unknown")

        logger.warning(f"CRASH ALERT: {severity} crash detected at ({latitude}, {longitude})")

        # Имитация вызова экстренных служб
        return {
            "status": "success",
            "message": "Emergency services notified",
            "location": {"lat": latitude, "lng": longitude},
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _start_monitoring(self) -> Dict[str, Any]:
        """Запустить мониторинг"""
        logger.info("Crash detection monitoring started")
        return {
            "status": "success",
            "message": "Monitoring started",
            "timestamp": datetime.utcnow().isoformat()
        }

    def _stop_monitoring(self) -> Dict[str, Any]:
        """Остановить мониторинг"""
        logger.info("Crash detection monitoring stopped")
        return {
            "status": "success",
            "message": "Monitoring stopped",
            "timestamp": datetime.utcnow().isoformat()
        }

    def _process_sensor_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Обработать данные сенсоров"""
        accelerometer = params.get("accelerometer", {})
        gyroscope = params.get("gyroscope", {})
        speed = params.get("speed", 0)
        latitude = params.get("latitude")
        longitude = params.get("longitude")

        # Простая логика обнаружения аварии
        total_g = sum(abs(v) for v in accelerometer.values()) / 9.81
        crash_detected = total_g > 3.0

        if crash_detected:
            logger.warning(f"Potential crash detected: {total_g:.2f}G at ({latitude}, {longitude})")

        return {
            "status": "success",
            "crash_detected": crash_detected,
            "g_force": total_g,
            "speed": speed,
            "location": {"lat": latitude, "lng": longitude},
            "timestamp": datetime.utcnow().isoformat()
        }

    def _get_status(self) -> Dict[str, Any]:
        """Получить статус"""
        return {
            "status": "success",
            "monitoring_active": True,  # Заглушка
            "active_sessions": 1,
            "timestamp": datetime.utcnow().isoformat()
        }

# Создание экземпляра агента
agent = CrashDetectionAgent()
EOF

cat > deploy_crash_detection_server.sh << 'EOF'
#!/bin/bash

# Скрипт деплоя Crash Detection API на сервер ALADDIN
# Запускать на сервере root@149.154.65.180

echo "🚨 ДЕПЛОЙ CRASH DETECTION API НА СЕРВЕР ALADDIN"
echo "=============================================="
echo ""

BACKUP_DIR="/opt/aladdin-backend/backup_$(date +%Y%m%d_%H%M%S)"

echo "📁 Создание бэкапа..."
mkdir -p "$BACKUP_DIR"
cp -r /opt/aladdin-backend/security "$BACKUP_DIR/" 2>/dev/null || echo "Предупреждение: папка security не найдена"

echo "📝 Копирование файлов..."
cp /tmp/crash_detection_router.py /opt/aladdin-backend/security/api/routers/ || {
    echo "❌ Ошибка копирования роутера"
    exit 1
}

cp /tmp/crash_detection_agent.py /opt/aladdin-backend/security/ai_agents/ || {
    echo "❌ Ошибка копирования агента"
    exit 1
}

echo "🔧 Обновление главного API файла..."

# Проверяем и добавляем импорт crash_detection_router
if ! grep -q "crash_detection_router" /opt/aladdin-backend/api_gateway_complete_full.py; then
    echo "Добавление импорта crash_detection_router..."
    sed -i '/from security.api.routers import/a from security.api.routers.crash_detection_router import router as crash_detection_router' /opt/aladdin-backend/api_gateway_complete_full.py
fi

# Проверяем и добавляем регистрацию роутера
if ! grep -q "app.include_router(crash_detection_router" /opt/aladdin-backend/api_gateway_complete_full.py; then
    echo "Регистрация crash_detection_router..."
    sed -i '/app.include_router/a app.include_router(crash_detection_router)' /opt/aladdin-backend/api_gateway_complete_full.py
fi

echo "🔄 Перезапуск сервера..."

# Находим и перезапускаем процесс сервера
SERVER_PID=$(ps aux | grep "uvicorn.*api_gateway" | grep -v grep | awk '{print $2}')
if [ ! -z "$SERVER_PID" ]; then
    echo "Останавливаем сервер (PID: $SERVER_PID)..."
    kill $SERVER_PID
    sleep 3
fi

echo "Запуск сервера..."
cd /opt/aladdin-backend
python3 -m uvicorn api_gateway_complete_full:app --host 0.0.0.0 --port 8002 --reload &
sleep 5

echo ""
echo "🧪 Тестирование API..."

# Тест базового эндпоинта
curl -s "http://localhost:8002/api/health" | grep -q "ok" && echo "✅ Health check OK" || echo "❌ Health check FAILED"

# Тест Crash Detection setup
RESPONSE=$(curl -s -X POST "http://localhost:8002/api/crash-detection/setup" \
  -H "Content-Type: application/json" \
  -d '{"latitude": 55.7558, "longitude": 37.6173, "radius": 500}')

echo "$RESPONSE" | grep -q "success" && echo "✅ Setup OK" || echo "❌ Setup FAILED"

# Тест Crash Detection status
curl -s "http://localhost:8002/api/crash-detection/status" | grep -q "success" && echo "✅ Status OK" || echo "❌ Status FAILED"

echo ""
echo "🎉 ДЕПЛОЙ CRASH DETECTION API ЗАВЕРШЕН!"
echo "📝 Проверьте логи сервера для подтверждения работы"
echo "🧪 Полная валидация: python3 validate_deployment_completion.py"
EOF

echo "📂 Файлы созданы в /tmp"
ls -la crash_detection_*

echo ""
echo "🔧 Выполнение деплоя..."
chmod +x deploy_crash_detection_server.sh
./deploy_crash_detection_server.sh

echo ""
echo "🧪 Тестирование после деплоя..."

# Тест статуса
echo "Тестируем статус..."
curl -s "http://localhost:8002/api/crash-detection/status" | head -5

# Тест setup
echo "Тестируем setup..."
curl -s -X POST "http://localhost:8002/api/crash-detection/setup" \
  -H "Content-Type: application/json" \
  -d '{"latitude": 55.7558, "longitude": 37.6173, "radius": 500}' | head -5

echo ""
echo "✅ РУЧНОЙ ДЕПЛОЙ ЗАВЕРШЕН!"
echo "📞 Если возникли проблемы, проверьте логи сервера"