#!/bin/bash

# Скрипт для тестирования Gamification API endpoints
# Использование: ./test_gamification_api.sh [base_url] [userId]

BASE_URL="${1:-http://localhost:8000}"
USER_ID="${2:-test_user_123}"

echo "🧪 Тестирование Gamification API"
echo "📍 Base URL: $BASE_URL"
echo "👤 User ID: $USER_ID"
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
test_endpoint() {
    local method=$1
    local endpoint=$2
    local description=$3
    local data=$4
    
    TOTAL=$((TOTAL + 1))
    echo -n "Testing: $description ... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code)"
        echo "  Response: $body"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo "═══════════════════════════════════════════════════════════"
echo "📊 БАЛАНС ЕДИНОРОГОВ (4 endpoint'а)"
echo "═══════════════════════════════════════════════════════════"

# 1. GET /api/gamification/balance/{userId}
test_endpoint "GET" "/api/gamification/balance/$USER_ID" \
    "GET /api/gamification/balance/{userId} - Получить баланс"

# 2. POST /api/gamification/balance/add
test_endpoint "POST" "/api/gamification/balance/add" \
    "POST /api/gamification/balance/add - Добавить единорогов" \
    "{\"userId\":\"$USER_ID\",\"amount\":10,\"reason\":\"Test reward\"}"

# 3. POST /api/gamification/balance/subtract
test_endpoint "POST" "/api/gamification/balance/subtract" \
    "POST /api/gamification/balance/subtract - Вычесть единорогов" \
    "{\"userId\":\"$USER_ID\",\"amount\":5,\"reason\":\"Test purchase\"}"

# 4. GET /api/gamification/balance/history
test_endpoint "GET" "/api/gamification/balance/history?userId=$USER_ID&limit=10" \
    "GET /api/gamification/balance/history - История операций"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🎁 НАГРАДЫ (6 endpoint'ов)"
echo "═══════════════════════════════════════════════════════════"

# 5. GET /api/gamification/rewards
test_endpoint "GET" "/api/gamification/rewards?userId=$USER_ID" \
    "GET /api/gamification/rewards - Получить награды"

# 6. POST /api/gamification/rewards/claim
test_endpoint "POST" "/api/gamification/rewards/claim" \
    "POST /api/gamification/rewards/claim - Получить награду" \
    "{\"userId\":\"$USER_ID\",\"rewardId\":\"reward_1\"}"

# 7. GET /api/gamification/rewards/history
test_endpoint "GET" "/api/gamification/rewards/history?userId=$USER_ID&limit=10" \
    "GET /api/gamification/rewards/history - История наград"

# 8. POST /api/gamification/rewards/give
test_endpoint "POST" "/api/gamification/rewards/give?childId=$USER_ID&rewardId=reward_1&parentId=parent_123" \
    "POST /api/gamification/rewards/give - Выдать награду ребенку" \
    "{}"

# 9. GET /api/gamification/rewards/shop
test_endpoint "GET" "/api/gamification/rewards/shop?userId=$USER_ID" \
    "GET /api/gamification/rewards/shop - Получить магазин"

# 10. POST /api/gamification/rewards/purchase
test_endpoint "POST" "/api/gamification/rewards/purchase" \
    "POST /api/gamification/rewards/purchase - Купить товар" \
    "{\"userId\":\"$USER_ID\",\"rewardId\":\"shop_1\"}"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🏆 ДОСТИЖЕНИЯ (5 endpoint'ов)"
echo "═══════════════════════════════════════════════════════════"

# 11. GET /api/gamification/achievements
test_endpoint "GET" "/api/gamification/achievements?userId=$USER_ID" \
    "GET /api/gamification/achievements - Получить достижения"

# 12. POST /api/gamification/achievements/unlock
test_endpoint "POST" "/api/gamification/achievements/unlock" \
    "POST /api/gamification/achievements/unlock - Разблокировать достижение" \
    "{\"userId\":\"$USER_ID\",\"achievementId\":\"ach_1\"}"

# 13. GET /api/gamification/achievements/progress
test_endpoint "GET" "/api/gamification/achievements/progress?userId=$USER_ID" \
    "GET /api/gamification/achievements/progress - Прогресс достижений"

# 14. GET /api/gamification/achievements/{achievementId}
test_endpoint "GET" "/api/gamification/achievements/ach_1?userId=$USER_ID" \
    "GET /api/gamification/achievements/{achievementId} - Получить достижение"

# 15. POST /api/gamification/achievements/claim
test_endpoint "POST" "/api/gamification/achievements/claim" \
    "POST /api/gamification/achievements/claim - Получить награду за достижение" \
    "{\"userId\":\"$USER_ID\",\"achievementId\":\"ach_1\"}"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🏅 ТУРНИРЫ (6 endpoint'ов)"
echo "═══════════════════════════════════════════════════════════"

# 16. GET /api/gamification/tournaments
test_endpoint "GET" "/api/gamification/tournaments" \
    "GET /api/gamification/tournaments - Получить турниры"

# 17. POST /api/gamification/tournaments/join
test_endpoint "POST" "/api/gamification/tournaments/join" \
    "POST /api/gamification/tournaments/join - Присоединиться к турниру" \
    "{\"userId\":\"$USER_ID\",\"tournamentId\":\"tour_1\"}"

# 18. GET /api/gamification/tournaments/{tournamentId}
test_endpoint "GET" "/api/gamification/tournaments/tour_1" \
    "GET /api/gamification/tournaments/{tournamentId} - Получить турнир"

# 19. GET /api/gamification/tournaments/leaderboard
test_endpoint "GET" "/api/gamification/tournaments/leaderboard?tournamentId=tour_1&limit=10" \
    "GET /api/gamification/tournaments/leaderboard - Таблица лидеров"

# 20. POST /api/gamification/tournaments/leave
test_endpoint "POST" "/api/gamification/tournaments/leave" \
    "POST /api/gamification/tournaments/leave - Покинуть турнир" \
    "{\"userId\":\"$USER_ID\",\"tournamentId\":\"tour_1\"}"

# 21. GET /api/gamification/tournaments/history
test_endpoint "GET" "/api/gamification/tournaments/history?userId=$USER_ID&limit=10" \
    "GET /api/gamification/tournaments/history - История турниров"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "⚙️  НАСТРОЙКИ ИГР (4 endpoint'а)"
echo "═══════════════════════════════════════════════════════════"

# 22. GET /api/gamification/settings
test_endpoint "GET" "/api/gamification/settings?userId=$USER_ID" \
    "GET /api/gamification/settings - Получить настройки"

# 23. POST /api/gamification/settings/update
test_endpoint "POST" "/api/gamification/settings/update" \
    "POST /api/gamification/settings/update - Обновить настройки" \
    "{\"userId\":\"$USER_ID\",\"soundEnabled\":true,\"difficulty\":\"medium\"}"

# 24. GET /api/gamification/settings/notifications
test_endpoint "GET" "/api/gamification/settings/notifications?userId=$USER_ID" \
    "GET /api/gamification/settings/notifications - Настройки уведомлений"

# 25. POST /api/gamification/settings/notifications/update
test_endpoint "POST" "/api/gamification/settings/notifications/update" \
    "POST /api/gamification/settings/notifications/update - Обновить уведомления" \
    "{\"userId\":\"$USER_ID\",\"achievementUnlocked\":true}"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📈 ПРОГРЕСС ИГР (5 endpoint'ов)"
echo "═══════════════════════════════════════════════════════════"

# 26. GET /api/gamification/progress
test_endpoint "GET" "/api/gamification/progress?userId=$USER_ID" \
    "GET /api/gamification/progress - Получить прогресс"

# 27. POST /api/gamification/progress/update
test_endpoint "POST" "/api/gamification/progress/update" \
    "POST /api/gamification/progress/update - Обновить прогресс" \
    "{\"userId\":\"$USER_ID\",\"gameId\":\"game_1\",\"experience\":10,\"score\":100}"

# 28. GET /api/gamification/progress/stats
test_endpoint "GET" "/api/gamification/progress/stats?userId=$USER_ID" \
    "GET /api/gamification/progress/stats - Статистика прогресса"

# 29. GET /api/gamification/progress/level
test_endpoint "GET" "/api/gamification/progress/level?userId=$USER_ID" \
    "GET /api/gamification/progress/level - Уровень игрока"

# 30. POST /api/gamification/progress/reset
test_endpoint "POST" "/api/gamification/progress/reset" \
    "POST /api/gamification/progress/reset - Сбросить прогресс" \
    "{\"userId\":\"$USER_ID\",\"gameId\":\"game_1\",\"parentId\":\"parent_123\"}"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ"
echo "═══════════════════════════════════════════════════════════"
echo "Всего тестов: $TOTAL"
echo -e "${GREEN}Успешно: $PASSED${NC}"
echo -e "${RED}Провалено: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ Все тесты пройдены успешно!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Некоторые тесты провалились${NC}"
    exit 1
fi
