#!/bin/bash
# ALADDIN VPN - Auto Monitor Stop Script

echo "🛑 Stopping ALADDIN VPN Auto Monitor..."

# Переходим в директорию VPN
cd /Users/sergejhlystov/ALADDIN_NEW/security/vpn

# Останавливаем монитор
if pgrep -f "auto_monitor.py" > /dev/null; then
    pkill -f "auto_monitor.py"
    echo "✅ VPN Monitor stopped"
    
    # Удаляем PID файл
    if [ -f "vpn_monitor.pid" ]; then
        rm vpn_monitor.pid
    fi
else
    echo "⚠️  VPN Monitor is not running"
fi

echo "📝 Last logs:"
tail -5 vpn_monitor.log 2>/dev/null || echo "No logs found"