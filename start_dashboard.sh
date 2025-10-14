#!/bin/bash
# Скрипт запуска дашборда ALADDIN

echo "🚀 Запуск ALADDIN Security Dashboard..."
cd /Users/sergejhlystov/ALADDIN_NEW

# Убиваем старые процессы
pkill -f dashboard_server.py 2>/dev/null

# Запускаем дашборд
python3 dashboard_server.py &
DASHBOARD_PID=$!

echo "📊 Дашборд запущен с PID: $DASHBOARD_PID"
echo "🌐 Доступен по адресу: http://localhost:5000"
echo "🔧 API: http://localhost:5000/api/"

# Ждем запуска
sleep 3

# Проверяем статус
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo "✅ Дашборд работает!"
else
    echo "❌ Дашборд не отвечает"
fi

echo "🛑 Для остановки выполните: pkill -f dashboard_server.py"