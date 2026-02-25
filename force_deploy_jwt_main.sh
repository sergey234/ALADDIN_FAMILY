#!/bin/bash

# Параметры сервера
SERVER_IP="149.154.65.180"
SERVER_USER="root"
SERVER_PASSWORD="Sergio675"

echo "🚀 ЗАПУСК ПРИНУДИТЕЛЬНОГО ОБНОВЛЕНИЯ API GATEWAY (MAIN.PY FIX)"
echo "======================================================"

# Проверка sshpass
if ! command -v sshpass &> /dev/null; then
    echo "❌ sshpass не найден! Установите его."
    exit 1
fi

echo "📤 ШАГ 1: Отправка api_gateway_complete_full.py..."

sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no api_gateway_complete_full.py ${SERVER_USER}@${SERVER_IP}:/opt/aladdin-backend/api_gateway_complete_full_jwt.py

if [ $? -ne 0 ]; then
    echo "❌ Ошибка отправки файла"
    exit 1
fi

echo "✅ Файл отправлен как api_gateway_complete_full_jwt.py"

echo ""
echo "🔧 ШАГ 2: Замена MAIN.PY на сервере..."

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'EOF'
cd /opt/aladdin-backend

# Резервная копия main.py (КРИТИЧНО!)
cp main.py main.py.backup_jwt_fix.$(date +%Y%m%d_%H%M%S)

# Замена main.py на новый API Gateway
cp api_gateway_complete_full_jwt.py main.py
chmod +x main.py

# Также обновляем api_gateway.py для совместимости
cp api_gateway_complete_full_jwt.py api_gateway.py

# Проверка содержимого (греп должен найти register_device)
if grep -q "register_device" main.py; then
    echo "✅ main.py успешно обновлен (найдена функция register_device)"
else
    echo "❌ ОШИБКА: Файл main.py не содержит register_device! Что-то пошло не так."
    exit 1
fi

# Перезапуск сервиса
systemctl restart aladdin-main-api-gateway
sleep 5

# Проверка статуса
systemctl status aladdin-main-api-gateway --no-pager | head -n 5
EOF

echo ""
echo "🧪 ШАГ 3: Повторное тестирование JWT..."

python3 test_jwt_flow.py

echo ""
echo "🎯 ЗАВЕРШЕНО!"