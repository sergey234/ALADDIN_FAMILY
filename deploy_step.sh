#!/bin/bash
# Скрипт пошагового развертывания с логированием
LOG="/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/deploy_process.log"
SERVER="149.154.65.180"
USER="root"
PASS="Sergio675"
REMOTE="/opt/aladdin-backend"
LOCAL="/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS"

echo "=== НАЧАЛО РАЗВЕРТЫВАНИЯ $(date) ===" > $LOG

# Проверка соединения
echo "🔍 Шаг 0: Проверка связи с сервером..." >> $LOG
ping -c 1 $SERVER >> $LOG 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Сервер доступен" >> $LOG
else
    echo "❌ Сервер недоступен" >> $LOG
    exit 1
fi

# Загрузка файлов
echo "📤 Шаг 1: Загрузка api_gateway_complete.py..." >> $LOG
sshpass -p "$PASS" scp -o StrictHostKeyChecking=no "$LOCAL/api_gateway_complete.py" $USER@$SERVER:$REMOTE/ >> $LOG 2>&1
if [ $? -eq 0 ]; then
    echo "✅ api_gateway_complete.py загружен" >> $LOG
else
    echo "❌ Ошибка загрузки api_gateway_complete.py" >> $LOG
fi

echo "📤 Шаг 2: Загрузка sfm_adapter.py..." >> $LOG
sshpass -p "$PASS" scp -o StrictHostKeyChecking=no "$LOCAL/sfm_adapter.py" $USER@$SERVER:$REMOTE/ >> $LOG 2>&1
if [ $? -eq 0 ]; then
    echo "✅ sfm_adapter.py загружен" >> $LOG
else
    echo "❌ Ошибка загрузки sfm_adapter.py" >> $LOG
fi

# Выполнение команд на сервере
echo "🔄 Шаг 3: Настройка и перезапуск на сервере..." >> $LOG
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$SERVER << EOF >> $LOG 2>&1
cd $REMOTE
# Backup
cp api_gateway.py api_gateway_backup_\$(date +%Y%m%d_%H%M%S).py 2>/dev/null
# Замена
cp api_gateway_complete.py api_gateway.py
# Проверка
python3 -m py_compile api_gateway.py
# Перезапуск
systemctl restart aladdin-api-gateway || systemctl restart aladdin-main-api-gateway
echo "--- Статус сервиса ---"
systemctl status aladdin-api-gateway --no-pager | head -n 5 || systemctl status aladdin-main-api-gateway --no-pager | head -n 5
EOF

echo "🧪 Шаг 4: Тест Health Endpoint..." >> $LOG
sleep 5
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$SERVER "curl -s http://127.0.0.1:8002/api/health" >> $LOG 2>&1

echo "=== ЗАВЕРШЕНО $(date) ===" >> $LOG



