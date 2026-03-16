#!/bin/bash
# Скрипт деплоя auth.py (как в deploy_step.sh)

SERVER="149.154.65.180"
USER="root"
PASS="Sergio675"
REMOTE="/opt/aladdin-backend/app/auth"
LOCAL_FILE="app/auth/auth.py"

echo "📤 Шаг 1: Загрузка auth.py..."
sshpass -p "$PASS" scp -o StrictHostKeyChecking=no "$LOCAL_FILE" $USER@$SERVER:$REMOTE/auth.py
if [ $? -eq 0 ]; then
    echo "✅ auth.py загружен"
else
    echo "❌ Ошибка загрузки auth.py"
    exit 1
fi

echo "🔄 Шаг 2: Настройка и перезапуск на сервере..."
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$SERVER << EOF
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

echo "✅ Деплой завершен!"
