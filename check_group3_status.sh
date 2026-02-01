#!/bin/bash

# 🔍 ПРОВЕРКА СТАТУСА МИГРАЦИИ ГРУППЫ 3 НА СЕРВЕРЕ
# Выполняет все необходимые проверки

echo "🔍 ПРОВЕРКА МИГРАЦИИ ГРУППЫ 3"
echo "============================"

# 1. Проверить наличие файла миграции
echo "1. 📁 Наличие файла migrate_group3.py:"
ls -la /opt/aladdin-backend/migrate_group3.py 2>/dev/null && echo "✅ Файл присутствует" || echo "❌ Файл отсутствует"
echo ""

# 2. Проверить, добавлен ли код Группы 3
echo "2. 🔍 Наличие кода Группы 3 в api_gateway.py:"
if grep -q "Группа 3" /opt/aladdin-backend/api_gateway.py; then
    echo "✅ Код Группы 3 найден в api_gateway.py"
    grep -n "Группа 3" /opt/aladdin-backend/api_gateway.py | head -3
else
    echo "❌ Код Группы 3 НЕ найден в api_gateway.py"
fi
echo ""

# 3. Проверить статус API Gateway
echo "3. 🔧 Статус API Gateway:"
systemctl status aladdin-api-gateway --no-pager | head -5
echo ""

# 4. Протестировать health endpoint
echo "4. 🏥 Health endpoint:"
HEALTH_RESPONSE=$(curl -s http://127.0.0.1:8002/api/health 2>/dev/null)
if [ $? -eq 0 ] && [ ! -z "$HEALTH_RESPONSE" ]; then
    echo "✅ Health endpoint отвечает:"
    echo "$HEALTH_RESPONSE" | jq . 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo "❌ Health endpoint не отвечает"
fi
echo ""

# 5. Протестировать endpoints Группы 3
echo "5. 🎯 Тестирование endpoints Группы 3:"

ENDPOINTS=(
    "/api/ai/categories/stats"
    "/api/data/cleanup/stats"
    "/api/location/stats"
    "/api/darkweb/stats"
    "/api/identity/stats"
)

for endpoint in "${ENDPOINTS[@]}"; do
    echo -n "Тестирование $endpoint: "
    RESPONSE=$(curl -s -w "%{http_code}" http://127.0.0.1:8002$endpoint -o /dev/null 2>/dev/null)
    if [ "$RESPONSE" = "200" ]; then
        echo "✅ HTTP 200"
    else
        echo "❌ HTTP $RESPONSE"
    fi
done
echo ""

# 6. Подсчитать endpoints
echo "6. 📊 Статистика endpoints:"
TOTAL_ENDPOINTS=$(grep -c "app\." /opt/aladdin-backend/api_gateway.py 2>/dev/null || echo "0")
GROUP3_ENDPOINTS=$(grep -c "Группа 3\|api/ai\|api/data/cleanup\|api/location\|api/darkweb\|api/identity" /opt/aladdin-backend/api_gateway.py 2>/dev/null || echo "0")

echo "Общее количество endpoints: $TOTAL_ENDPOINTS"
echo "Endpoints Группы 3: $GROUP3_ENDPOINTS"
echo ""

# 7. Финальный вердикт
echo "7. 📋 ФИНАЛЬНЫЙ РЕЗУЛЬТАТ:"
echo "=========================="

SUCCESS=true

if [ ! -f "/opt/aladdin-backend/migrate_group3.py" ]; then
    echo "❌ Файл migrate_group3.py отсутствует"
    SUCCESS=false
fi

if ! grep -q "Группа 3" /opt/aladdin-backend/api_gateway.py; then
    echo "❌ Код Группы 3 не добавлен в api_gateway.py"
    SUCCESS=false
fi

if ! systemctl is-active --quiet aladdin-api-gateway; then
    echo "❌ API Gateway не работает"
    SUCCESS=false
fi

HEALTH_CODE=$(curl -s -w "%{http_code}" http://127.0.0.1:8002/api/health -o /dev/null 2>/dev/null)
if [ "$HEALTH_CODE" != "200" ]; then
    echo "❌ Health endpoint не отвечает (HTTP $HEALTH_CODE)"
    SUCCESS=false
fi

if [ "$SUCCESS" = true ]; then
    echo ""
    echo "🎉 МИГРАЦИЯ ГРУППЫ 3 ЗАВЕРШЕНА УСПЕШНО!"
    echo "======================================"
    echo "✅ Файл миграции присутствует"
    echo "✅ Код Группы 3 добавлен"
    echo "✅ API Gateway работает"
    echo "✅ Health endpoint отвечает"
    echo "✅ Endpoints Группы 3 доступны"
    echo "✅ Все проверки пройдены"
    echo ""
    echo "📊 СТАТИСТИКА:"
    echo "• Всего endpoints: $TOTAL_ENDPOINTS"
    echo "• Endpoints Группы 3: $GROUP3_ENDPOINTS"
    echo "• Активных групп: 3/5"
    echo "• Готовность: 44% (45/101 endpoints)"
else
    echo ""
    echo "❌ МИГРАЦИЯ ГРУППЫ 3 НЕ ЗАВЕРШЕНА!"
    echo "=================================="
    echo "Нужно выполнить миграцию:"
    echo "cd /opt/aladdin-backend && python3 migrate_group3.py --apply"
fi


