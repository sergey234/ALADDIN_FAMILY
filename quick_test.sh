#!/bin/bash

echo "🚀 БЫСТРОЕ ТЕСТИРОВАНИЕ ALADDIN API"
echo "==================================="
echo ""

TOTAL_TESTS=0
PASSED_TESTS=0

# Функция для тестирования
test_endpoint() {
    local endpoint="$1"
    local method="${2:-GET}"
    local description="$3"
    
    ((TOTAL_TESTS++))
    
    echo "🧪 ТЕСТ $TOTAL_TESTS: $description"
    echo "   $method $endpoint"
    
    # Выполняем запрос
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "HTTPSTATUS:%{http_code};TIME:%{time_total}" "http://149.154.65.180:8002$endpoint" 2>/dev/null)
    else
        response=$(curl -s -X "$method" -H "Content-Type: application/json" -w "HTTPSTATUS:%{http_code};TIME:%{time_total}" "http://149.154.65.180:8002$endpoint" -d '{}' 2>/dev/null)
    fi
    
    # Разбираем ответ
    body=$(echo "$response" | sed 's/HTTPSTATUS.2)
    time=$(echo "$response" | grep -o "TIME:[0-9.]*" | cut -d: -f2)
    
    # Проверяем JSON
    if echo "$body" | jq . >/dev/null 2>&1; then
        json_valid="✅"
    else
        json_valid="❌"
    fi
    
    # Проверяем source
    source=$(echo "$body" | jq -r '.source // "no_source"' 2>/dev/null || echo "invalid")
    if [ "$source" = "real_sfm" ]; then
        source_check="✅ real_sfm"
        ((PASSED_TESTS++))
    else
        source_check="⚠️ $source"
    fi
    
    # Вывод результата
    printf "   Статус: %-3s | Время: %-6s | JSON: %s | Source: %s\n" "$status" "${time}s" "$json_valid" "$source_check"
    echo ""
}

echo "🎯 ТЕСТИРОВАНИЕ ОСНОВНЫХ КОМПОНЕНТОВ:"
echo "===================================="

# 1. Health Check
test_endpoint "/api/health" "GET" "API Health Check"

# 2. Исправленные компоненты
test_endpoint "/api/components/health" "GET" "Components Health"
test_endpoint "/a "Component Config"
test_endpoint "/api/components/logs/sfm_core" "GET" "Component Logs"

# 3. Исправленные функции безопасности
test_endpoint "/api/phishing/sensitivity" "GET" "Phishing Sensitivity"
test_endpoint "/api/phishing/block_suspicious" "GET" "Block Suspicious"
test_endpoint "/api/phishing/exclusions" "GET" "Phishing Exclusions"
test_endpoint "/api/malware/scan_scheduled" "GET" "Malware Scan Scheduled"

# 4. Аналитика
test_endpoint "/api/analytics/overview" "GET" "Analytics Overview"

# 5. Мониторинг
test_endpoint "/api/ai/categories/stats" "GET" "AI Categories Stats"
test_endpoint "/api/darkweb/stats" "GET" "Dark Web Stats"
test_endpoint "/api/identity/stats" "GET" "Identity Stats"

echo "📊 ИТОГИ БЫСТРОГО ТЕСТИРОВАНИЯ:"
echo "================================"
echo "Всего тестов: $TOTAL_TESTS"
echo "Пройдено: $PASSED_TESTS"
echo "Успешность: $((PASSED_TESTS * 100 / TOTAL_TESTS))%"

if [ "$PAS   echo "⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ. ТРЕБУЕТСЯ АНАЛИЗ."
fi

echo ""
echo "📋 ДЕТАЛЬНЫЙ ПЛАН ТЕСТИРОВАНИЯ: COMPREHENSIVE_TESTING_PLAN.md"

