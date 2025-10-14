#!/bin/bash

# Скрипт запуска Monitoring API Server
# ALADDIN Security System

echo "🚀 Запуск Monitoring API Server..."

# Проверяем, что мы в правильной директории
if [ ! -f "monitoring_api_server.py" ]; then
    echo "❌ Ошибка: monitoring_api_server.py не найден"
    echo "Запустите скрипт из директории ALADDIN_NEW"
    exit 1
fi

# Проверяем, что порт 5006 свободен
if lsof -Pi :5006 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️ Порт 5006 уже занят"
    echo "Останавливаем существующий процесс..."
    pkill -f "monitoring_api_server.py"
    sleep 2
fi

# Проверяем зависимости
echo "🔍 Проверка зависимостей..."

if ! python3 -c "import psutil" 2>/dev/null; then
    echo "📦 Установка psutil..."
    pip3 install psutil
fi

if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Установка Flask..."
    pip3 install flask flask-cors
fi

# Запускаем сервер
echo "🚀 Запуск Monitoring API Server на порту 5006..."
echo "📊 Dashboard: http://localhost:5006/api/monitoring/dashboard"
echo "🔧 Health check: http://localhost:5006/api/monitoring/health"
echo "🛑 Для остановки нажмите Ctrl+C"
echo ""

python3 monitoring_api_server.py