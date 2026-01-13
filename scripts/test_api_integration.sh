#!/bin/bash

# 🔌 Скрипт для тестирования API интеграции всех 42 компонентов
# Использование: ./Scripts/test_api_integration.sh

set -e

SERVER_IP="149.154.65.180"
# Пробуем разные варианты URL
BASE_URLS=(
    "http://${SERVER_IP}/api"
    "https://${SERVER_IP}/api"
    "http://${SERVER_IP}:8000/api"
    "http://${SERVER_IP}:8080/api"
    "http://${SERVER_IP}:3000/api"
    "https://aladdin-ai.ru/api"
)

# Используем первый доступный URL, но пробуем HTTPS если HTTP редиректит
BASE_URL="${BASE_URLS[0]}"

# Если HTTP редиректит, используем HTTPS версию
if echo "$BASE_URL" | grep -q "http://"; then
    HTTPS_URL=$(echo "$BASE_URL" | sed 's|http://|https://|')
    # Проверяем HTTPS
    https_test=$(curl -s -o /dev/null -w "%{http_code}" -L --connect-timeout 3 --max-time 5 -k "${HTTPS_URL}/health" 2>&1 || echo "000")
    if [ "$https_test" != "000" ] && [ "$https_test" != "" ]; then
        BASE_URL="$HTTPS_URL"
        echo "Используем HTTPS: $BASE_URL"
    fi
fi

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║     🔌 ТЕСТИРОВАНИЕ API ИНТЕГРАЦИИ: 42 КОМПОНЕНТА                            ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Сервер: ${SERVER_IP}"
echo "📡 Base URL: ${BASE_URL}"
echo ""

# Список всех 42 компонентов
COMPONENTS=(
    # NetworkProtectionScreen (10)
    "crash_detection_agent"
    "roadside_assistance_agent"
    "emergency_response_bot"
    "emergency_event_manager"
    "phishing_protection_agent"
    "malware_detection_agent"
    "mobile_security_agent"
    "network_security_agent"
    "incident_response_agent"
    "password_security_agent"
    
    # ParentalControlScreen (5)
    "self_harm_detection_agent"
    "grooming_detection_agent"
    "online_predators_agent"
    "psychological_support_agent"
    "parental_control_bot"
    
    # AdvancedProtectionSettingsScreen (13)
    "telegram_security_bot"
    "whatsapp_security_bot"
    "instagram_security_bot"
    "max_messenger_security_bot"
    "gaming_security_bot"
    "browser_security_bot"
    "location_bubble_agent"
    "personal_data_cleanup_agent"
    "anti_tracker_agent"
    "dark_web_monitoring_agent"
    "russian_identity_theft_protection_agent"
    "ai_categories_agent"
    "driving_reports_agent"
    
    # SettingsScreen (5)
    "emergency_contacts_manager"
    "emergency_notifications_manager"
    "voice_control_manager"
    "russian_child_protection_compliance_manager"
    "russian_data_protection_compliance_manager"
    
    # Улучшение существующих (9)
    "family_notification_manager"
    "smart_notification_manager"
    "child_interface_manager"
    "elderly_interface_manager"
    "subscription_manager"
    "referral_manager"
    "qr_payment_manager"
    "analytics_manager"
    "report_manager"
)

# Функция для проверки статуса компонента
check_component_status() {
    local component_id=$1
    local url="${BASE_URL}/components/status/${component_id}"
    
    # Следовать редиректам и использовать HTTPS если нужно
    response=$(curl -s -L -w "\n%{http_code}" -X GET "${url}" \
        -H "Content-Type: application/json" \
        --connect-timeout 5 \
        --max-time 10 \
        -k 2>&1)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d' | head -c 200)
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✅${NC} ${component_id}: OK (HTTP $http_code)"
        if [ ${#body} -gt 0 ]; then
            echo "   Response: $body"
        fi
        return 0
    elif [ "$http_code" = "301" ] || [ "$http_code" = "302" ]; then
        # Попробуем HTTPS
        https_url=$(echo "$url" | sed 's|http://|https://|')
        https_response=$(curl -s -L -w "\n%{http_code}" -X GET "${https_url}" \
            -H "Content-Type: application/json" \
            --connect-timeout 5 \
            --max-time 10 \
            -k 2>&1)
        https_code=$(echo "$https_response" | tail -n1)
        https_body=$(echo "$https_response" | sed '$d' | head -c 200)
        
        if [ "$https_code" = "200" ] || [ "$https_code" = "201" ]; then
            echo -e "${GREEN}✅${NC} ${component_id}: OK (HTTPS, HTTP $https_code)"
            BASE_URL=$(echo "$BASE_URL" | sed 's|http://|https://|')
            return 0
        else
            echo -e "${YELLOW}⚠️${NC} ${component_id}: Redirect to HTTPS but failed (HTTP $https_code)"
            return 1
        fi
    else
        echo -e "${RED}❌${NC} ${component_id}: HTTP $http_code"
        if [ ${#body} -gt 0 ]; then
            echo "   Response: $body"
        fi
        return 1
    fi
}

# Функция для включения компонента
enable_component() {
    local component_id=$1
    local url="${BASE_URL}/components/enable/${component_id}"
    
    response=$(curl -s -w "\n%{http_code}" -X POST "${url}" \
        -H "Content-Type: application/json" \
        --connect-timeout 5 \
        --max-time 10 2>&1)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✅${NC} ${component_id}: Enabled"
        return 0
    else
        echo -e "${RED}❌${NC} ${component_id}: Enable failed (HTTP $http_code)"
        return 1
    fi
}

# Функция для выключения компонента
disable_component() {
    local component_id=$1
    local url="${BASE_URL}/components/disable/${component_id}"
    
    response=$(curl -s -w "\n%{http_code}" -X POST "${url}" \
        -H "Content-Type: application/json" \
        --connect-timeout 5 \
        --max-time 10 2>&1)
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✅${NC} ${component_id}: Disabled"
        return 0
    else
        echo -e "${RED}❌${NC} ${component_id}: Disable failed (HTTP $http_code)"
        return 1
    fi
}

# Проверка доступности сервера
echo "🔍 Проверка доступности сервера..."
echo "Пробуем разные варианты подключения..."

FOUND_URL=""
for url in "${BASE_URLS[@]}"; do
    echo "  Проверка: $url"
    http_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 --max-time 5 "${url}/health" 2>&1 || echo "000")
    if [ "$http_code" != "000" ] && [ "$http_code" != "" ]; then
        echo -e "  ${GREEN}✅${NC} Доступен (HTTP $http_code)"
        BASE_URL="$url"
        FOUND_URL="$url"
        break
    else
        echo -e "  ${RED}❌${NC} Недоступен"
    fi
done

if [ -z "$FOUND_URL" ]; then
    echo ""
    echo -e "${YELLOW}⚠️${NC} Не удалось найти доступный API endpoint"
    echo "Продолжаем с базовым URL: ${BASE_URL}"
    echo "Возможно, требуется авторизация или другой порт"
else
    echo ""
    echo -e "${GREEN}✅${NC} Найден доступный API: ${BASE_URL}"
fi
echo ""

echo ""
echo "📋 Тестирование всех 42 компонентов..."
echo ""

success_count=0
failure_count=0

# Тест 1: Проверка статуса всех компонентов
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ТЕСТ 1: Получение статуса компонентов"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for component in "${COMPONENTS[@]}"; do
    if check_component_status "$component"; then
        ((success_count++))
    else
        ((failure_count++))
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "ТЕСТ 2: Включение/выключение компонентов (первые 5 для примера)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Тестируем только первые 5 компонентов для toggle (чтобы не менять все настройки)
for i in {0..4}; do
    component="${COMPONENTS[$i]}"
    echo "Тестирование: $component"
    
    # Получить исходный статус
    initial_status=$(check_component_status "$component" 2>&1 | grep -o "enabled\|disabled" || echo "unknown")
    
    # Включить
    if enable_component "$component"; then
        sleep 1
        # Выключить
        if disable_component "$component"; then
            sleep 1
            # Вернуть исходное состояние
            if [ "$initial_status" = "enabled" ]; then
                enable_component "$component" > /dev/null 2>&1
            fi
            echo -e "${GREEN}✅${NC} $component: Toggle успешен"
        else
            echo -e "${YELLOW}⚠️${NC} $component: Disable не удался"
        fi
    else
        echo -e "${YELLOW}⚠️${NC} $component: Enable не удался"
    fi
    echo ""
done

# Итоговая статистика
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                          📊 ИТОГОВАЯ СТАТИСТИКА                             ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Всего компонентов: ${#COMPONENTS[@]}"
echo -e "Успешно: ${GREEN}${success_count}${NC}"
echo -e "Ошибок: ${RED}${failure_count}${NC}"
echo ""

success_rate=$(awk "BEGIN {printf \"%.1f\", (${success_count}/${#COMPONENTS[@]})*100}")
echo "Процент успеха: ${success_rate}%"

if [ "$success_rate" -ge 80 ]; then
    echo -e "${GREEN}✅ Тестирование пройдено успешно!${NC}"
    exit 0
else
    echo -e "${RED}❌ Тестирование не пройдено (требуется минимум 80%)${NC}"
    exit 1
fi

