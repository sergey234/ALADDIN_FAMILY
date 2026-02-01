#!/bin/bash
# 🚀 ПОЛНОЕ РАЗВЕРТЫВАНИЕ ALADDIN API GATEWAY

set -e

SERVER="149.154.65.180"
USER="root"
PASSWORD="Sergio675"
REMOTE_PATH="/opt/aladdin-backend"
LOCAL_PATH="/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS"

echo "=========================================="
echo "🚀 РАЗВЕРТЫВАНИЕ ALADDIN API GATEWAY"
echo "=========================================="
echo ""

# Функция для выполнения SSH команд
ssh_cmd() {
    /usr/bin/expect <<EOF
set timeout 60
spawn ssh -o StrictHostKeyChecking=no $USER@$SERVER "$1"
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    "yes/no" { send "yes\r"; exp_continue }
    eof
}
wait
EOF
}

# Функция для SCP
scp_file() {
    /usr/bin/expect <<EOF
set timeout 120
spawn scp -o StrictHostKeyChecking=no "$1" $USER@$SERVER:"$2"
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    "yes/no" { send "yes\r"; exp_continue }
    eof
}
wait
EOF
}

# ШАГ 1: Проверка файлов локально
echo "📋 ШАГ 1: Проверка локальных файлов..."
if [ ! -f "$LOCAL_PATH/api_gateway_complete.py" ]; then
    echo "❌ api_gateway_complete.py не найден!"
    exit 1
fi
if [ ! -f "$LOCAL_PATH/sfm_adapter.py" ]; then
    echo "❌ sfm_adapter.py не найден!"
    exit 1
fi
echo "✅ Все файлы найдены"
echo ""

# ШАГ 2: Создание backup
echo "💾 ШАГ 2: Создание backup на сервере..."
ssh_cmd "cd $REMOTE_PATH && if [ -f api_gateway.py ]; then cp api_gateway.py api_gateway_backup_\$(date +%Y%m%d_%H%M%S).py && echo '✅ Backup создан'; else echo '⚠️ Первый деплой'; fi"
echo ""

# ШАГ 3: Загрузка api_gateway_complete.py
echo "📤 ШАГ 3: Загрузка api_gateway_complete.py..."
scp_file "$LOCAL_PATH/api_gateway_complete.py" "$REMOTE_PATH/"
echo "✅ api_gateway_complete.py загружен"
echo ""

# ШАГ 4: Загрузка sfm_adapter.py
echo "📤 ШАГ 4: Загрузка sfm_adapter.py..."
scp_file "$LOCAL_PATH/sfm_adapter.py" "$REMOTE_PATH/"
echo "✅ sfm_adapter.py загружен"
echo ""

# ШАГ 5: Проверка синтаксиса
echo "🔍 ШАГ 5: Проверка синтаксиса Python..."
ssh_cmd "cd $REMOTE_PATH && python3 -m py_compile api_gateway_complete.py && echo '✅ Синтаксис OK'"
echo ""

# ШАГ 6: Замена api_gateway.py
echo "🔄 ШАГ 6: Замена api_gateway.py..."
ssh_cmd "cd $REMOTE_PATH && cp api_gateway_complete.py api_gateway.py && echo '✅ API Gateway заменен'"
echo ""

# ШАГ 7: Перезапуск сервиса
echo "🔄 ШАГ 7: Перезапуск сервиса..."
ssh_cmd "systemctl restart aladdin-api-gateway 2>/dev/null || systemctl restart aladdin-main-api-gateway 2>/dev/null || echo '⚠️ Сервис не найден'"
echo ""

# ШАГ 8: Ожидание запуска
echo "⏳ ШАГ 8: Ожидание запуска (10 сек)..."
sleep 10
echo ""

# ШАГ 9: Тест health endpoint
echo "🧪 ШАГ 9: Тест health endpoint..."
ssh_cmd "curl -s http://127.0.0.1:8002/api/health | python3 -m json.tool 2>/dev/null || curl -s http://127.0.0.1:8002/api/health"
echo ""

echo "=========================================="
echo "✅ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
echo "=========================================="
echo ""
echo "📝 Проверьте:"
echo "   curl http://$SERVER/api/health"
echo "   curl https://aladdin-ai.ru/api/health"
echo ""



