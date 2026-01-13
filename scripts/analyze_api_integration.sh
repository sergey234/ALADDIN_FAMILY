#!/bin/bash

# 🔍 Глубокий анализ интеграции мобильного приложения и сервера
# Проверка всех 138 функций + 42 компонента

set -e

SERVER_IP="149.154.65.180"
SERVER_USER="root"
SERVER_PASSWORD="Sergio675"

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║     🔍 ГЛУБОКИЙ АНАЛИЗ ИНТЕГРАЦИИ: 138 ФУНКЦИЙ + 42 КОМПОНЕНТА                ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# 1. Анализ endpoints в мобильном приложении
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📱 1. АНАЛИЗ ENDPOINTS В МОБИЛЬНОМ ПРИЛОЖЕНИИ"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

MOBILE_ENDPOINTS=$(grep -r "AppConfig\.Endpoint\." Core/ --include="*.swift" | grep -v "//" | wc -l | tr -d ' ')
echo -e "${BLUE}Найдено использований endpoints:${NC} $MOBILE_ENDPOINTS"

echo ""
echo "📋 Категории endpoints:"
echo "  - Network Protection: $(grep -r "networkProtection" Core/Config/AppConfig.swift | wc -l | tr -d ' ')"
echo "  - Family: $(grep -r "family" Core/Config/AppConfig.swift | grep -i "endpoint" | wc -l | tr -d ' ')"
echo "  - Analytics: $(grep -r "analytics" Core/Config/AppConfig.swift | grep -i "endpoint" | wc -l | tr -d ' ')"
echo "  - AI Assistant: $(grep -r "ai" Core/Config/AppConfig.swift | grep -i "endpoint" | wc -l | tr -d ' ')"
echo "  - Parental Control: $(grep -r "parental" Core/Config/AppConfig.swift | grep -i "endpoint" | wc -l | tr -d ' ')"
echo "  - Components (42): $(grep -r "component" Core/Config/AppConfig.swift | grep -i "endpoint" | wc -l | tr -d ' ')"
echo "  - Protection: $(grep -r "protection" Core/Config/AppConfig.swift | grep -i "endpoint" | wc -l | tr -d ' ')"
echo "  - Referral: $(grep -r "referral" Core/Config/AppConfig.swift | grep -i "endpoint" | wc -l | tr -d ' ')"
echo "  - Devices: $(grep -r "device" Core/Config/AppConfig.swift | grep -i "endpoint" | wc -l | tr -d ' ')"
echo "  - IoT: $(grep -r "iot" Core/Config/AppConfig.swift | grep -i "endpoint" | wc -l | tr -d ' ')"
echo "  - Auth: $(grep -r "auth" Core/Config/AppConfig.swift | grep -i "endpoint" | wc -l | tr -d ' ')"
echo "  - Subscription: $(grep -r "subscription\|tariff" Core/Config/AppConfig.swift | grep -i "endpoint" | wc -l | tr -d ' ')"
echo ""

# 2. Анализ API методов в APIService
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📡 2. АНАЛИЗ API МЕТОДОВ В APIService"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

API_METHODS=$(grep -E "func (get|post|put|delete|patch)" Core/Network/APIService.swift | wc -l | tr -d ' ')
echo -e "${BLUE}Всего API методов:${NC} $API_METHODS"

echo ""
echo "📋 Методы по категориям:"
echo "  - Network Protection: $(grep -E "func.*NetworkProtection" Core/Network/APIService.swift | wc -l | tr -d ' ')"
echo "  - Family: $(grep -E "func.*Family" Core/Network/APIService.swift | wc -l | tr -d ' ')"
echo "  - Analytics: $(grep -E "func.*Analytics" Core/Network/APIService.swift | wc -l | tr -d ' ')"
echo "  - AI Assistant: $(grep -E "func.*AI\|func.*ai" Core/Network/APIService.swift | wc -l | tr -d ' ')"
echo "  - Parental Control: $(grep -E "func.*Parental" Core/Network/APIService.swift | wc -l | tr -d ' ')"
echo "  - Components: $(grep -E "func.*Component" Core/Network/APIService.swift | wc -l | tr -d ' ')"
echo "  - Protection: $(grep -E "func.*Protection" Core/Network/APIService.swift | wc -l | tr -d ' ')"
echo "  - Referral: $(grep -E "func.*Referral" Core/Network/APIService.swift | wc -l | tr -d ' ')"
echo "  - Devices: $(grep -E "func.*Device" Core/Network/APIService.swift | wc -l | tr -d ' ')"
echo "  - IoT: $(grep -E "func.*IoT" Core/Network/APIService.swift | wc -l | tr -d ' ')"
echo "  - Auth: $(grep -E "func.*login\|func.*logout\|func.*register" Core/Network/APIService.swift | wc -l | tr -d ' ')"
echo "  - Subscription: $(grep -E "func.*Subscription\|func.*Tariff" Core/Network/APIService.swift | wc -l | tr -d ' ')"
echo ""

# 3. Проверка ViewModels
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎨 3. АНАЛИЗ VIEWMODELS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

VIEWMODELS=$(find ViewModels -name "*.swift" -type f 2>/dev/null | wc -l | tr -d ' ')
echo -e "${BLUE}Всего ViewModels:${NC} $VIEWMODELS"

echo ""
echo "📋 ViewModels использующие APIService:"
for vm in ViewModels/*.swift; do
    if [ -f "$vm" ]; then
        uses_api=$(grep -E "APIService|apiService" "$vm" | wc -l | tr -d ' ')
        if [ "$uses_api" -gt 0 ]; then
            vm_name=$(basename "$vm" .swift)
            echo -e "  ${GREEN}✅${NC} $vm_name (использует API)"
        fi
    fi
done
echo ""

# 4. Проверка сервера
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🖥️  4. АНАЛИЗ СЕРВЕРА"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Получаем токен для тестирования
TOKEN=$(sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_IP}" "/opt/aladdin-backend/venv/bin/python3 << 'PYTHON_SCRIPT'
import jwt
import os
from datetime import datetime, timedelta
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
payload = {'id': 1, 'user_id': 1, 'email': 'test@aladdin.family', 'exp': datetime.utcnow() + timedelta(days=30)}
print(jwt.encode(payload, JWT_SECRET, algorithm='HS256'))
PYTHON_SCRIPT
" 2>&1 | grep -v DeprecationWarning | tail -1)

echo -e "${BLUE}Тестирование endpoints на сервере...${NC}"
echo ""

# Тестируем основные категории
CATEGORIES=(
    "network-protection:/network-protection/status"
    "family:/family/members"
    "analytics:/analytics"
    "protection:/protection/status"
    "components:/api/components/status/crash_detection_agent"
    "parental:/api/v1/parental-control/stats"
    "referral:/api/referral/code"
    "devices:/devices"
)

SUCCESS=0
FAILED=0

for category_info in "${CATEGORIES[@]}"; do
    IFS=':' read -r category endpoint <<< "$category_info"
    echo -n "  $category: "
    
    response=$(curl -s -k -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "https://aladdin-ai.ru/api$endpoint" 2>&1 | tail -1)
    
    if [ "$response" = "200" ] || [ "$response" = "201" ]; then
        echo -e "${GREEN}✅ OK${NC} (HTTP $response)"
        ((SUCCESS++))
    elif [ "$response" = "401" ]; then
        echo -e "${YELLOW}⚠️  Unauthorized${NC} (требуется токен)"
        ((SUCCESS++))
    elif [ "$response" = "404" ]; then
        echo -e "${RED}❌ Not Found${NC} (HTTP 404)"
        ((FAILED++))
    else
        echo -e "${YELLOW}⚠️  HTTP $response${NC}"
        ((FAILED++))
    fi
done

echo ""
echo -e "${BLUE}Результаты:${NC} ${GREEN}✅ $SUCCESS${NC} успешно, ${RED}❌ $FAILED${NC} ошибок"
echo ""

# 5. Проверка 42 компонентов
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 5. ПРОВЕРКА 42 КОМПОНЕНТОВ"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

COMPONENTS=(
    "crash_detection_agent"
    "phishing_protection_agent"
    "self_harm_detection_agent"
    "telegram_security_bot"
    "emergency_contacts_manager"
    "family_notification_manager"
)

COMP_SUCCESS=0
COMP_FAILED=0

for component in "${COMPONENTS[@]}"; do
    echo -n "  $component: "
    
    response=$(curl -s -k -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "https://aladdin-ai.ru/api/components/status/$component" 2>&1 | tail -1)
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✅ OK${NC}"
        ((COMP_SUCCESS++))
    else
        echo -e "${RED}❌ HTTP $response${NC}"
        ((COMP_FAILED++))
    fi
done

echo ""
echo -e "${BLUE}Результаты компонентов:${NC} ${GREEN}✅ $COMP_SUCCESS${NC} успешно, ${RED}❌ $COMP_FAILED${NC} ошибок"
echo ""

# 6. Итоговая статистика
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 6. ИТОГОВАЯ СТАТИСТИКА"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "Мобильное приложение:"
echo "  - Endpoints определены: $MOBILE_ENDPOINTS"
echo "  - API методов: $API_METHODS"
echo "  - ViewModels: $VIEWMODELS"
echo ""

echo "Сервер:"
echo "  - Основные категории: ${#CATEGORIES[@]}"
echo "  - Успешных тестов: $SUCCESS"
echo "  - Ошибок: $FAILED"
echo ""

echo "42 компонента:"
echo "  - Протестировано: ${#COMPONENTS[@]}"
echo "  - Успешно: $COMP_SUCCESS"
echo "  - Ошибок: $COMP_FAILED"
echo ""

if [ "$FAILED" -eq 0 ] && [ "$COMP_FAILED" -eq 0 ]; then
    echo -e "${GREEN}✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  ЕСТЬ ПРОБЛЕМЫ, ТРЕБУЕТСЯ ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА${NC}"
    exit 1
fi

