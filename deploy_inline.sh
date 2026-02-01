#!/bin/bash
# Развертывание с inline expect командами

cd "$(dirname "$0")"

SERVER="149.154.65.180"
USER="root"
PASSWORD="Sergio675"
REMOTE_PATH="/opt/aladdin-backend"

echo "=========================================="
echo "🚀 РАЗВЕРТЫВАНИЕ ALADDIN API GATEWAY"
echo "=========================================="
echo ""

# Загрузка api_gateway_complete.py
echo "📤 Загрузка api_gateway_complete.py..."
/usr/bin/expect <<EOF
set timeout 60
spawn scp -o StrictHostKeyChecking=no api_gateway_complete.py $USER@$SERVER:$REMOTE_PATH/
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    "yes/no" { send "yes\r"; exp_continue }
    eof
}
wait
EOF
echo "✅ api_gateway_complete.py загружен"
echo ""

# Загрузка sfm_adapter.py
echo "📤 Загрузка sfm_adapter.py..."
/usr/bin/expect <<EOF
set timeout 60
spawn scp -o StrictHostKeyChecking=no sfm_adapter.py $USER@$SERVER:$REMOTE_PATH/
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    eof
}
wait
EOF
echo "✅ sfm_adapter.py загружен"
echo ""

# Развертывание на сервере
echo "🔄 Развертывание на сервере..."
/usr/bin/expect <<EOF
set timeout 120
spawn ssh -o StrictHostKeyChecking=no $USER@$SERVER "cd $REMOTE_PATH && cp api_gateway.py api_gateway_backup_\$(date +%Y%m%d_%H%M%S).py 2>/dev/null && echo '✅ Backup создан' || echo '⚠️ Первый деплой' && python3 -m py_compile api_gateway_complete.py && echo '✅ Синтаксис OK' && cp api_gateway_complete.py api_gateway.py && echo '✅ API Gateway заменен' && systemctl restart aladdin-api-gateway 2>/dev/null || systemctl restart aladdin-main-api-gateway 2>/dev/null && sleep 10 && curl -s http://127.0.0.1:8002/api/health | python3 -m json.tool 2>/dev/null || curl -s http://127.0.0.1:8002/api/health"
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    "yes/no" { send "yes\r"; exp_continue }
    eof
}
wait
EOF

echo ""
echo "=========================================="
echo "✅ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
echo "=========================================="
echo ""
echo "📝 Проверьте:"
echo "   curl http://$SERVER/api/health"
echo "   curl https://aladdin-ai.ru/api/health"
echo ""



