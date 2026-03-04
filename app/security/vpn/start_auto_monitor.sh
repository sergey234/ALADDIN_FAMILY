#!/bin/bash
# ALADDIN VPN - Auto Monitor Startup Script

echo "🚀 Starting ALADDIN VPN Auto Monitor..."

# Переходим в директорию VPN
cd /Users/sergejhlystov/ALADDIN_NEW/security/vpn

# Проверяем, не запущен ли уже монитор
if pgrep -f "auto_monitor.py" > /dev/null; then
    echo "⚠️  VPN Monitor is already running"
    echo "   To stop: pkill -f auto_monitor.py"
    exit 1
fi

# Запускаем монитор в фоне
nohup python3 auto_monitor.py > vpn_monitor.log 2>&1 &

# Получаем PID процесса
MONITOR_PID=$!

# Сохраняем PID в файл
echo $MONITOR_PID > vpn_monitor.pid

echo "✅ VPN Monitor started with PID: $MONITOR_PID"
echo "📝 Logs: vpn_monitor.log"
echo "🛑 To stop: ./stop_auto_monitor.sh or pkill -f auto_monitor.py"
echo ""
echo "📊 Monitor will:"
echo "   - Check every 60 seconds"
echo "   - Stop VPN servers if memory > 80%"
echo "   - Stop VPN servers if free memory < 1GB"
echo "   - Stop VPN servers after 30 minutes idle"
echo ""
echo "🔍 To check status: tail -f vpn_monitor.log"