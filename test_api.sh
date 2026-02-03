#!/bin/bash

echo "🧪 ПРОСТОЙ ТЕСТ API ALADDIN"
echo "==========================="

# Тест корневого эндпоинта
echo "🔍 Тестируем GET /"
response=$(curl -s -w "HTTP:%{http_code};TIME:%{time_total}" "http://149.154.65.180:8002/" 2>/dev/null)
status=$(echo "$response" | grep -o "HTTP:[0-9]*" | cut -d: -f2)
time=$(echo "$response" | grep -o "TIME:[0-9.]*" | cut -d: -f2)
body=$(echo "$response" | sed 's/HTTP.*//')

echo "📊 Результат:"
echo "   HTTP: $status"
echo "   Время: ${time}s"
echo "   Ответ: $body"

if [ "$status" = "200" ]; then
    echo "✅ API РАБОТАЕТ!"
else
    echo "❌ API НЕ РАБОТАЕТ"
fi
