#!/bin/bash
# Ручной деплой Location Bubble Agent
# Использование: ./deploy_location_bubble_manual.sh
# Пароль будет запрошен интерактивно

set -e

SERVER="root@149.154.65.180"
PASSWORD_PROMPT="Введите пароль для $SERVER (или нажмите Enter для использования 'Sergio675'): "

echo "=== ДЕПЛОЙ LOCATION BUBBLE AGENT ==="
echo ""

# Запрос пароля (опционально)
read -p "$PASSWORD_PROMPT" PASSWORD
if [ -z "$PASSWORD" ]; then
    PASSWORD="Sergio675"
fi

echo ""
echo "1. Копирование location_bubble_agent.py..."
scp security/ai_agents/location_bubble_agent.py \
    $SERVER:/opt/aladdin-backend/security/ai_agents/

echo "2. Копирование location_bubble_router.py..."
scp security/api/routers/location_bubble_router.py \
    $SERVER:/opt/aladdin-backend/security/api/routers/

echo "3. Копирование function_registry_entry_location_bubble.json..."
scp security/ai_agents/function_registry_entry_location_bubble.json \
    $SERVER:/tmp/

echo "4. Копирование скриптов регистрации..."
scp register_location_bubble_in_sfm.py add_location_bubble_to_main.py \
    $SERVER:/tmp/

echo ""
echo "✅ Все файлы скопированы на сервер!"
echo ""
echo "=== СЛЕДУЮЩИЕ ШАГИ ==="
echo ""
echo "Выполните на сервере:"
echo ""
echo "ssh $SERVER"
echo "cd /tmp"
echo "python3 register_location_bubble_in_sfm.py"
echo "python3 add_location_bubble_to_main.py"
echo "systemctl restart aladdin-backend"
echo "curl http://localhost:8000/api/location/bubble/health"
echo ""
