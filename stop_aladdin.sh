#!/bin/bash
# stop_aladdin.sh - Остановка ALADDIN системы

echo "🛑 Остановка ALADDIN Security System..."

# Остановка процессов
echo "🛑 Остановка дашборда..."
pkill -f dashboard_server.py

echo "🛑 Остановка поиска..."
pkill -f elasticsearch_api.py

echo "🛑 Остановка алертов..."
pkill -f alerts_api.py

# Ожидание завершения
sleep 2

# Проверка остановки
echo "🔍 Проверка остановки..."

if pgrep -f dashboard_server.py > /dev/null; then
    echo "⚠️  Дашборд: Все еще работает"
else
    echo "✅ Дашборд: Остановлен"
fi

if pgrep -f elasticsearch_api.py > /dev/null; then
    echo "⚠️  Поиск: Все еще работает"
else
    echo "✅ Поиск: Остановлен"
fi

if pgrep -f alerts_api.py > /dev/null; then
    echo "⚠️  Алерты: Все еще работают"
else
    echo "✅ Алерты: Остановлены"
fi

echo ""
echo "✅ ALADDIN Security System остановлена"
echo "🚀 Для запуска: ./start_aladdin.sh"