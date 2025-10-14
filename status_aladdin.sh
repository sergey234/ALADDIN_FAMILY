#!/bin/bash
# status_aladdin.sh - Проверка статуса ALADDIN

echo "🔍 Статус ALADDIN Security System"
echo "=================================="

# Проверка процессов
echo "📊 Процессы:"

if pgrep -f dashboard_server.py > /dev/null; then
    DASHBOARD_PID=$(pgrep -f dashboard_server.py)
    echo "✅ Дашборд: Работает (PID: $DASHBOARD_PID)"
else
    echo "❌ Дашборд: Не работает"
fi

if pgrep -f elasticsearch_api.py > /dev/null; then
    SEARCH_PID=$(pgrep -f elasticsearch_api.py)
    echo "✅ Поиск: Работает (PID: $SEARCH_PID)"
else
    echo "❌ Поиск: Не работает"
fi

if pgrep -f alerts_api.py > /dev/null; then
    ALERTS_PID=$(pgrep -f alerts_api.py)
    echo "✅ Алерты: Работают (PID: $ALERTS_PID)"
else
    echo "❌ Алерты: Не работают"
fi

echo ""
echo "🌐 HTTP проверки:"

# Проверка дашборда
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "✅ Дашборд API: Отвечает (http://localhost:5000)"
else
    echo "❌ Дашборд API: Не отвечает"
fi

# Проверка поиска
if curl -s http://localhost:5001/api/health > /dev/null 2>&1; then
    echo "✅ Поиск API: Отвечает (http://localhost:5001)"
else
    echo "❌ Поиск API: Не отвечает"
fi

# Проверка алертов
if curl -s http://localhost:5003/api/alerts/health > /dev/null 2>&1; then
    echo "✅ Алерты API: Отвечают (http://localhost:5003)"
else
    echo "❌ Алерты API: Не отвечают"
fi

echo ""
echo "📈 Статистика:"

# Подсчет работающих сервисов
WORKING_SERVICES=0
if pgrep -f dashboard_server.py > /dev/null; then ((WORKING_SERVICES++)); fi
if pgrep -f elasticsearch_api.py > /dev/null; then ((WORKING_SERVICES++)); fi
if pgrep -f alerts_api.py > /dev/null; then ((WORKING_SERVICES++)); fi

echo "🟢 Работающих сервисов: $WORKING_SERVICES/3"

if [ $WORKING_SERVICES -eq 3 ]; then
    echo "🎉 Все сервисы работают!"
elif [ $WORKING_SERVICES -gt 0 ]; then
    echo "⚠️  Частично работает"
else
    echo "❌ Ни один сервис не работает"
fi

echo ""
echo "🔧 Команды:"
echo "   Запуск: ./start_aladdin.sh"
echo "   Остановка: ./stop_aladdin.sh"
echo "   Статус: ./status_aladdin.sh"