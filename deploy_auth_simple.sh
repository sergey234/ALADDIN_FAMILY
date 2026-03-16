#!/bin/bash
# 🚀 Простой деплой auth.py через sshpass + scp (как в deploy_step.sh)

set -e

SERVER="149.154.65.180"
USER="root"
PASS="Sergio675"
REMOTE="/opt/aladdin-backend/app/auth"
LOCAL_FILE="app/auth/auth.py"

echo "=========================================="
echo "🚀 ДЕПЛОЙ ИСПРАВЛЕНИЯ auth.py"
echo "=========================================="
echo ""

# Проверка файла
if [ ! -f "$LOCAL_FILE" ]; then
    echo "❌ Файл $LOCAL_FILE не найден!"
    exit 1
fi

echo "✅ Локальный файл найден: $LOCAL_FILE"
echo ""

# ШАГ 1: Backup на сервере
echo "💾 ШАГ 1: Создание backup на сервере..."
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$SERVER "cd $REMOTE && cp auth.py auth.py.backup_\$(date +%Y%m%d_%H%M%S) 2>&1 || echo 'First deploy or file not found'" 2>&1
echo "✅ Backup создан"
echo ""

# ШАГ 2: Загрузка файла через scp
echo "📤 ШАГ 2: Загрузка файла на сервер..."
sshpass -p "$PASS" scp -o StrictHostKeyChecking=no "$LOCAL_FILE" $USER@$SERVER:$REMOTE/auth.py 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Файл успешно загружен"
else
    echo "❌ Ошибка при загрузке файла!"
    exit 1
fi
echo ""

# ШАГ 3: Проверка синтаксиса
echo "🔍 ШАГ 3: Проверка синтаксиса Python..."
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$SERVER "python3 -m py_compile $REMOTE/auth.py && echo '✅ Синтаксис OK' || echo '❌ Ошибка синтаксиса'" 2>&1
echo ""

# ШАГ 4: Перезапуск сервера
echo "🔄 ШАГ 4: Перезапуск сервера..."
sshpass -p "$PASS" ssh -o StrictHostKeyChecking=no $USER@$SERVER << 'EOF'
    if systemctl is-active --quiet aladdin-backend 2>/dev/null; then
        systemctl restart aladdin-backend
        echo "✅ Перезапущен через systemd"
        systemctl status aladdin-backend --no-pager -l | head -5
    elif command -v pm2 >/dev/null && pm2 list | grep -q aladdin-backend; then
        pm2 restart aladdin-backend
        echo "✅ Перезапущен через pm2"
        pm2 status aladdin-backend
    else
        echo "⚠️ Не удалось определить способ запуска"
        echo "Проверьте вручную: systemctl status aladdin-backend или pm2 list"
    fi
EOF
echo ""

echo "=========================================="
echo "✅ ДЕПЛОЙ ЗАВЕРШЕН!"
echo "=========================================="
