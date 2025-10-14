#!/bin/bash

# Скрипт запуска External APIs Server для ALADDIN Security System

echo "🚀 Запуск External APIs Server..."

# Убиваем все предыдущие процессы external_apis_server.py
pkill -f external_apis_server.py

# Переходим в директорию проекта
cd /Users/sergejhlystov/ALADDIN_NEW

# Запускаем external_apis_server.py в фоне
python3 external_apis_server.py &
PID=$!

echo "📊 External APIs Server запущен с PID: $PID"
echo "🌐 Доступен по адресу: http://localhost:5004"
echo "🔧 API: http://localhost:5004/api/external/"

# Ждем несколько секунд, чтобы сервер успел запуститься
sleep 5

# Проверяем статус сервера
HEALTH_CHECK=$(curl -s http://localhost:5004/api/external/health 2>/dev/null)

if [ "$HEALTH_CHECK" == *"ok"* ]; then
    echo "✅ External APIs Server работает!"
    echo "📋 Доступные endpoints:"
    echo "   - Health: http://localhost:5004/api/external/health"
    echo "   - Threat Intelligence: http://localhost:5004/api/external/threat-intelligence"
    echo "   - IP Geolocation: http://localhost:5004/api/external/ip-geolocation"
    echo "   - Email Validation: http://localhost:5004/api/external/email-validation"
    echo "   - Statistics: http://localhost:5004/api/external/statistics"
    echo "   - API Status: http://localhost:5004/api/external/status"
    echo "   - Test All: http://localhost:5004/api/external/test-all"
else
    echo "❌ External APIs Server не отвечает. Проверьте логи."
fi

echo "🛑 Для остановки выполните: pkill -f external_apis_server.py"