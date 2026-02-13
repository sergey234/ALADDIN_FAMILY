#!/bin/bash
# Скрипт для перезапуска API Gateway сервера на 149.154.65.180

set -e

SERVER="root@149.154.65.180"
PASSWORD="Sergio675"
SERVICE_NAME="aladdin-api-gateway"
API_GATEWAY_PATH="/opt/aladdin-backend/security/microservices/api_gateway.py"

echo "🔄 Перезапуск API Gateway сервера..."

expect << EOF
set timeout 30
spawn ssh $SERVER "systemctl status $SERVICE_NAME 2>/dev/null || echo 'Service not found'"
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    eof
}
EOF

echo ""
echo "📋 Проверяю текущий процесс..."
expect << EOF
set timeout 30
spawn ssh $SERVER "ps aux | grep -E 'api_gateway|uvicorn' | grep -v grep || echo 'No process found'"
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    eof
}
EOF

echo ""
echo "🛑 Останавливаю сервер..."
expect << EOF
set timeout 30
spawn ssh $SERVER "pkill -f 'api_gateway.py' || pkill -f 'uvicorn.*api_gateway' || echo 'No process to kill'"
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    eof
}
EOF

sleep 2

echo ""
echo "✅ Проверяю синтаксис перед запуском..."
expect << EOF
set timeout 30
spawn ssh $SERVER "python3 -m py_compile $API_GATEWAY_PATH && echo '✅ Syntax OK' || echo '❌ Syntax Error'"
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    eof
}
EOF

echo ""
echo "🚀 Запускаю сервер..."
expect << EOF
set timeout 30
spawn ssh $SERVER "cd /opt/aladdin-backend/security/microservices && nohup python3 api_gateway.py > /var/log/aladdin-api-gateway.log 2>&1 &"
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    eof
}
EOF

sleep 3

echo ""
echo "✅ Проверяю что сервер запущен..."
expect << EOF
set timeout 30
spawn ssh $SERVER "ps aux | grep -E 'api_gateway|uvicorn' | grep -v grep && echo '✅ Server is running' || echo '❌ Server not running'"
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    eof
}
EOF

echo ""
echo "📊 Проверяю доступность API..."
expect << EOF
set timeout 30
spawn ssh $SERVER "curl -s http://localhost:8001/api/health | head -20 || echo 'API not responding'"
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    eof
}
EOF

echo ""
echo "✅ Перезапуск завершен!"
