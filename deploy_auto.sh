#!/bin/bash
# Автоматическое развертывание - выбирает лучший метод

cd "$(dirname "$0")"

echo "=========================================="
echo "🚀 АВТОМАТИЧЕСКОЕ РАЗВЕРТЫВАНИЕ"
echo "=========================================="
echo ""

# Проверяем доступные инструменты
HAS_SSHPASS=false
HAS_EXPECT=false
HAS_PYTHON3=false

if command -v sshpass &> /dev/null; then
    HAS_SSHPASS=true
    echo "✅ sshpass доступен"
fi

if command -v expect &> /dev/null; then
    HAS_EXPECT=true
    echo "✅ expect доступен"
fi

if command -v python3 &> /dev/null; then
    HAS_PYTHON3=true
    echo "✅ python3 доступен"
fi

echo ""

# Выбираем метод
if [ "$HAS_SSHPASS" = true ]; then
    echo "📋 Используем метод: sshpass"
    echo ""
    SERVER="149.154.65.180"
    USER="root"
    PASSWORD="Sergio675"
    REMOTE_PATH="/opt/aladdin-backend"
    
    echo "📤 Загрузка файлов..."
    sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no api_gateway_complete.py "$USER@$SERVER:$REMOTE_PATH/" || exit 1
    sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no sfm_adapter.py "$USER@$SERVER:$REMOTE_PATH/" || exit 1
    echo "✅ Файлы загружены"
    echo ""
    
    echo "🔄 Развертывание на сервере..."
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USER@$SERVER" << 'EOF'
cd /opt/aladdin-backend
cp api_gateway.py api_gateway_backup_$(date +%Y%m%d_%H%M%S).py 2>/dev/null && echo '✅ Backup создан' || echo '⚠️ Первый деплой'
python3 -m py_compile api_gateway_complete.py && echo '✅ Синтаксис OK' || exit 1
cp api_gateway_complete.py api_gateway.py && echo '✅ API Gateway заменен'
systemctl restart aladdin-api-gateway 2>/dev/null || systemctl restart aladdin-main-api-gateway 2>/dev/null || echo '⚠️ Сервис не найден'
sleep 10
curl -s http://127.0.0.1:8002/api/health | python3 -m json.tool 2>/dev/null || curl -s http://127.0.0.1:8002/api/health
EOF
    
elif [ "$HAS_EXPECT" = true ]; then
    echo "📋 Используем метод: expect"
    echo ""
    chmod +x deploy_api_gateway_final.exp
    ./deploy_api_gateway_final.exp
    
elif [ "$HAS_PYTHON3" = true ]; then
    echo "📋 Используем метод: python3"
    echo ""
    python3 deploy_subprocess.py
    
else
    echo "❌ Не найдены необходимые инструменты (sshpass, expect или python3)"
    echo ""
    echo "📝 Выполните команды вручную из файла COMMANDS_TO_RUN.txt"
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



