#!/bin/bash
# РАБОЧИЙ ДЕПЛОЙ auth.py (на основе deploy_step.sh)

LOG="/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/deploy_auth_working.log"
SERVER="149.154.65.180"
USER="root"
PASS="Sergio675"
REMOTE="/opt/aladdin-backend/app/auth"
LOCAL_FILE="app/auth/auth.py"

echo "=== НАЧАЛО ДЕПЛОЯ auth.py $(date) ===" | tee -a $LOG

# Проверка соединения
echo "🔍 Шаг 0: Проверка связи с сервером..." | tee -a $LOG
ping -c 1 $SERVER >> $LOG 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Сервер доступен" | tee -a $LOG
else
    echo "❌ Сервер недоступен" | tee -a $LOG
    exit 1
fi

# Загрузка файла
echo "📤 Шаг 1: Загрузка auth.py..." | tee -a $LOG
sshpass -p "$PASS" scp -o StrictHostKeyChecking=no "$LOCAL_FILE" $USER@$SERVER:$REMOTE/auth.py >> $LOG 2>&1
if [ $? -eq 0 ]; then
    echo "✅ auth.py загружен" | tee -a $LOG
else
    echo "❌ Ошибка загрузки auth.py" | tee -a $LOG
    exit 1
fi

# Выполнение команд на сервере
echo "🔄 Шаг 2: Настройка и перезапуск на сервере..." | tee -a $LOG
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$SERVER << EOF >> $LOG 2>&1
cd $REMOTE
# Backup
cp auth.py auth.py.backup_\$(date +%Y%m%d_%H%M%S) 2>/dev/null
# Проверка
python3 -m py_compile auth.py
# Перезапуск
systemctl restart aladdin-backend || systemctl restart aladdin-main-api-gateway || pm2 restart aladdin-backend
echo "--- Статус сервиса ---"
systemctl status aladdin-backend --no-pager | head -n 5 || pm2 status aladdin-backend | head -n 5
EOF

echo "🧪 Шаг 3: Тест Health Endpoint..." | tee -a $LOG
sleep 5
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$SERVER "curl -s http://127.0.0.1:8002/api/health" >> $LOG 2>&1

echo "=== ЗАВЕРШЕНО $(date) ===" | tee -a $LOG
echo ""
echo "✅ ДЕПЛОЙ ЗАВЕРШЕН! Проверьте лог: $LOG" | tee -a $LOG