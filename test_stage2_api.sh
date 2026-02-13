#!/bin/bash

# Скрипт для тестирования всех 33 endpoint'ов Этапа 2
# Использование: ./test_stage2_api.sh [BASE_URL]

BASE_URL="${1:-http://149.154.65.180:8000}"
USER_ID="user_123"
DEVICE_ID="device_123"
FAMILY_ID="family_123"
CHILD_ID="child_123"

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SUCCESS_COUNT=0
FAIL_COUNT=0

# Функция для тестирования GET запроса
test_get() {
    local url=$1
    local description=$2
    echo -n "Testing: $description... "
    
    response=$(curl -s -w "\n%{http_code}" "$url" 2>/dev/null)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "404" ]; then
        echo -e "${GREEN}✓${NC} (HTTP $http_code)"
        ((SUCCESS_COUNT++))
        return 0
    else
        echo -e "${RED}✗${NC} (HTTP $http_code)"
        ((FAIL_COUNT++))
        return 1
    fi
}

# Функция для тестирования POST запроса
test_post() {
    local url=$1
    local data=$2
    local description=$3
    echo -n "Testing: $description... "
    
    response=$(curl -s -w "\n%{http_code}" -X POST "$url" \
        -H "Content-Type: application/json" \
        -d "$data" 2>/dev/null)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ] || [ "$http_code" = "404" ]; then
        echo -e "${GREEN}✓${NC} (HTTP $http_code)"
        ((SUCCESS_COUNT++))
        return 0
    else
        echo -e "${RED}✗${NC} (HTTP $http_code)"
        ((FAIL_COUNT++))
        return 1
    fi
}

# Функция для тестирования DELETE запроса
test_delete() {
    local url=$1
    local description=$2
    echo -n "Testing: $description... "
    
    response=$(curl -s -w "\n%{http_code}" -X DELETE "$url" 2>/dev/null)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "204" ] || [ "$http_code" = "404" ]; then
        echo -e "${GREEN}✓${NC} (HTTP $http_code)"
        ((SUCCESS_COUNT++))
        return 0
    else
        echo -e "${RED}✗${NC} (HTTP $http_code)"
        ((FAIL_COUNT++))
        return 1
    fi
}

echo "🧪 ТЕСТИРОВАНИЕ ЭТАПА 2: ВАЖНО (33 endpoint'а)"
echo "=============================================="
echo "Base URL: $BASE_URL"
echo ""

# ========== ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ (5 endpoint'ов) ==========
echo -e "${YELLOW}📋 ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ (5 endpoint'ов)${NC}"
echo "----------------------------------------"

test_post "$BASE_URL/api/user/profile/sync" \
    "{\"userId\": \"$USER_ID\", \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/user/profile/sync - Синхронизация профиля"

test_post "$BASE_URL/api/user/profile/update" \
    "{\"userId\": \"$USER_ID\", \"name\": \"Test User\", \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/user/profile/update - Обновление профиля"

test_get "$BASE_URL/api/user/profile/history?userId=$USER_ID&limit=10" \
    "GET /api/user/profile/history - История изменений"

test_get "$BASE_URL/api/user/profile/privacy?userId=$USER_ID" \
    "GET /api/user/profile/privacy - Настройки приватности"

test_post "$BASE_URL/api/user/profile/privacy/update" \
    "{\"userId\": \"$USER_ID\", \"profileVisibility\": \"private\", \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/user/profile/privacy/update - Обновление приватности"

echo ""

# ========== ТАРИФЫ И ПОДПИСКИ (8 endpoint'ов) ==========
echo -e "${YELLOW}📋 ТАРИФЫ И ПОДПИСКИ (8 endpoint'ов)${NC}"
echo "----------------------------------------"

test_post "$BASE_URL/api/subscription/sync" \
    "{\"userId\": \"$USER_ID\", \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/subscription/sync - Синхронизация подписки"

test_post "$BASE_URL/api/subscription/update" \
    "{\"userId\": \"$USER_ID\", \"subscriptionType\": \"family\", \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/subscription/update - Обновление подписки"

test_get "$BASE_URL/api/subscription/purchase-history?userId=$USER_ID&limit=10" \
    "GET /api/subscription/purchase-history - История покупок"

test_get "$BASE_URL/api/subscription/status?userId=$USER_ID" \
    "GET /api/subscription/status - Статус подписки"

test_post "$BASE_URL/api/subscription/status/update" \
    "{\"userId\": \"$USER_ID\", \"status\": \"active\", \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/subscription/status/update - Обновление статуса"

test_get "$BASE_URL/api/subscription/auto-renewal?userId=$USER_ID" \
    "GET /api/subscription/auto-renewal - Настройки автопродления"

test_post "$BASE_URL/api/subscription/auto-renewal/update" \
    "{\"userId\": \"$USER_ID\", \"enabled\": true, \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/subscription/auto-renewal/update - Обновление автопродления"

test_post "$BASE_URL/api/subscription/cancel" \
    "{\"userId\": \"$USER_ID\", \"reason\": \"Test cancellation\", \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/subscription/cancel - Отмена подписки"

echo ""

# ========== НАСТРОЙКИ ПРИЛОЖЕНИЯ (10 endpoint'ов) ==========
echo -e "${YELLOW}📋 НАСТРОЙКИ ПРИЛОЖЕНИЯ (10 endpoint'ов)${NC}"
echo "----------------------------------------"

test_post "$BASE_URL/api/settings/sync" \
    "{\"userId\": \"$USER_ID\", \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/settings/sync - Синхронизация настроек"

test_post "$BASE_URL/api/settings/update" \
    "{\"userId\": \"$USER_ID\", \"theme\": \"dark\", \"language\": \"ru\", \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/settings/update - Обновление настроек"

test_get "$BASE_URL/api/settings/theme?userId=$USER_ID" \
    "GET /api/settings/theme - Настройки темы"

test_post "$BASE_URL/api/settings/theme/update" \
    "{\"userId\": \"$USER_ID\", \"theme\": \"light\", \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/settings/theme/update - Обновление темы"

test_get "$BASE_URL/api/settings/language?userId=$USER_ID" \
    "GET /api/settings/language - Настройки языка"

test_post "$BASE_URL/api/settings/language/update" \
    "{\"userId\": \"$USER_ID\", \"language\": \"en\", \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/settings/language/update - Обновление языка"

test_get "$BASE_URL/api/settings/notifications?userId=$USER_ID" \
    "GET /api/settings/notifications - Настройки уведомлений"

test_post "$BASE_URL/api/settings/notifications/update" \
    "{\"userId\": \"$USER_ID\", \"enabled\": true, \"pushEnabled\": true, \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/settings/notifications/update - Обновление уведомлений"

test_get "$BASE_URL/api/settings/biometry?userId=$USER_ID" \
    "GET /api/settings/biometry - Настройки биометрии"

test_post "$BASE_URL/api/settings/biometry/update" \
    "{\"userId\": \"$USER_ID\", \"enabled\": true, \"type\": \"face\", \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/settings/biometry/update - Обновление биометрии"

echo ""

# ========== ГЕОЛОКАЦИЯ И ГЕОЗОНЫ (7 endpoint'ов) ==========
echo -e "${YELLOW}📋 ГЕОЛОКАЦИЯ И ГЕОЗОНЫ (7 endpoint'ов)${NC}"
echo "----------------------------------------"

test_post "$BASE_URL/api/location/geofences/sync" \
    "{\"userId\": \"$USER_ID\", \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/location/geofences/sync - Синхронизация геозон"

test_post "$BASE_URL/api/location/geofences/update" \
    "{\"userId\": \"$USER_ID\", \"name\": \"Home\", \"latitude\": 55.7558, \"longitude\": 37.6173, \"radius\": 100, \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/location/geofences/update - Обновление геозоны"

test_delete "$BASE_URL/api/location/geofences/test_geofence_123" \
    "DELETE /api/location/geofences/{geofenceId} - Удаление геозоны"

test_get "$BASE_URL/api/location/movement-history?userId=$USER_ID&limit=10" \
    "GET /api/location/movement-history - История перемещений"

test_post "$BASE_URL/api/location/movement-history/update" \
    "{\"userId\": \"$USER_ID\", \"entries\": [], \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/location/movement-history/update - Обновление истории"

test_get "$BASE_URL/api/location/status?userId=$USER_ID" \
    "GET /api/location/status - Статус геолокации"

test_post "$BASE_URL/api/location/status/update" \
    "{\"userId\": \"$USER_ID\", \"enabled\": true, \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/location/status/update - Обновление статуса"

echo ""

# ========== СЕМЕЙНЫЙ ЧАТ (ОФЛАЙН) (3 endpoint'а) ==========
echo -e "${YELLOW}📋 СЕМЕЙНЫЙ ЧАТ (ОФЛАЙН) (3 endpoint'а)${NC}"
echo "----------------------------------------"

test_post "$BASE_URL/api/chat/offline-messages/sync" \
    "{\"userId\": \"$USER_ID\", \"familyId\": \"$FAMILY_ID\", \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/chat/offline-messages/sync - Синхронизация сообщений"

test_post "$BASE_URL/api/chat/offline-messages/send" \
    "{\"userId\": \"$USER_ID\", \"recipientId\": \"$CHILD_ID\", \"familyId\": \"$FAMILY_ID\", \"content\": \"Test message\", \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/chat/offline-messages/send - Отправка сообщения"

test_post "$BASE_URL/api/chat/offline-messages/resolve-conflicts" \
    "{\"userId\": \"$USER_ID\", \"familyId\": \"$FAMILY_ID\", \"conflicts\": [], \"deviceId\": \"$DEVICE_ID\"}" \
    "POST /api/chat/offline-messages/resolve-conflicts - Разрешение конфликтов"

echo ""

# ========== ИТОГИ ==========
echo "=============================================="
echo -e "${GREEN}✅ Успешно: $SUCCESS_COUNT${NC}"
echo -e "${RED}❌ Ошибок: $FAIL_COUNT${NC}"
echo "Всего протестировано: $((SUCCESS_COUNT + FAIL_COUNT))"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Некоторые тесты не прошли. Проверьте логи сервера.${NC}"
    exit 1
fi
