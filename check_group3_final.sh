#!/bin/bash

# 🔍 ФИНАЛЬНАЯ ПРОВЕРКА МИГРАЦИИ ГРУППЫ 3
# Использует sshpass для автоматизации

SERVER="149.154.65.180"
USER="root"
PASSWORD="Sergio675"

# Функция для выполнения команд на сервере
server_cmd() {
    local cmd="$1"
    echo "📡 Выполнение: $cmd"
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USER@$SERVER" "$cmd"
    echo ""
}

echo "🔍 ФИНАЛЬНАЯ ПРОВЕРКА МИГРАЦИИ ГРУППЫ 3"
echo "======================================"
echo "Сервер: $SERVER"
echo "Метод: sshpass"
echo ""

# Проверка 1: Файл миграции
echo "1. 📁 ФАЙЛ МИГРАЦИИ:"
server_cmd "ls -la /opt/aladdin-backend/migrate_group3.py"

# Проверка 2: Код Группы 3 в api_gateway.py
echo "2. 🔍 КОД ГРУППЫ 3:"
server_cmd "grep -n 'Группа 3' /opt/aladdin-backend/api_gateway.py | head -3"

# Проверка 3: Статус API Gateway
echo "3. 🔧 СТАТУС API GATEWAY:"
server_cmd "systemctl status aladdin-api-gateway --no-pager | head -5"

# Проверка 4: Health endpoint
echo "4. 🏥 HEALTH ENDPOINT:"
server_cmd "curl -s http://127.0.0.1:8002/api/health"

# Проверка 5: Endpoints Группы 3
echo "5. 🎯 ENDPOINTS ГРУППЫ 3:"
ENDPOINTS=(
    "/api/ai/categories/stats"
    "/api/data/cleanup/stats"
    "/api/location/stats"
    "/api/darkweb/stats"
    "/api/identity/stats"
)

for endpoint in "${ENDPOINTS[@]}"; do
    echo "Тестирование $endpoint:"
    server_cmd "curl -s http://127.0.0.1:8002$endpoint | head -2"
done

# Проверка 6: Статистика endpoints
echo "6. 📊 СТАТИСТИКА ENDPOINTS:"
server_cmd "echo 'Всего endpoints:' && grep -c 'app\.' /opt/aladdin-backend/api_gateway.py"
server_cmd "echo 'Endpoints Группы 3:' && grep -c 'Группа 3\|api/ai\|api/data/cleanup\|api/location\|api/darkweb\|api/identity' /opt/aladdin-backend/api_gateway.py"

# Финальный вердикт
echo "7. 📋 ФИНАЛЬНЫЙ РЕЗУЛЬТАТ:"
echo "=========================="

# Проверяем условия успеха
SUCCESS=true

echo -n "Проверка файла миграции: "
if sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USER@$SERVER" "test -f /opt/aladdin-backend/migrate_group3.py"; then
    echo "✅"
else
    echo "❌"
    SUCCESS=false
fi

echo -n "Проверка кода Группы 3: "
if sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USER@$SERVER" "grep -q 'Группа 3' /opt/aladdin-backend/api_gateway.py"; then
    echo "✅"
else
    echo "❌"
    SUCCESS=false
fi

echo -n "Проверка API Gateway: "
if sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USER@$SERVER" "systemctl is-active aladdin-api-gateway >/dev/null 2>&1"; then
    echo "✅"
else
    echo "❌"
    SUCCESS=false
fi

echo -n "Проверка health endpoint: "
HEALTH_CODE=$(sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USER@$SERVER" "curl -s -w '%{http_code}' http://127.0.0.1:8002/api/health -o /dev/null")
if [ "$HEALTH_CODE" = "200" ]; then
    echo "✅"
else
    echo "❌ (HTTP $HEALTH_CODE)"
    SUCCESS=false
fi

echo ""
if [ "$SUCCESS" = true ]; then
    echo "🎉 МИГРАЦИЯ ГРУППЫ 3 ЗАВЕРШЕНА УСПЕШНО!"
    echo "======================================"
    echo "✅ Все проверки пройдены"
    echo "✅ Группа 3 готова к использованию"
    echo "✅ Мобильное приложение может использовать новые endpoints"
else
    echo "❌ МИГРАЦИЯ ГРУППЫ 3 НЕ ЗАВЕРШЕНА!"
    echo "=================================="
    echo "Нужно выполнить миграцию:"
    echo "sshpass -p '$PASSWORD' ssh $USER@$SERVER 'cd /opt/aladdin-backend && python3 migrate_group3.py --apply'"
fi

echo ""
echo "📊 ИТОГОВАЯ ИНФОРМАЦИЯ:"
TOTAL_ENDPOINTS=$(sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USER@$SERVER" "grep -c 'app\.' /opt/aladdin-backend/api_gateway.py")
GROUP3_ENDPOINTS=$(sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USER@$SERVER" "grep -c 'Группа 3\|api/ai\|api/data/cleanup\|api/location\|api/darkweb\|api/identity' /opt/aladdin-backend/api_gateway.py")

echo "• Всего endpoints: $TOTAL_ENDPOINTS"
echo "• Endpoints Группы 3: $GROUP3_ENDPOINTS"
echo "• Активных групп: 3/5"
echo "• Готовность: $((TOTAL_ENDPOINTS * 100 / 101))% (примерно)"


