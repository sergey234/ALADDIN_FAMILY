#!/bin/bash
# 🚀 НЕМЕДЛЕННОЕ РАЗВЕРТЫВАНИЕ API GATEWAY

set -e

SERVER="149.154.65.180"
USER="root"
PASSWORD="Sergio675"
REMOTE_PATH="/opt/aladdin-backend"
LOCAL_PATH="/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS"

echo "=========================================="
echo "🚀 РАЗВЕРТЫВАНИЕ API GATEWAY"
echo "=========================================="
echo ""

# Функция для выполнения команд через expect
run_ssh() {
    /usr/bin/expect <<EOF
set timeout 30
spawn ssh -o StrictHostKeyChecking=no $USER@$SERVER "$1"
expect {
    "password:" {
        send "$PASSWORD\r"
        exp_continue
    }
    eof
}
wait
EOF
}

run_scp() {
    /usr/bin/expect <<EOF
set timeout 60
spawn scp -o StrictHostKeyChecking=no "$1" $USER@$SERVER:"$2"
expect {
    "password:" {
        send "$PASSWORD\r"
        exp_continue
    }
    eof
}
wait
EOF
}

# ШАГ 1: Backup
echo "💾 ШАГ 1: Создание backup..."
run_ssh "cd $REMOTE_PATH && cp api_gateway.py api_gateway_backup_\$(date +%Y%m%d_%H%M%S).py 2>/dev/null && echo '✅ Backup создан' || echo '⚠️ Первый деплой'"

# ШАГ 2: Загрузка файлов
echo ""
echo "📤 ШАГ 2: Загрузка api_gateway_complete.py..."
run_scp "$LOCAL_PATH/api_gateway_complete.py" "$REMOTE_PATH/"

echo ""
echo "📤 ШАГ 3: Загрузка sfm_adapter.py..."
run_scp "$LOCAL_PATH/sfm_adapter.py" "$REMOTE_PATH/"

# ШАГ 3: Замена и перезапуск
echo ""
echo "🔄 ШАГ 4: Замена API Gateway и перезапуск..."
run_ssh "cd $REMOTE_PATH && cp api_gateway_complete.py api_gateway.py && python3 -m py_compile api_gateway.py && echo '✅ Синтаксис OK' && systemctl restart aladdin-api-gateway 2>/dev/null || systemctl restart aladdin-main-api-gateway 2>/dev/null && echo '✅ Сервис перезапущен'"

# ШАГ 4: Тестирование
echo ""
echo "🧪 ШАГ 5: Тестирование..."
sleep 3
run_ssh "curl -s http://127.0.0.1:8002/api/health | python3 -m json.tool 2>/dev/null || curl -s http://127.0.0.1:8002/api/health"

echo ""
echo "=========================================="
echo "✅ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
echo "=========================================="



