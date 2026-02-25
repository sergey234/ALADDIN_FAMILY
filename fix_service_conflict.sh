#!/bin/bash

# Параметры сервера
SERVER_IP="149.154.65.180"
SERVER_USER="root"
SERVER_PASSWORD="Sergio675"

echo "🧹 УСТРАНЕНИЕ КОНФЛИКТА СЕРВИСОВ И ЗАПУСК НОВОГО API GATEWAY"
echo "======================================================"

# Проверка sshpass
if ! command -v sshpass &> /dev/null; then
    echo "❌ sshpass не найден! Установите его."
    exit 1
fi

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'EOF'

echo "🛑 Остановка старых конфликтующих сервисов..."
systemctl stop aladdin-api-gateway.service
systemctl disable aladdin-api-gateway.service
echo "✅ aladdin-api-gateway.service остановлен"

systemctl stop aladdin-production-api.service
systemctl disable aladdin-production-api.service
echo "✅ aladdin-production-api.service остановлен"

# Убиваем любые процессы на порту 8002 (на всякий случай)
fuser -k 8002/tcp 2>/dev/null || true

echo "🔄 Перезапуск основного сервиса (aladdin-main-api-gateway)..."
systemctl restart aladdin-main-api-gateway
sleep 5

# Проверка статуса
STATUS=$(systemctl is-active aladdin-main-api-gateway)
if [ "$STATUS" = "active" ]; then
    echo "✅ aladdin-main-api-gateway УСПЕШНО ЗАПУЩЕН!"
    systemctl status aladdin-main-api-gateway --no-pager | head -n 10
else
    echo "❌ ОШИБКА: Сервис не запустился. Логи:"
    journalctl -u aladdin-main-api-gateway -n 20 --no-pager
    exit 1
fi

EOF

echo ""
echo "🧪 ПОВТОРНОЕ ТЕСТИРОВАНИЕ JWT..."
python3 test_jwt_flow.py

echo ""
echo "🎯 ФИНАЛЬНЫЙ РЕЗУЛЬТАТ: JWT ДОЛЖЕН РАБОТАТЬ!"