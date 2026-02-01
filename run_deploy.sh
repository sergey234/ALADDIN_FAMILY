#!/bin/bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Проверяем sshpass
if command -v sshpass &> /dev/null; then
    echo "✅ Используем sshpass"
    sshpass -p 'Sergio675' scp -o StrictHostKeyChecking=no api_gateway_complete.py root@149.154.65.180:/opt/aladdin-backend/
    sshpass -p 'Sergio675' scp -o StrictHostKeyChecking=no sfm_adapter.py root@149.154.65.180:/opt/aladdin-backend/
    sshpass -p 'Sergio675' ssh -o StrictHostKeyChecking=no root@149.154.65.180 "cd /opt/aladdin-backend && cp api_gateway.py api_gateway_backup_\$(date +%Y%m%d_%H%M%S).py 2>/dev/null && python3 -m py_compile api_gateway_complete.py && cp api_gateway_complete.py api_gateway.py && systemctl restart aladdin-api-gateway 2>/dev/null || systemctl restart aladdin-main-api-gateway 2>/dev/null && sleep 10 && curl -s http://127.0.0.1:8002/api/health"
else
    echo "⚠️ sshpass не найден, используем expect"
    chmod +x deploy_api_gateway_final.exp
    ./deploy_api_gateway_final.exp
fi



