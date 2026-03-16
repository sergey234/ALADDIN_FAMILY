#!/bin/bash
# 🚀 Деплой auth.py через expect

set -e

SERVER="149.154.65.180"
USER="root"
PASSWORD="Sergio675"
REMOTE_PATH="/opt/aladdin-backend/app/auth"
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

# ШАГ 1: Backup
echo "💾 ШАГ 1: Создание backup..."
BACKUP_SUFFIX=$(date +%Y%m%d_%H%M%S)
/usr/bin/expect <<EXPECT_SCRIPT
set timeout 60
set server "149.154.65.180"
set user "root"
set password "Sergio675"
set remote_path "/opt/aladdin-backend/app/auth"
set backup_suffix "$BACKUP_SUFFIX"

spawn ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 \$user@\$server "cd \$remote_path && cp auth.py auth.py.backup_\$backup_suffix 2>&1 || echo 'File not found or first deploy'"
expect {
    "password:" { send "\$password\r"; exp_continue }
    "yes/no" { send "yes\r"; exp_continue }
    eof
}
wait
EXPECT_SCRIPT
echo ""

# ШАГ 2: Загрузка файла
echo "📤 ШАГ 2: Загрузка файла на сервер..."
/usr/bin/expect <<EXPECT_SCRIPT
set timeout 120
set server "149.154.65.180"
set user "root"
set password "Sergio675"
set local_file "$LOCAL_FILE"
set remote_file "/opt/aladdin-backend/app/auth/auth.py"

spawn scp -o StrictHostKeyChecking=no -o ConnectTimeout=30 "$local_file" $user@$server:$remote_file
expect {
    "password:" { send "$password\r"; exp_continue }
    "yes/no" { send "yes\r"; exp_continue }
    eof
}
wait
EXPECT_SCRIPT
echo "✅ Файл загружен"
echo ""

# ШАГ 3: Проверка синтаксиса
echo "🔍 ШАГ 3: Проверка синтаксиса Python..."
/usr/bin/expect <<'EXPECT_SCRIPT'
set timeout 60
set server "149.154.65.180"
set user "root"
set password "Sergio675"
set remote_path "/opt/aladdin-backend/app/auth"

spawn ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 $user@$server "python3 -m py_compile $remote_path/auth.py && echo 'Syntax OK' || echo 'Syntax Error'"
expect {
    "password:" { send "$password\r"; exp_continue }
    "yes/no" { send "yes\r"; exp_continue }
    eof
}
wait
EXPECT_SCRIPT
echo ""

# ШАГ 4: Перезапуск сервера
echo "🔄 ШАГ 4: Перезапуск сервера..."
/usr/bin/expect <<'EXPECT_SCRIPT'
set timeout 60
set server "149.154.65.180"
set user "root"
set password "Sergio675"

spawn ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 $user@$server "systemctl restart aladdin-backend 2>/dev/null && echo 'Restarted via systemd' || (pm2 restart aladdin-backend 2>/dev/null && echo 'Restarted via pm2' || echo 'Could not restart')"
expect {
    "password:" { send "$password\r"; exp_continue }
    "yes/no" { send "yes\r"; exp_continue }
    eof
}
wait
EXPECT_SCRIPT
echo ""

echo "=========================================="
echo "✅ ДЕПЛОЙ ЗАВЕРШЕН!"
echo "=========================================="
