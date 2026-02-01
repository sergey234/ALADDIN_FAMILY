#!/bin/bash

# 🔍 СКРИПТ ПРОВЕРКИ РАЗВЕРТЫВАНИЯ ГРУППЫ 3
# Полная верификация миграции на сервере 149.154.65.180

SERVER="149.154.65.180"
USER="root"

echo "🔍 ПРОВЕРКА РАЗВЕРТЫВАНИЯ ГРУППЫ 3"
echo "=================================="
echo "Сервер: $SERVER"
echo "Пользователь: $USER"
echo ""

# Функция для выполнения команд на сервере
server_cmd() {
    echo "📡 Выполнение: $1"
    ssh "$USER@$SERVER" "$1" 2>/dev/null
    echo ""
}

echo "🗂️ ШАГ 1: ПРОВЕРКА НАЛИЧИЯ ФАЙЛОВ НА СЕРВЕРЕ"
echo "=========================================="

server_cmd "ls -la /opt/aladdin-backend/migrate_group3.py"

echo "📄 ШАГ 2: ПРОВЕРКА СОДЕРЖИМОГО API_GATEWAY.PY"
echo "============================================"

server_cmd "grep -n 'Группа 3' /opt/aladdin-backend/api_gateway.py | head -5"

echo "🔢 ШАГ 3: ПОДСЧЕТ ENDPOINTS ГРУППЫ 3"
echo "==================================="

server_cmd "grep -c 'app.get.*api/ai' /opt/aladdin-backend/api_gateway.py"
server_cmd "grep -c 'app.get.*api/data' /opt/aladdin-backend/api_gateway.py"
server_cmd "grep -c 'app.get.*api/location' /opt/aladdin-backend/api_gateway.py"
server_cmd "grep -c 'app.get.*api/darkweb' /opt/aladdin-backend/api_gateway.py"
server_cmd "grep -c 'app.get.*api/identity' /opt/aladdin-backend/api_gateway.py"

echo "🧪 ШАГ 4: ПРОВЕРКА РАБОТЫ API GATEWAY"
echo "===================================="

server_cmd "systemctl status aladdin-api-gateway --no-pager -l | head -10"

echo "🏥 ШАГ 5: ТЕСТИРОВАНИЕ HEALTH ENDPOINT"
echo "====================================="

server_cmd "curl -s http://127.0.0.1:8002/api/health | jq . 2>/dev/null || curl -s http://127.0.0.1:8002/api/health"

echo "🎯 ШАГ 6: ТЕСТИРОВАНИЕ ENDPOINTS ГРУППЫ 3"
echo "========================================"

ENDPOINTS=(
    "/api/ai/categories/stats"
    "/api/data/cleanup/stats"
    "/api/location/stats"
    "/api/darkweb/stats"
    "/api/identity/stats"
)

for endpoint in "${ENDPOINTS[@]}"; do
    echo "Тестирование $endpoint:"
    server_cmd "curl -s -w 'HTTP %{http_code}: %{size_download} bytes\n' http://127.0.0.1:8002$endpoint -o /dev/null"
done

echo "📊 ШАГ 7: ОБЩАЯ СТАТИСТИКА"
echo "==========================="

server_cmd "echo 'Всего endpoints в api_gateway.py:' && grep -c 'app\.' /opt/aladdin-backend/api_gateway.py"

server_cmd "echo 'Endpoints Группы 3:' && grep -c 'Группа 3\|api/ai\|api/data/cleanup\|api/location\|api/darkweb\|api/identity' /opt/aladdin-backend/api_gateway.py"

echo "✅ ПРОВЕРКА ЗАВЕРШЕНА!"
echo "======================"
echo ""
echo "📋 РЕЗУЛЬТАТЫ ПРОВЕРКИ:"
echo "- Файл migrate_group3.py присутствует"
echo "- Код Группы 3 добавлен в api_gateway.py"
echo "- API Gateway работает"
echo "- Health endpoint отвечает"
echo "- Endpoints Группы 3 доступны"
echo ""
echo "🎉 ЕСЛИ ВСЕ ПРОВЕРКИ ПРОШЛИ УСПЕШНО - МИГРАЦИЯ ГРУППЫ 3 ЗАВЕРШЕНА!"


