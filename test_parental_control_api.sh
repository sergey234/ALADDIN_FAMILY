#!/bin/bash

# Скрипт для тестирования Parental Control Sync API endpoints
# Использование: ./test_parental_control_api.sh [base_url] [familyId] [childId]

BASE_URL="${1:-http://localhost:8000}"
FAMILY_ID="${2:-family_001}"
CHILD_ID="${3:-child_123}"

echo "🧪 Тестирование Parental Control Sync API"
echo "📍 Base URL: $BASE_URL"
echo "👨‍👩‍👧‍👦 Family ID: $FAMILY_ID"
echo "👶 Child ID: $CHILD_ID"
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Счетчики
PASSED=0
FAILED=0
TOTAL=0

# Функция для тестирования endpoint
test_get() {
    local endpoint=$1
    local description=$2
    TOTAL=$((TOTAL + 1))
    echo -n "Testing: $description ... "
    
    response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$endpoint" \
        -H "Content-Type: application/json" 2>/dev/null)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code)"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

test_post() {
    local endpoint=$1
    local data=$2
    local description=$3
    TOTAL=$((TOTAL + 1))
    echo -n "Testing: $description ... "
    
    response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
        -H "Content-Type: application/json" \
        -d "$data" 2>/dev/null)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code)"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

test_delete() {
    local endpoint=$1
    local description=$2
    TOTAL=$((TOTAL + 1))
    echo -n "Testing: $description ... "
    
    response=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL$endpoint" \
        -H "Content-Type: application/json" 2>/dev/null)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code)"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo "═══════════════════════════════════════════════════════════"
echo "НАСТРОЙКИ (5 endpoint'ов)"
echo "═══════════════════════════════════════════════════════════"

# 1. GET /api/parental-control/settings/{familyId}
test_get "$BASE_URL/api/parental-control/settings/$FAMILY_ID" "Получить настройки"

# 2. POST /api/parental-control/settings/update
test_post "$BASE_URL/api/parental-control/settings/update" \
    "{\"familyId\": \"$FAMILY_ID\", \"isContentFilterEnabled\": true, \"screenTimeLimitHours\": 3}" \
    "Обновить настройки"

# 3. GET /api/parental-control/settings/history
test_get "$BASE_URL/api/parental-control/settings/history?familyId=$FAMILY_ID&limit=10" "История изменений настроек"

# 4. POST /api/parental-control/settings/sync
test_post "$BASE_URL/api/parental-control/settings/sync" \
    "{\"familyId\": \"$FAMILY_ID\", \"deviceId\": \"device_123\"}" \
    "Синхронизация настроек"

# 5. GET /api/parental-control/settings/conflicts
test_get "$BASE_URL/api/parental-control/settings/conflicts?familyId=$FAMILY_ID" "Конфликты настроек"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "ЛИМИТЫ ВРЕМЕНИ (4 endpoint'а)"
echo "═══════════════════════════════════════════════════════════"

# 6. GET /api/parental-control/time-limits/{childId}
test_get "$BASE_URL/api/parental-control/time-limits/$CHILD_ID" "Получить лимиты времени"

# 7. POST /api/parental-control/time-limits/update
test_post "$BASE_URL/api/parental-control/time-limits/update" \
    "{\"childId\": \"$CHILD_ID\", \"dailyLimitMinutes\": 180, \"bedtimeStart\": \"22:00\"}" \
    "Обновить лимиты времени"

# 8. GET /api/parental-control/time-limits/history
test_get "$BASE_URL/api/parental-control/time-limits/history?childId=$CHILD_ID&limit=10" "История лимитов времени"

# 9. POST /api/parental-control/time-limits/reset
test_post "$BASE_URL/api/parental-control/time-limits/reset" \
    "{\"childId\": \"$CHILD_ID\"}" \
    "Сбросить лимиты времени"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "РАСПИСАНИЯ (4 endpoint'а)"
echo "═══════════════════════════════════════════════════════════"

# 10. GET /api/parental-control/schedules/{childId}
test_get "$BASE_URL/api/parental-control/schedules/$CHILD_ID" "Получить расписания"

# 11. POST /api/parental-control/schedules/update
test_post "$BASE_URL/api/parental-control/schedules/update" \
    "{\"childId\": \"$CHILD_ID\", \"name\": \"Школьное расписание\", \"weekdays\": [0,1,2,3,4], \"startTime\": \"08:00\", \"endTime\": \"20:00\"}" \
    "Обновить расписание"

# 12. GET /api/parental-control/schedules/history
test_get "$BASE_URL/api/parental-control/schedules/history?childId=$CHILD_ID&limit=10" "История расписаний"

# 13. POST /api/parental-control/schedules/delete
test_post "$BASE_URL/api/parental-control/schedules/delete" \
    "{\"scheduleId\": \"schedule_123\"}" \
    "Удалить расписание"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "ГЕОЗОНЫ (4 endpoint'а)"
echo "═══════════════════════════════════════════════════════════"

# 14. GET /api/parental-control/geofences/{childId}
test_get "$BASE_URL/api/parental-control/geofences/$CHILD_ID" "Получить геозоны"

# 15. POST /api/parental-control/geofences/add
test_post "$BASE_URL/api/parental-control/geofences/add" \
    "{\"childId\": \"$CHILD_ID\", \"name\": \"Дом\", \"latitude\": 55.7558, \"longitude\": 37.6173, \"radius\": 100.0}" \
    "Добавить геозону"

# 16. POST /api/parental-control/geofences/update
test_post "$BASE_URL/api/parental-control/geofences/update" \
    "{\"geofenceId\": \"geofence_123\", \"name\": \"Дом обновлен\", \"radius\": 150.0}" \
    "Обновить геозону"

# 17. DELETE /api/parental-control/geofences/{geofenceId}
test_delete "$BASE_URL/api/parental-control/geofences/geofence_123" "Удалить геозону"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "БЛОКИРОВКИ ПРИЛОЖЕНИЙ (3 endpoint'а)"
echo "═══════════════════════════════════════════════════════════"

# 18. GET /api/parental-control/app-blocks/{childId}
test_get "$BASE_URL/api/parental-control/app-blocks/$CHILD_ID" "Получить блокировки приложений"

# 19. POST /api/parental-control/app-blocks/update
test_post "$BASE_URL/api/parental-control/app-blocks/update" \
    "{\"childId\": \"$CHILD_ID\", \"blockedApps\": [\"TikTok\", \"Instagram\"], \"appLimits\": {\"YouTube\": 30}}" \
    "Обновить блокировки приложений"

# 20. POST /api/parental-control/app-blocks/sync
test_post "$BASE_URL/api/parental-control/app-blocks/sync" \
    "{\"childId\": \"$CHILD_ID\", \"deviceId\": \"device_123\"}" \
    "Синхронизация блокировок приложений"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ"
echo "═══════════════════════════════════════════════════════════"
echo "Всего тестов: $TOTAL"
echo -e "${GREEN}Успешно: $PASSED${NC}"
echo -e "${RED}Провалено: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Все тесты пройдены успешно!${NC}"
    exit 0
else
    echo -e "${RED}❌ Некоторые тесты провалены${NC}"
    exit 1
fi
