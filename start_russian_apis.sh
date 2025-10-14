#!/bin/bash

# Убиваем все предыдущие процессы russian_apis_server.py
pkill -f russian_apis_server.py

echo "🚀 Запуск Russian APIs Server..."

# Запускаем russian_apis_server.py в фоне
python3 russian_apis_server.py &
PID=$!
echo "📊 Russian APIs Server запущен с PID: $PID"
echo "🌐 Доступен по адресу: http://localhost:5005"
echo "🔧 API: http://localhost:5005/api/russian/"

# Ждем несколько секунд, чтобы сервер успел запуститься
sleep 5

# Проверяем статус сервера
HEALTH_CHECK=$(curl -s http://localhost:5005/api/russian/health)

if [ "$HEALTH_CHECK" == *"ok"* ]; then
    echo "✅ Russian APIs Server работает!"
    echo "📊 Статус: $(echo $HEALTH_CHECK | grep -o '"status":"[^"]*"')"
else
    echo "❌ Russian APIs Server не отвечает. Проверьте логи."
fi

echo "🛑 Для остановки выполните: pkill -f russian_apis_server.py"