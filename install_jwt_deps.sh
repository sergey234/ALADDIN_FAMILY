#!/bin/bash

# Параметры сервера
SERVER_IP="149.154.65.180"
SERVER_USER="root"
SERVER_PASSWORD="Sergio675"

echo "📦 УСТАНОВКА НЕДОСТАЮЩИХ JWT ЗАВИСИМОСТЕЙ"
echo "======================================================"

# Проверка sshpass
if ! command -v sshpass &> /dev/null; then
    echo "❌ sshpass не найден! Установите его."
    exit 1
fi

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'EOF'

echo "🔍 Проверка pip..."
/opt/aladdin-backend/venv/bin/pip list | grep jose

echo "📦 Установка python-jose и других..."
/opt/aladdin-backend/venv/bin/pip install "python-jose[cryptography]" "passlib[bcrypt]" "python-multipart" "email-validator" "aiosqlite"

if [ $? -eq 0 ]; then
    echo "✅ Зависимости успешно установлены"
else
    echo "❌ Ошибка установки зависимостей"
    exit 1
fi

echo "🔄 Перезапуск основного сервиса..."
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
echo "🧪 ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ JWT..."
python3 test_jwt_flow.py

echo ""
echo "🎯 РАБОТА ЗАВЕРШЕНА!"