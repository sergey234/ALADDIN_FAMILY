#!/bin/bash

# Параметры сервера
SERVER_IP="149.154.65.180"
SERVER_USER="root"
SERVER_PASSWORD="Sergio675"

echo "🛡️ ЗАГРУЗКА SECURITY ЗАВИСИМОСТЕЙ (PARENTAL CONTROL FIX)"
echo "======================================================"

# Проверка sshpass
if ! command -v sshpass &> /dev/null; then
    echo "❌ sshpass не найден! Установите его."
    exit 1
fi

echo "📤 ШАГ 1: Создание структуры директорий..."

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "mkdir -p /opt/aladdin-backend/security/family"

echo "📤 ШАГ 2: Отправка файлов..."

sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no security/family/parental_controls.py ${SERVER_USER}@${SERVER_IP}:/opt/aladdin-backend/security/family/
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no security/family/__init__.py ${SERVER_USER}@${SERVER_IP}:/opt/aladdin-backend/security/family/
sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no security/family/advanced_parental_controls.py ${SERVER_USER}@${SERVER_IP}:/opt/aladdin-backend/security/family/

if [ $? -ne 0 ]; then
    echo "❌ Ошибка отправки файлов"
    exit 1
fi

echo "✅ Файлы отправлены"

echo "🔄 ШАГ 3: Перезапуск сервиса..."

sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'EOF'
systemctl restart aladdin-main-api-gateway
sleep 5
systemctl status aladdin-main-api-gateway --no-pager | head -n 10
EOF

echo ""
echo "🧪 ШАГ 4: Тестирование Parental Control..."

python3 test_jwt_flow.py # Или отдельный тест

echo ""
echo "🎯 Parental Control должен заработать!"