#!/bin/bash

echo "🔬 ГЛУБОКОЕ ТЕСТИРОВАНИЕ ALADDIN API - ПО ОДНОМУ ЭНДПОИНТУ ЗА РАЗ"
echo "=================================================================="
echo ""

# Функция для тестирования одного API
test_api() {
    local endpoint=$1
    local method=${2:-GET}
    local expected_source=${3:-real_sfm}
    
    echo "🧪 ТЕСТИРУЕМ: $method $endpoint"
    echo "----------------------------------------"
    
    # Замер времени
    start_time=$(date +%s.%3N)
    
    # Выполнение запроса
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\nHTTPSTATUS:%{http_code}\nTIME:%{time_total}" "http://149.154.65.180:8002$endpoint" 2>/dev/null)
    elif [ "$method" = "POST" ]; then
        response=$(curl -s -X POST -H "Content-Type: application/json" -w "\nHTTPSTATUS:%{http_code}\nTIn
        response=$(curl -s -X PUT -H "Content-Type: application/json" -w "\nHTTPSTATUS:%{http_code}\nTIME:%{time_total}" "http://149.154.65.180:8002$endpoint" -d '{}' 2>/dev/null)
    fi
    
    # Разбор ответа
    body=$(echo "$response" | head -n -2)
    http_status=$(echo "$response" | grep "HTTPSTATUS:" | cut -d: -f2)
    response_time=$(echo "$response" | grep "TIME:" | cut -d: -f2)
    
    end_time=$(date +%s.%3N)
    total_time=$(echo "$end_time - $start_time" | bc)
    
    echo "📊 РЕЗУЛЬТАТЫ:"
    echo "   HTTP Статус: $http_status"
    printf "   Время отклика: %.3f сек\n" "$response_time"
    printf "   Общее время: %.3f сек\n" "$total_time"
    
    # Проверка JSON
    if echo "$body" | jq . >/dev/null 2>&1; then
        echo "   ✅ JSON: ВАЛИДНЫЙ"
        
        # Проверка source
        source_value=$(echo "$body" | jq -r '.source // empty')
        if [ "$source_value" = "$expected_source" ]; then
      $source_value (ОЖИДАЛИ: $expected_source)"
        fi
        
        # Показать содержимое
        echo "   📄 СОДЕРЖИМОЕ:"
        echo "$body" | jq . | head -20
        
    else
        echo "   ❌ JSON: НЕВАЛИДНЫЙ"
        echo "   📄 СЫРОЙ ОТВЕТ:"
        echo "$body"
    fi
    
    echo ""
    echo "----------------------------------------"
    echo ""
}

echo "🧪 ЭТАП 1: ТЕСТИРОВАНИЕ КОМПОНЕНТОВ (10 эндпоинтов)"
echo "=================================================="

# Компоненты - исправлены
test_api "/api/components/health" "GET" "real_sfm"
test_api "/api/components/status/sfm_core" "GET" "real_sfm"
test_api "/api/components/config/sfm_core" "GET" "real_sfm"
test_api "/api/components/logs/sfm_core" "GET" "real_sfm"

echo "🧪 ЭТАП 2: ТЕСТИРОВАНИЕ БЕЗОПАСНОСТИ (14 эндпоинтов)"
echo "==================================================="

# ng/exclusions" "GET" "real_sfm"
test_api "/api/malware/scan_scheduled" "GET" "real_sfm"

echo "🎯 ПРОМЕЖУТОЧНЫЕ РЕЗУЛЬТАТЫ:"
echo "• Компоненты: 4/4 протестировано"
echo "• Безопасность: 4/4 протестировано"
echo "• Все исправленные функции должны возвращать real_sfm"

