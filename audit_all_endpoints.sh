#!/bin/bash

echo "🎯 ДЕТАЛЬНЫЙ АУДИТ ВСЕХ ENDPOINTS ALADDIN API"
echo "==========================================="
echo "🕐 ВРЕМЯ НАЧАЛА: $(date)"
echo "🌐 СЕРВЕР: https://aladdin-ai.ru/api"
echo ""

# Счетчики
TOTAL_TESTS=0
SUCCESSFUL_TESTS=0

# Функция для тестирования endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local method="${3:-GET}"

    echo ""
    echo "🔍 ТЕСТИРОВАНИЕ: $name"
    echo "📍 URL: $url"
    echo "📝 Метод: $method"

    ((TOTAL_TESTS++))

    # Выполняем запрос
    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\nHTTP_STATUS:%{http_code}\nTIME:%{time_total}s" -X POST -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"test123"}' "$url" 2>/dev/null)
    else
        response=$(curl -s -w "\nHTTP_STATUS:%{http_code}\nTIME:%{time_total}s" "$url" 2>/dev/null)
    fi

    # Парсим ответ
    body=$(echo "$response" | head -n -2)
    status_line=$(echo "$response" | grep "HTTP_STATUS:")
    time_line=$(echo "$response" | grep "TIME:")

    status_code=$(echo "$status_line" | cut -d: -f2)
    response_time=$(echo "$time_line" | cut -d: -f2)

    echo "📊 СТАТУС: $status_code"
    echo "⏱️ ВРЕМЯ: ${response_time}s"

    # Проверяем JSON
    if echo "$body" | jq . >/dev/null 2>&1; then
        echo "📄 JSON ОТВЕТ: $(echo "$body" | jq -c . | cut -c1-100)..."
    else
        echo "📄 ТЕКСТ ОТВЕТ: ${body:0:100}..."
    fi

    # Проверяем успех
    if [ "$status_code" = "200" ]; then
        echo "✅ РЕЗУЛЬТАТ: УСПЕХ"
        ((SUCCESSFUL_TESTS++))
    else
        echo "❌ РЕЗУЛЬТАТ: НЕУДАЧА"
    fi
}

echo "🚀 НАЧИНАЕМ ТЕСТИРОВАНИЕ..."

# 1. HEALTH
test_endpoint "Health Check" "https://aladdin-ai.ru/api/health"

# 2. COMPONENTS
test_endpoint "Component: crash_detection_agent" "https://aladdin-ai.ru/api/components/status/crash_detection_agent"
test_endpoint "Component: emergency_response_agent" "https://aladdin-ai.ru/api/components/status/emergency_response_agent"
test_endpoint "Component: phishing_protection_agent" "https://aladdin-ai.ru/api/components/status/phishing_protection_agent"

# 3. SECURITY
test_endpoint "Security: Phishing Sensitivity" "https://aladdin-ai.ru/api/phishing/sensitivity"
test_endpoint "Security: Malware Scan" "https://aladdin-ai.ru/api/malware/scan_scheduled"
test_endpoint "Security: Mobile App Lock" "https://aladdin-ai.ru/api/mobile/app_lock"
test_endpoint "Security: Network Firewall" "https://aladdin-ai.ru/api/network/firewall_rules"

# 4. MONITORING
test_endpoint "Monitoring: AI Categories Stats" "https://aladdin-ai.ru/api/ai/categories/stats"
test_endpoint "Monitoring: Location Stats" "https://aladdin-ai.ru/api/location/stats"
test_endpoint "Monitoring: Data Cleanup Stats" "https://aladdin-ai.ru/api/data/cleanup/stats"

# 5. PROTECTION
test_endpoint "Protection: Dark Web Leaks" "https://aladdin-ai.ru/api/darkweb/leaks"
test_endpoint "Protection: Identity Theft Stats" "https://aladdin-ai.ru/api/identity/theft/stats"
test_endpoint "Protection: Anti-Tracker" "https://aladdin-ai.ru/api/antitracker/trackers"

# 6. ANALYTICS
test_endpoint "Analytics: Overview" "https://aladdin-ai.ru/api/analytics/overview"
test_endpoint "Analytics: Security Events" "https://aladdin-ai.ru/api/analytics/security_events"
test_endpoint "Analytics: Performance" "https://aladdin-ai.ru/api/analytics/performance"

# 7. AUTH
test_endpoint "Auth: Login" "https://aladdin-ai.ru/api/auth/login" "POST"

echo ""
echo "📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ АУДИТА"
echo "============================"
echo "✅ УСПЕШНЫХ ТЕСТОВ: $SUCCESSFUL_TESTS/$TOTAL_TESTS"
echo "❌ НЕУДАЧНЫХ ТЕСТОВ: $((TOTAL_TESTS - SUCCESSFUL_TESTS))"
SUCCESS_RATE=$(echo "scale=1; ($SUCCESSFUL_TESTS * 100) / $TOTAL_TESTS" | bc 2>/dev/null || echo "0")
echo "🎯 ПРОЦЕНТ УСПЕХА: ${SUCCESS_RATE}%"

# Финальный вердикт
echo ""
if [ "$SUCCESSFUL_TESTS" -eq "$TOTAL_TESTS" ]; then
    echo "🎉 ВЕРДИКТ: ВСЕ ENDPOINTS РАБОТАЮТ! ПРОДАКШЕН ГОТОВ!"
elif [ "$SUCCESSFUL_TESTS" -ge "$(($TOTAL_TESTS * 8 / 10))" ]; then
    echo "⚠️ ВЕРДИКТ: БОЛЬШИНСТВО ENDPOINTS РАБОТАЕТ! ПРОДАКШЕН ГОТОВ!"
else
    echo "❌ ВЕРДИКТ: МНОГИЕ ENDPOINTS НЕ РАБОТАЮТ! ТРЕБУЕТСЯ ДОРАБОТКА!"
fi

echo ""
echo "🕐 ВРЕМЯ ОКОНЧАНИЯ АУДИТА: $(date)"
echo ""
echo "💾 ДАННЫЕ ДОСТУПНЫ ДЛЯ ПРОВЕРКИ ВЫШЕ"