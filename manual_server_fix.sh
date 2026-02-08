# КОМАНДЫ ДЛЯ ВЫПОЛНЕНИЯ НА СЕРВЕРЕ root@149.154.65.180
# Выполните эти команды вручную на сервере

echo "🔧 РУЧНАЯ НАСТРОЙКА CRASH DETECTION НА СЕРВЕРЕ"
echo "=============================================="

cd /opt/aladdin-backend

# Проверить какие файлы API gateway есть
echo "📂 Поиск API gateway файлов..."
find . -name "*api_gateway*" -type f

# Проверить текущий рабочий файл
echo "🔍 Проверка текущего API файла..."
ps aux | grep uvicorn | grep -v grep | head -1

# Найти какой файл используется
UVICORN_CMD=$(ps aux | grep uvicorn | grep -v grep | awk '{for(i=1;i<=NF;i++) if($i ~ /api_gateway/) print $i}' | head -1)
echo "Текущий файл: $UVICORN_CMD"

# Проверить содержимое файла
if [ -f "api_gateway_complete_full.py" ]; then
    echo "✅ api_gateway_complete_full.py найден"
    grep -n "crash_detection" api_gateway_complete_full.py || echo "❌ Импорт crash_detection не найден"
else
    echo "❌ api_gateway_complete_full.py не найден"
    ls -la *api* | head -5
fi

# Добавить импорт вручную если нужно
echo "🔧 Добавление импорта crash_detection_router..."
if [ -f "api_gateway_complete_full.py" ]; then
    grep -q "crash_detection_router" api_gateway_complete_full.py || sed -i '/from security.api.routers import/a from security.api.routers.crash_detection_router import router as crash_detection_router' api_gateway_complete_full.py
    grep -q "app.include_router(crash_detection_router" api_gateway_complete_full.py || sed -i '/app.include_router/a app.include_router(crash_detection_router)' api_gateway_complete_full.py
    echo "✅ Импорт добавлен"
else
    echo "❌ Файл api_gateway_complete_full.py не найден"
fi

# Проверить синтаксис
echo "🔍 Проверка синтаксиса..."
python3 -m py_compile security/api/routers/crash_detection_router.py && echo "✅ crash_detection_router.py - синтаксис OK" || echo "❌ Ошибка синтаксиса в роутере"
python3 -m py_compile security/ai_agents/crash_detection_agent.py && echo "✅ crash_detection_agent.py - синтаксис OK" || echo "❌ Ошибка синтаксиса в агенте"

# Перезапустить сервер
echo "🔄 Перезапуск сервера..."
SERVER_PID=$(ps aux | grep "uvicorn.*api_gateway" | grep -v grep | awk '{print $2}')
if [ ! -z "$SERVER_PID" ]; then
    echo "Останавливаем сервер (PID: $SERVER_PID)..."
    kill $SERVER_PID
    sleep 3
fi

echo "Запуск сервера..."
python3 -m uvicorn api_gateway_complete_full:app --host 0.0.0.0 --port 8002 --reload &
sleep 5

# Тестирование
echo "🧪 Тестирование..."
curl -s http://127.0.0.1:8002/api/health | grep -q "ok" && echo "✅ Health check OK" || echo "❌ Health check FAILED"

curl -s http://127.0.0.1:8002/api/crash-detection/status | grep -q "success" && echo "✅ Crash Detection status OK" || echo "❌ Crash Detection status FAILED"

# Полное тестирование
echo "🔬 Полное тестирование Crash Detection API..."

# Тест setup
RESPONSE=$(curl -s -X POST http://127.0.0.1:8002/api/crash-detection/setup \
  -H "Content-Type: application/json" \
  -d '{"latitude": 55.7558, "longitude": 37.6173, "radius": 500}')

echo "$RESPONSE" | grep -q "success" && echo "✅ Setup OK" || echo "❌ Setup FAILED: $RESPONSE"

# Тест start
curl -s -X POST http://127.0.0.1:8002/api/crash-detection/start | grep -q "success" && echo "✅ Start OK" || echo "❌ Start FAILED"

# Тест data
CRASH_DATA=$(curl -s -X POST http://127.0.0.1:8002/api/crash-detection/data \
  -H "Content-Type: application/json" \
  -d '{
    "accelerometer": {"x": 35.5, "y": -8.2, "z": 4.1},
    "gyroscope": {"x": 2.1, "y": 1.8, "z": -1.2},
    "speed": 65.5,
    "latitude": 55.7558,
    "longitude": 37.6173,
    "timestamp": 1707234567.123
  }')

echo "$CRASH_DATA" | grep -q "crash_detected" && echo "✅ Data processing OK" || echo "❌ Data processing FAILED"

echo ""
echo "🎉 НАСТРОЙКА ЗАВЕРШЕНА!"
echo "Проверьте работу с мобильного приложения!"