#!/bin/bash
# Прямое развертывание без expect - использует sshpass или интерактивный ввод

SERVER="149.154.65.180"
USER="root"
PASSWORD="Sergio675"
REMOTE_PATH="/opt/aladdin-backend"
LOCAL_PATH="/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS"

echo "=========================================="
echo "🚀 ПРЯМОЕ РАЗВЕРТЫВАНИЕ API GATEWAY"
echo "=========================================="
echo ""

# Проверка sshpass
if command -v sshpass &> /dev/null; then
    SCP_CMD="sshpass -p '$PASSWORD' scp"
    SSH_CMD="sshpass -p '$PASSWORD' ssh"
    echo "✅ Используется sshpass"
else
    SCP_CMD="scp"
    SSH_CMD="ssh"
    echo "⚠️  sshpass не найден, будет запрашиваться пароль"
fi

# ШАГ 1: Проверка файлов
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

# ШАГ 2: Загрузка файлов
echo "📤 ШАГ 2: Загрузка api_gateway_complete.py..."
$SCP_CMD -o StrictHostKeyChecking=no "$LOCAL_PATH/api_gateway_complete.py" "$USER@$SERVER:$REMOTE_PATH/" || {
    echo "❌ Ошибка загрузки api_gateway_complete.py"
    exit 1
}
echo "✅ api_gateway_complete.py загружен"
echo ""

echo "📤 ШАГ 3: Загрузка sfm_adapter.py..."
$SCP_CMD -o StrictHostKeyChecking=no "$LOCAL_PATH/sfm_adapter.py" "$USER@$SERVER:$REMOTE_PATH/" || {
    echo "❌ Ошибка загрузки sfm_adapter.py"
    exit 1
}
echo "✅ sfm_adapter.py загружен"
echo ""

# ШАГ 3: Развертывание на сервере
echo "🔄 ШАГ 4: Развертывание на сервере..."
$SSH_CMD -o StrictHostKeyChecking=no "$USER@$SERVER" << 'DEPLOY_SCRIPT'
cd /opt/aladdin-backend

# Backup
if [ -f api_gateway.py ]; then
    cp api_gateway.py api_gateway_backup_$(date +%Y%m%d_%H%M%S).py
    echo "✅ Backup создан"
else
    echo "⚠️ Первый деплой"
fi

# Проверка синтаксиса
python3 -m py_compile api_gateway_complete.py && echo "✅ Синтаксис OK" || {
    echo "❌ Ошибка синтаксиса!"
    exit 1
}

# Замена
cp api_gateway_complete.py api_gateway.py
echo "✅ API Gateway заменен"

# Перезапуск
systemctl restart aladdin-api-gateway 2>/dev/null || systemctl restart aladdin-main-api-gateway 2>/dev/null || echo "⚠️ Сервис не найден"
echo "✅ Сервис перезапущен"

# Ожидание
sleep 10

# Тест
echo "🧪 Тестирование health endpoint..."
curl -s http://127.0.0.1:8002/api/health | python3 -m json.tool 2>/dev/null || curl -s http://127.0.0.1:8002/api/health
DEPLOY_SCRIPT

echo ""
echo "=========================================="
echo "✅ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
echo "=========================================="
echo ""
echo "📝 Проверьте:"
echo "   curl http://$SERVER/api/health"
echo "   curl https://aladdin-ai.ru/api/health"
echo ""



