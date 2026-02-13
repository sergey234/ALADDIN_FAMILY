#!/bin/bash

# 🔍 СКРИПТ ПРОВЕРКИ METRICS ROUTER НА СЕРВЕРЕ
# Дата: 2026-02-13
# Цель: Проверить и исправить подключение metrics_router

echo "=== ПРОВЕРКА METRICS ROUTER НА СЕРВЕРЕ ==="
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Проверка файла роутера
echo "1️⃣ Проверка файла роутера..."
if [ -f "/opt/aladdin-backend/security/api/routers/metrics_router.py" ]; then
    echo -e "${GREEN}✅ Файл metrics_router.py существует${NC}"
    echo "   Размер: $(ls -lh /opt/aladdin-backend/security/api/routers/metrics_router.py | awk '{print $5}')"
else
    echo -e "${RED}❌ Файл metrics_router.py НЕ найден!${NC}"
    exit 1
fi

# 2. Проверка префикса роутера
echo ""
echo "2️⃣ Проверка префикса роутера..."
PREFIX=$(grep -oP 'prefix=["\047]?[^"\047]*["\047]?' /opt/aladdin-backend/security/api/routers/metrics_router.py | head -1)
echo "   Префикс: $PREFIX"
if echo "$PREFIX" | grep -q "/metrics"; then
    echo -e "${GREEN}✅ Префикс правильный (/metrics)${NC}"
else
    echo -e "${YELLOW}⚠️ Префикс может быть неправильным${NC}"
fi

# 3. Проверка подключения в main.py
echo ""
echo "3️⃣ Проверка подключения в main.py..."
if grep -q "metrics_router" /opt/aladdin-backend/main.py; then
    echo -e "${GREEN}✅ metrics_router найден в main.py${NC}"
    echo ""
    echo "   Строки с metrics_router:"
    grep -n "metrics_router" /opt/aladdin-backend/main.py | head -10
else
    echo -e "${RED}❌ metrics_router НЕ найден в main.py!${NC}"
    exit 1
fi

# 4. Проверка независимости подключения
echo ""
echo "4️⃣ Проверка независимости подключения..."
if grep -A 5 "metrics_router_available" /opt/aladdin-backend/main.py | grep -q "if metrics_router_available:"; then
    echo -e "${GREEN}✅ Роутер подключен независимо${NC}"
else
    echo -e "${YELLOW}⚠️ Роутер может быть подключен условно (зависит от system_router)${NC}"
    echo "   Нужно проверить вручную!"
fi

# 5. Проверка статуса сервиса
echo ""
echo "5️⃣ Проверка статуса сервиса..."
if systemctl is-active --quiet aladdin-production-api; then
    echo -e "${GREEN}✅ Сервис aladdin-production-api активен${NC}"
    systemctl status aladdin-production-api --no-pager -l | head -10
else
    echo -e "${RED}❌ Сервис aladdin-production-api НЕ активен!${NC}"
    exit 1
fi

# 6. Проверка логов
echo ""
echo "6️⃣ Проверка логов (последние 20 строк с metrics)..."
journalctl -u aladdin-production-api -n 100 --no-pager | grep -i metrics | tail -20 || echo "   Нет записей о metrics в логах"

# 7. Тестирование endpoint
echo ""
echo "7️⃣ Тестирование endpoint..."
echo "   Отправка тестового запроса..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST https://aladdin-ai.ru/api/metrics/upload \
  -H "Content-Type: application/json" \
  -d '{"deviceId":"test_check","appVersion":"1.0.0","platform":"ios","metrics":[]}')

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Endpoint работает! HTTP $HTTP_CODE${NC}"
    echo "   Ответ: $BODY"
elif [ "$HTTP_CODE" = "404" ]; then
    echo -e "${RED}❌ Endpoint возвращает 404!${NC}"
    echo "   Ответ: $BODY"
    echo ""
    echo "   🔧 НУЖНО ИСПРАВИТЬ:"
    echo "   1. Проверить подключение роутера в main.py"
    echo "   2. Убедиться, что роутер подключен независимо"
    echo "   3. Перезапустить сервис"
else
    echo -e "${YELLOW}⚠️ Endpoint возвращает HTTP $HTTP_CODE${NC}"
    echo "   Ответ: $BODY"
fi

echo ""
echo "=== ПРОВЕРКА ЗАВЕРШЕНА ==="
