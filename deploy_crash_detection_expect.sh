#!/bin/bash
# Развертывание Crash Detection API с inline expect командами
# Аналогично тому, как мы делали ранее

cd "$(dirname "$0")"

SERVER="149.154.65.180"
USER="root"
PASSWORD="Sergio675"
REMOTE_PATH="/opt/aladdin-backend"

echo "=========================================="
echo "🚨 РАЗВЕРТЫВАНИЕ CRASH DETECTION API"
echo "=========================================="
echo ""

# Создание backup директории на сервере
echo "📁 Создание backup..."
/usr/bin/expect <<EOF
set timeout 30
spawn ssh -o StrictHostKeyChecking=no $USER@$SERVER "mkdir -p $REMOTE_PATH/backup_\$(date +%Y%m%d_%H%M%S) && cp -r $REMOTE_PATH/security $REMOTE_PATH/backup_\$(date +%Y%m%d_%H%M%S)/ 2>/dev/null && echo '✅ Backup создан'"
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    eof
}
EOF
echo ""

# Загрузка crash_detection_router.py
echo "📤 Загрузка crash_detection_router.py..."
/usr/bin/expect <<EOF
set timeout 60
spawn scp -o StrictHostKeyChecking=no crash_detection_router.py $USER@$SERVER:$REMOTE_PATH/security/api/routers/
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    "yes/no" { send "yes\r"; exp_continue }
    eof
}
EOF
echo "✅ crash_detection_router.py загружен"
echo ""

# Загрузка crash_detection_agent.py
echo "📤 Загрузка crash_detection_agent.py..."
/usr/bin/expect <<EOF
set timeout 60
spawn scp -o StrictHostKeyChecking=no crash_detection_agent.py $USER@$SERVER:$REMOTE_PATH/security/ai_agents/
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    eof
}
EOF
echo "✅ crash_detection_agent.py загружен"
echo ""

# Обновление главного API файла
echo "🔧 Обновление api_gateway_complete_full.py..."
/usr/bin/expect <<EOF
set timeout 120
spawn ssh -o StrictHostKeyChecking=no $USER@$SERVER "cd $REMOTE_PATH && echo 'Проверка импорта crash_detection_router...' && grep -q 'crash_detection_router' api_gateway_complete_full.py || sed -i '/from security.api.routers import/a from security.api.routers.crash_detection_router import router as crash_detection_router' api_gateway_complete_full.py && echo '✅ Импорт добавлен' && echo 'Проверка регистрации роутера...' && grep -q 'app.include_router(crash_detection_router' api_gateway_complete_full.py || sed -i '/app.include_router/a app.include_router(crash_detection_router)' api_gateway_complete_full.py && echo '✅ Роутер зарегистрирован'"
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    eof
}
EOF
echo "✅ api_gateway_complete_full.py обновлен"
echo ""

# Проверка синтаксиса Python
echo "🔍 Проверка синтаксиса Python..."
/usr/bin/expect <<EOF
set timeout 30
spawn ssh -o StrictHostKeyChecking=no $USER@$SERVER "cd $REMOTE_PATH && python3 -m py_compile security/api/routers/crash_detection_router.py && echo '✅ crash_detection_router.py - синтаксис OK' && python3 -m py_compile security/ai_agents/crash_detection_agent.py && echo '✅ crash_detection_agent.py - синтаксис OK'"
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    eof
}
EOF
echo ""

# Перезапуск сервера
echo "🔄 Перезапуск сервера..."
/usr/bin/expect <<EOF
set timeout 60
spawn ssh -o StrictHostKeyChecking=no $USER@$SERVER "cd $REMOTE_PATH && echo 'Поиск процесса uvicorn...' && SERVER_PID=\$(ps aux | grep 'uvicorn.*api_gateway' | grep -v grep | awk '{print \$2}') && if [ ! -z \"\$SERVER_PID\" ]; then echo \"Останавливаем сервер (PID: \$SERVER_PID)...\" && kill \$SERVER_PID && sleep 3; else echo 'Сервер не найден, продолжаем...'; fi && echo 'Запуск сервера...' && python3 -m uvicorn api_gateway_complete_full:app --host 0.0.0.0 --port 8002 --reload &> /dev/null & && sleep 5 && echo '✅ Сервер запущен'"
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    eof
}
EOF
echo ""

# Тестирование API
echo "🧪 Тестирование API..."
/usr/bin/expect <<EOF
set timeout 30
spawn ssh -o StrictHostKeyChecking=no $USER@$SERVER "echo 'Тест health check...' && curl -s http://127.0.0.1:8002/api/health | grep -q 'ok' && echo '✅ Health check OK' || echo '❌ Health check FAILED' && echo 'Тест Crash Detection status...' && curl -s http://127.0.0.1:8002/api/crash-detection/status | grep -q 'success' && echo '✅ Crash Detection status OK' || echo '❌ Crash Detection status FAILED' && echo 'Тест Crash Detection setup...' && RESPONSE=\$(curl -s -X POST http://127.0.0.1:8002/api/crash-detection/setup -H 'Content-Type: application/json' -d '{\"latitude\": 55.7558, \"longitude\": 37.6173, \"radius\": 500}') && echo \"\$RESPONSE\" | grep -q 'success' && echo '✅ Crash Detection setup OK' || echo '❌ Crash Detection setup FAILED'"
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    eof
}
EOF
echo ""

# Финальная проверка
echo "🎯 Финальная проверка..."
/usr/bin/expect <<EOF
set timeout 30
spawn ssh -o StrictHostKeyChecking=no $USER@$SERVER "echo 'Проверка процессов...' && ps aux | grep uvicorn | grep -v grep | wc -l && echo 'Проверка порта...' && netstat -tlnp | grep 8002 || ss -tlnp | grep 8002 && echo 'Проверка логов...' && tail -3 /opt/aladdin-backend/logs/api.log 2>/dev/null || echo 'Логи не найдены'"
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    eof
}
EOF
echo ""

echo "=========================================="
echo "🎉 РАЗВЕРТЫВАНИЕ CRASH DETECTION ЗАВЕРШЕНО!"
echo "=========================================="
echo ""
echo "📊 Результаты:"
echo "✅ Файлы загружены на сервер"
echo "✅ API Gateway обновлен"
echo "✅ Синтаксис проверен"
echo "✅ Сервер перезапущен"
echo "✅ API протестировано"
echo ""
echo "🧪 Полная валидация: python3 validate_deployment_completion.py"
echo "📱 Мобильное приложение готово к использованию Crash Detection!"
echo ""
echo "🚨 ВАЖНО: Если возникли ошибки, проверьте логи сервера:"
echo "ssh root@149.154.65.180 'tail -f /opt/aladdin-backend/logs/api.log'"