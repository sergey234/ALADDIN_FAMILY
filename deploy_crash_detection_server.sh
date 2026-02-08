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
echo "Тестируем /api/health..."
curl -s "http://localhost:8002/api/health" | grep -q "ok" && echo "✅ Health check OK" || echo "❌ Health check FAILED"

# Тест Crash Detection setup
echo "Тестируем Crash Detection setup..."
RESPONSE=$(curl -s -X POST "http://localhost:8002/api/crash-detection/setup" \
  -H "Content-Type: application/json" \
  -d '{"latitude": 55.7558, "longitude": 37.6173, "radius": 500}')

echo "$RESPONSE" | grep -q "success" && echo "✅ Setup OK" || echo "❌ Setup FAILED"

# Тест Crash Detection status
echo "Тестируем Crash Detection status..."
curl -s "http://localhost:8002/api/crash-detection/status" | grep -q "success" && echo "✅ Status OK" || echo "❌ Status FAILED"

echo ""
echo "🎉 ДЕПЛОЙ CRASH DETECTION API ЗАВЕРШЕН!"
echo "📝 Проверьте логи сервера для подтверждения работы"
echo "🧪 Полная валидация: python3 validate_deployment_completion.py"