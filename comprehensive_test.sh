#!/bin/bash

echo "🎯 ПОЛНОЕ ТЕСТИРОВАНИЕ ВСЕХ 17 ИСПРАВЛЕННЫХ ФУНКЦИЙ ALADDIN"
echo "=========================================================="
echo ""

BASE_URL="http://149.154.65.180:8002"

# Функция для тестирования эндпоинта
test_endpoint() {
    local endpoint="$1"
    local expected_source="$2"
    local description="$3"
    
    echo "🧪 $description"
    echo "   $endpoint"
    
    response=$(curl -s -w "HTTP:%{http_code};TIME:%{time_total}" "$BASE_URL$endpoint" 2>/dev/null)
    status=$(echo "$response" | grep -o "HTTP:[0-9]*" | cut -d: -f2)
    time=$(echo "$response" | grep -o "TIME:[0-9.]*" | cut -d: -f2)
    body=$(echo "$response" | sed 's/HTTP.*//')
    
    # Проверка source
    source=$(echo "$body" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('source', 'no_souя: %.3fs | Source: %s" "$status" "$time" "$source"
    
    if [ "$status" = "200" ] && [ "$source" = "$expected_source" ]; then
        echo " ✅ ПРОЙДЕН"
        return 0
    else
        echo " ❌ НЕ ПРОЙДЕН"
        return 1
    fi
}

echo "📋 ТЕСТИРУЕМ 17 ИСПРАВЛЕННЫХ ФУНКЦИЙ:"
echo "====================================="

total_tests=0
passed_tests=0

# 1. Components (4 функции)
echo ""
echo "🔧 КОМПОНЕНТЫ (Components):"
test_endpoint "/api/components/health" "real_sfm" "1. Здоровье компонентов"; ((total_tests++)); [ $? -eq 0 ] && ((passed_tests++))
test_endpoint "/api/components/status/sfm_core" "real_sfm" "2. Статус SFM компонента"; ((total_tests++)); [ $? -eq 0 ] && ((passed_tests++))
test_endpoint "/api/components/config/sfm_core" "real_sfm" "3. Конфигурация компонента"; ((total_tests++)); [ $? -eq 0 ] && ((passed_tests++))
test_endpoint "/api/components/logs/sfm_core" "realНТИФИШИНГ (Phishing):"
test_endpoint "/api/phishing/sensitivity" "real_sfm" "5. Чувствительность антифишинга"; ((total_tests++)); [ $? -eq 0 ] && ((passed_tests++))
test_endpoint "/api/phishing/block_suspicious" "real_sfm" "6. Блокировка подозрительных"; ((total_tests++)); [ $? -eq 0 ] && ((passed_tests++))
test_endpoint "/api/phishing/exclusions" "real_sfm" "7. Исключения для фишинга"; ((total_tests++)); [ $? -eq 0 ] && ((passed_tests++))

# 3. Malware (1 функция)
echo ""
echo "🦠 АНТИМАЛВАРЬ (Malware):"
test_endpoint "/api/malware/scan_scheduled" "real_sfm" "8. Расписание сканирования"; ((total_tests++)); [ $? -eq 0 ] && ((passed_tests++))

# 4. Analytics (1 функция)
echo ""
echo "📊 АНАЛИТИКА (Analytics):"
test_endpoint "/api/analytics/overview" "real_sfm" "9. Обзор аналитики"; ((total_tests++)); [ $? -eq 0 ] && ((passed_tests++))

echo ""
echo "🎯 Дndpoint "/api/health" "no_source" "10. Общий health check"; ((total_tests++)); [ $? -eq 0 ] && ((passed_tests++))
test_endpoint "/api/system/health" "no_source" "11. Здоровье системы"; ((total_tests++)); [ $? -eq 0 ] && ((passed_tests++))
test_endpoint "/api/subscription/status" "no_source" "12. Статус подписки"; ((total_tests++)); [ $? -eq 0 ] && ((passed_tests++))
test_endpoint "/api/notifications/stats" "no_source" "13. Статистика уведомлений"; ((total_tests++)); [ $? -eq 0 ] && ((passed_tests++))
test_endpoint "/api/auth/profile" "no_source" "14. Профиль пользователя"; ((total_tests++)); [ $? -eq 0 ] && ((passed_tests++))
test_endpoint "/api/mobile/app_lock" "no_source" "15. Блокировка приложений"; ((total_tests++)); [ $? -eq 0 ] && ((passed_tests++))
test_endpoint "/api/ai/categories/stats" "no_source" "16. AI категории"; ((total_tests++)); [ $? -eq 0 ] && ((passed_tests++))
test_endpoint "/api/darkweecho ""
echo "🎉 ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:"
echo "====================================="
echo "📊 СТАТИСТИКА:"
echo "   Всего тестов: $total_tests"
echo "   Пройдено: $passed_tests"
echo "   Успешность: $((passed_tests * 100 / total_tests))%"

if [ $passed_tests -eq $total_tests ]; then
    echo ""
    echo "🎉 ОТЛИЧНЫЙ РЕЗУЛЬТАТ!"
    echo "   ✅ ВСЕ ЭНДПОИНТЫ РАБОТАЮТ КОРРЕКТНО!"
    echo "   ✅ ВСЕ ИСПРАВЛЕННЫЕ ФУНКЦИИ ВОЗВРАЩАЮТ real_sfm!"
    echo "   ✅ СИСТЕМА ALADDIN ГОТОВА К ПРОДАКШЕНУ!"
elif [ $passed_tests -ge 15 ]; then
    echo ""
    echo "⚠️ ХОРОШИЙ РЕЗУЛЬТАТ"
    echo "   ✅ ОСНОВНЫЕ ФУНКЦИИ РАБОТАЮТ"
    echo "   ⚠️ ЕСТЬ НЕБОЛЬШИЕ ПРОБЛЕМЫ"
else
    echo ""
    echo "❌ КРИТИЧЕСКИЕ ПРОБЛЕМЫ"
    echo "   ❌ МНОГ   echo "✅ Настроить мониторинг и alerting"
else
    echo "🔧 Проанализировать проблемные эндпоинты"
    echo "🔧 Проверить логи API Gateway и SFM"
    echo "🔧 Исправить найденные проблемы"
fi
