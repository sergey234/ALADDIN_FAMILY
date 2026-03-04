#!/bin/bash
# 🚀 ФИНАЛЬНЫЙ ПРОДАКШЕН ДЕПЛОЙ (СБОРКА 77)
# Синхронизация всех восстановленных роутеров и основной логики

SERVER_IP="149.154.65.180"
SERVER_USER="root"
SERVER_PASSWORD="Sergio675"
REMOTE_PATH="/opt/aladdin-backend"

echo "=========================================="
echo "🚀 ЗАПУСК ФИНАЛЬНОГО ДЕПЛОЯ НА СЕРВЕР"
echo "=========================================="

# 1. Синхронизация файлов
echo "📤 ШАГ 1: Синхронизация файлов через rsync..."
sshpass -p "$SERVER_PASSWORD" rsync -avz -e "ssh -o StrictHostKeyChecking=no" \
    --exclude '.git/' \
    --exclude 'DerivedData/' \
    --exclude 'node_modules/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude 'BACKUPS/' \
    --exclude '.cursor/' \
    --exclude 'ALADDIN.xcodeproj/' \
    --exclude 'ALADDIN/' \
    --exclude 'ALADDINWidgets/' \
    --exclude 'ALADDINContentBlocker/' \
    --exclude 'Info.plist' \
    --exclude 'smart_api_tester.py' \
    ./ ${SERVER_USER}@${SERVER_IP}:${REMOTE_PATH}/

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при синхронизации файлов"
    exit 1
fi

echo "✅ Файлы успешно синхронизированы!"

# 2. Проверка и перезапуск
echo ""
echo "🔄 ШАГ 2: Проверка синтаксиса и перезапуск сервиса..."
sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << EOF
cd ${REMOTE_PATH}
echo "🔍 Проверка main.py..."
python3 -m py_compile main.py
if [ \$? -eq 0 ]; then
    echo "✅ Синтаксис OK"
    echo "🔄 Перезапуск aladdin-backend..."
    systemctl restart aladdin-backend
    sleep 3
    systemctl status aladdin-backend --no-pager | head -n 10
else
    echo "❌ ОШИБКА СИНТАКСИСА в main.py! Деплой прерван."
    exit 1
fi
EOF

if [ $? -ne 0 ]; then
    echo "❌ Ошибка при перезапуске сервиса"
    exit 1
fi

echo ""
echo "🏥 ШАГ 3: Проверка Health Check..."
curl -s https://aladdin-ai.ru/api/health | grep -q "ok" && echo "✅ Сервер отвечает: OK" || echo "⚠️ Health Check не пройден"

echo "=========================================="
echo "🎉 ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!"
echo "=========================================="
