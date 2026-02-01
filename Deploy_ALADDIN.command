#!/bin/bash
# Файл .command для macOS - можно запустить двойным кликом

cd "$(dirname "$0")"

echo "=========================================="
echo "🚀 РАЗВЕРТЫВАНИЕ ALADDIN API GATEWAY"
echo "=========================================="
echo ""

SERVER="149.154.65.180"
USER="root"
PASSWORD="Sergio675"
REMOTE_PATH="/opt/aladdin-backend"

# Функция для выполнения команд
deploy_with_sshpass() {
    echo "📤 Загрузка api_gateway_complete.py..."
    sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no api_gateway_complete.py "$USER@$SERVER:$REMOTE_PATH/" || return 1
    
    echo "📤 Загрузка sfm_adapter.py..."
    sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no sfm_adapter.py "$USER@$SERVER:$REMOTE_PATH/" || return 1
    
    echo "🔄 Развертывание на сервере..."
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USER@$SERVER" << 'DEPLOY_SCRIPT'
cd /opt/aladdin-backend
cp api_gateway.py api_gateway_backup_$(date +%Y%m%d_%H%M%S).py 2>/dev/null && echo "✅ Backup создан" || echo "⚠️ Первый деплой"
python3 -m py_compile api_gateway_complete.py && echo "✅ Синтаксис OK" || exit 1
cp api_gateway_complete.py api_gateway.py && echo "✅ API Gateway заменен"
systemctl restart aladdin-api-gateway 2>/dev/null || systemctl restart aladdin-main-api-gateway 2>/dev/null || echo "⚠️ Сервис не найден"
sleep 10
echo "🧪 Тестирование health endpoint..."
curl -s http://127.0.0.1:8002/api/health | python3 -m json.tool 2>/dev/null || curl -s http://127.0.0.1:8002/api/health
DEPLOY_SCRIPT
}

# Проверяем sshpass
if command -v sshpass &> /dev/null; then
    deploy_with_sshpass
elif [ -f "deploy_api_gateway_final.exp" ]; then
    echo "📋 Используем expect скрипт..."
    chmod +x deploy_api_gateway_final.exp
    ./deploy_api_gateway_final.exp
else
    echo "❌ sshpass не найден и expect скрипт недоступен"
    echo ""
    echo "📝 Выполните команды вручную:"
    echo "   scp api_gateway_complete.py root@149.154.65.180:/opt/aladdin-backend/"
    echo "   scp sfm_adapter.py root@149.154.65.180:/opt/aladdin-backend/"
    echo "   ssh root@149.154.65.180"
    echo "   (затем выполните команды из COMMANDS_TO_RUN.txt)"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
echo "=========================================="
echo ""
echo "📝 Проверьте:"
echo "   curl http://149.154.65.180/api/health"
echo "   curl https://aladdin-ai.ru/api/health"
echo ""
echo "Нажмите любую клавишу для закрытия..."
read -n 1



