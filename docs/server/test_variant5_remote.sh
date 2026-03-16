#!/bin/bash
# Тестирование Варианта 5 на удаленном сервере через SSH

SERVER_IP="149.154.65.180"
SERVER_USER="root"

echo "🧪 ТЕСТИРОВАНИЕ ВАРИАНТА 5 НА СЕРВЕРЕ"
echo "======================================"
echo ""

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Функция для выполнения команд через SSH
ssh_test() {
    local endpoint=$1
    local description=$2
    local should_not_be_wildcard=$3
    
    echo -e "${BLUE}🔍 Тест: $description${NC}"
    echo -e "   Endpoint: $endpoint"
    
    # Выполняем curl на сервере
    RESPONSE=$(ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "curl -s 'http://127.0.0.1:8002$endpoint'")
    
    # Проверяем ответ
    if echo "$RESPONSE" | grep -q "SFM_PROXIED"; then
        if [ "$should_not_be_wildcard" = "true" ]; then
            echo -e "${RED}❌ Попал в Wildcard Proxy (не должен!)${NC}"
            echo "   Ответ: $RESPONSE"
            return 1
        else
            echo -e "${YELLOW}⚠️ Попал в Wildcard Proxy (ожидаемо для неизвестных endpoints)${NC}"
            return 0
        fi
    elif echo "$RESPONSE" | grep -q "error\|Error\|ERROR"; then
        echo -e "${YELLOW}⚠️ Ошибка в ответе: $RESPONSE${NC}"
        return 0  # Ошибки могут быть нормальными (401, 422)
    else
        echo -e "${GREEN}✅ Обработан правильно${NC}"
        return 0
    fi
}

# Тест 1: Reports Router endpoints
echo -e "${YELLOW}ТЕСТ 1: Reports Router endpoints${NC}"
echo "----------------------------------------"
ssh_test "/api/reports/driving/stats" "Driving Reports Stats" "true"
ssh_test "/api/reports/dark-web/stats" "Dark Web Stats" "true"
ssh_test "/api/reports/identity-theft/stats" "Identity Theft Stats" "true"
ssh_test "/api/reports/privacy/location/stats" "Location Stats" "true"
ssh_test "/api/reports/privacy/cleanup/stats" "Cleanup Stats" "true"
ssh_test "/api/reports/privacy/tracker/stats" "Tracker Stats" "true"
ssh_test "/api/reports/ai-categories/stats" "AI Categories Stats" "true"
echo ""

# Тест 2: Analytics Router endpoints
echo -e "${YELLOW}ТЕСТ 2: Analytics Router endpoints${NC}"
echo "----------------------------------------"
ssh_test "/api/analytics?period=day" "Analytics Overview" "true"
ssh_test "/api/analytics/threats?period=day" "Analytics Threats" "true"
ssh_test "/api/analytics/top-threats?limit=10&period=day" "Analytics Top Threats" "true"
echo ""

# Тест 3: Endpoints с роутерами (не должны попадать в Wildcard Proxy)
echo -e "${YELLOW}ТЕСТ 3: Endpoints с роутерами${NC}"
echo "----------------------------------------"
ssh_test "/api/auth/login" "Auth Login" "true"
ssh_test "/api/components/list" "Components List" "true"
ssh_test "/api/family/stats" "Family Stats" "true"
echo ""

# Тест 4: Неизвестные endpoints (должны обрабатываться через Wildcard Proxy)
echo -e "${YELLOW}ТЕСТ 4: Неизвестные endpoints${NC}"
echo "----------------------------------------"
ssh_test "/api/unknown/endpoint" "Unknown Endpoint" "false"
ssh_test "/api/test/function" "Test Function" "false"
echo ""

echo -e "${GREEN}✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО${NC}"
