#!/bin/bash
# Скрипт для тестирования всех endpoints через curl

BASE_URL="https://aladdin-ai.ru"
# Для локального тестирования: BASE_URL="http://149.154.65.180:8001"

echo "🧪 ТЕСТИРОВАНИЕ ENDPOINTS ALADDIN API"
echo "======================================"
echo ""

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -n "Testing $method $endpoint ... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$endpoint" 2>/dev/null)
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✅ OK (HTTP $http_code)${NC}"
        echo "   $description"
    else
        echo -e "${RED}❌ FAILED (HTTP $http_code)${NC}"
        echo "   $description"
        echo "   Response: $body" | head -3
    fi
    echo ""
}

echo "🤖 AI ASSISTANT ENDPOINTS (8)"
echo "-------------------------------"
test_endpoint "POST" "/api/ai/assistant/chat" '{"message":"Test","context":"general"}' "AI Chat"
test_endpoint "GET" "/api/ai/assistant/history" "" "AI History"
test_endpoint "POST" "/api/ai/assistant/feedback" '{"rating":5,"comment":"Test"}' "AI Feedback"
test_endpoint "GET" "/api/ai/assistant/capabilities" "" "AI Capabilities"
test_endpoint "POST" "/api/ai/assistant/analyze_threat" '{"threat":"Test threat"}' "AI Analyze Threat"
test_endpoint "GET" "/api/ai/assistant/recommendations" "" "AI Recommendations"
test_endpoint "POST" "/api/ai/assistant/report_incident" '{"type":"test","description":"Test"}' "AI Report Incident"
test_endpoint "GET" "/api/ai/assistant/security_tips" "" "AI Security Tips"

echo ""
echo "🔔 NOTIFICATIONS ENDPOINTS (16)"
echo "-------------------------------"
test_endpoint "GET" "/api/notifications/list" "" "List Notifications"
test_endpoint "GET" "/api/notifications/stats" "" "Notifications Stats"
test_endpoint "GET" "/api/notifications/unread_count" "" "Unread Count"
test_endpoint "POST" "/api/notifications/mark_read/test123" "" "Mark Read"
test_endpoint "POST" "/api/notifications/delete/test123" "" "Delete Notification"
test_endpoint "POST" "/api/notifications/bulk_mark_read" '{"notification_ids":["1","2"]}' "Bulk Mark Read"
test_endpoint "POST" "/api/notifications/test" "" "Test Notification"
test_endpoint "PUT" "/api/notifications/settings" '{"push_enabled":true}' "Update Settings"
test_endpoint "GET" "/api/notifications/categories" "" "Get Categories"
test_endpoint "GET" "/api/notifications/preferences" "" "Get Preferences"
test_endpoint "PUT" "/api/notifications/preferences" '{"preferences":{"push_enabled":true}}' "Update Preferences"
test_endpoint "POST" "/api/notifications/clear_all" "" "Clear All"
test_endpoint "POST" "/api/notifications/archive/test123" "" "Archive Notification"
test_endpoint "POST" "/api/notifications/unarchive/test123" "" "Unarchive Notification"
test_endpoint "GET" "/api/notifications/filter?category=threat&limit=10" "" "Filter Notifications"
test_endpoint "GET" "/api/notifications/search?query=test&limit=10" "" "Search Notifications"
test_endpoint "GET" "/api/notifications/export?format=json" "" "Export Notifications"

echo ""
echo "📊 ИТОГОВАЯ СТАТИСТИКА"
echo "======================"
echo "Всего протестировано: 24 endpoints"
echo "  - AI Assistant: 8"
echo "  - Notifications: 16"
echo ""
echo "✅ Тестирование завершено!"
