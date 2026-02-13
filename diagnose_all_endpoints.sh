#!/bin/bash

# 🔍 СКРИПТ ДИАГНОСТИКИ ВСЕХ 331 ENDPOINT'А
# Дата: 2026-02-11
# Цель: Проверить каждый endpoint на существование, подключение и работу

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Конфигурация
SERVER_IP="149.154.65.180"
SERVER_PORT="8002"
BASE_URL="http://${SERVER_IP}:${SERVER_PORT}"
SSH_USER="root"
SSH_PASS="Sergio675"
SERVER_PATH="/opt/aladdin-backend"

# Файлы результатов
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="endpoints_diagnosis_${TIMESTAMP}"
mkdir -p "$RESULTS_DIR"

DIAGNOSIS_REPORT="${RESULTS_DIR}/diagnosis_report.json"
SUMMARY_REPORT="${RESULTS_DIR}/summary_report.md"
DETAILED_REPORT="${RESULTS_DIR}/detailed_report.md"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🔍 ДИАГНОСТИКА ВСЕХ 331 ENDPOINT'А${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Инициализация JSON отчета
echo "{" > "$DIAGNOSIS_REPORT"
echo "  \"diagnosis_date\": \"$(date -Iseconds)\"," >> "$DIAGNOSIS_REPORT"
echo "  \"server\": \"${SERVER_IP}:${SERVER_PORT}\"," >> "$DIAGNOSIS_REPORT"
echo "  \"total_endpoints\": 331," >> "$DIAGNOSIS_REPORT"
echo "  \"endpoints\": [" >> "$DIAGNOSIS_REPORT"

# Функция для проверки подключения к серверу
check_server_connection() {
    echo -e "${BLUE}📡 Проверка подключения к серверу...${NC}"
    
    if sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no "$SSH_USER@$SERVER_IP" "test -d $SERVER_PATH" 2>/dev/null; then
        echo -e "${GREEN}✅ Подключение к серверу успешно${NC}"
        return 0
    else
        echo -e "${RED}❌ Не удалось подключиться к серверу${NC}"
        return 1
    fi
}

# Функция для проверки существования функции на сервере
check_function_exists() {
    local function_name=$1
    local search_path=$2
    
    sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no "$SSH_USER@$SERVER_IP" \
        "cd $SERVER_PATH && grep -r 'def ${function_name}' ${search_path} 2>/dev/null | head -1" | grep -q "def ${function_name}" && return 0 || return 1
}

# Функция для проверки FastAPI endpoint в роутере
check_endpoint_in_router() {
    local method=$1
    local path=$2
    local router_file=$3
    
    sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no "$SSH_USER@$SERVER_IP" \
        "cd $SERVER_PATH && grep -E '@router\.${method}.*[\"']${path}[\"']' ${router_file} 2>/dev/null" | grep -q "${path}" && return 0 || return 1
}

# Функция для проверки подключения роутера в main.py
check_router_connected() {
    local router_name=$1
    
    sshpass -p "$SSH_PASS" ssh -o StrictHostKeyChecking=no "$SSH_USER@$SERVER_IP" \
        "cd $SERVER_PATH && grep -E 'include_router.*${router_name}|from.*${router_name}' main.py 2>/dev/null" | grep -q "${router_name}" && return 0 || return 1
}

# Функция для проверки видимости в OpenAPI
check_openapi_visibility() {
    local method=$1
    local path=$2
    
    curl -s "${BASE_URL}/openapi.json" | jq -r ".paths.\"${path}\".${method,,}" 2>/dev/null | grep -q "." && return 0 || return 1
}

# Функция для проверки HTTP работы endpoint'а
check_http_work() {
    local method=$1
    local path=$2
    local token=$3
    
    local http_code
    if [ "$method" = "GET" ]; then
        http_code=$(curl -s -o /dev/null -w "%{http_code}" \
            -X GET "${BASE_URL}${path}" \
            ${token:+-H "Authorization: Bearer ${token}"})
    else
        http_code=$(curl -s -o /dev/null -w "%{http_code}" \
            -X "$method" "${BASE_URL}${path}" \
            -H "Content-Type: application/json" \
            -d '{}' \
            ${token:+-H "Authorization: Bearer ${token}"})
    fi
    
    # 200, 201, 422 (валидация) считаются успешными
    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ] || [ "$http_code" = "422" ]; then
        echo "$http_code"
        return 0
    elif [ "$http_code" = "401" ] || [ "$http_code" = "403" ]; then
        echo "$http_code"
        return 2  # Требует авторизацию
    elif [ "$http_code" = "404" ]; then
        echo "$http_code"
        return 1  # Не найден
    else
        echo "$http_code"
        return 1  # Ошибка
    fi
}

# Функция для диагностики одного endpoint'а
diagnose_endpoint() {
    local endpoint_num=$1
    local method=$2
    local path=$3
    local category=$4
    local router_file=$5
    local function_name=$6
    
    echo -e "${YELLOW}Проверка endpoint #${endpoint_num}: ${method} ${path}${NC}"
    
    # Инициализация результата
    local function_exists=false
    local endpoint_exists=false
    local router_connected=false
    local openapi_visible=false
    local http_works=false
    local http_code=""
    local status="unknown"
    local problems=()
    local solutions=()
    
    # 1. Проверка существования функции
    if [ -n "$function_name" ]; then
        if check_function_exists "$function_name" "security/ app/"; then
            function_exists=true
            echo -e "  ${GREEN}✅ Функция существует${NC}"
        else
            echo -e "  ${RED}❌ Функция не найдена${NC}"
            problems+=("Функция ${function_name} не найдена")
        fi
    else
        echo -e "  ${YELLOW}⚠️  Имя функции не указано${NC}"
    fi
    
    # 2. Проверка FastAPI endpoint в роутере
    if [ -n "$router_file" ]; then
        if check_endpoint_in_router "$method" "$path" "$router_file"; then
            endpoint_exists=true
            echo -e "  ${GREEN}✅ FastAPI endpoint найден в роутере${NC}"
        else
            echo -e "  ${RED}❌ FastAPI endpoint не найден в роутере${NC}"
            problems+=("FastAPI endpoint не добавлен в ${router_file}")
            solutions+=("Добавить @router.${method,,}(\"${path}\") в ${router_file}")
        fi
    else
        echo -e "  ${YELLOW}⚠️  Файл роутера не указан${NC}"
    fi
    
    # 3. Проверка подключения роутера
    if [ -n "$router_file" ]; then
        local router_name=$(basename "$router_file" .py)
        if check_router_connected "$router_name"; then
            router_connected=true
            echo -e "  ${GREEN}✅ Роутер подключен в main.py${NC}"
        else
            echo -e "  ${RED}❌ Роутер не подключен в main.py${NC}"
            problems+=("Роутер ${router_name} не подключен в main.py")
            solutions+=("Добавить app.include_router(${router_name}) в main.py")
        fi
    fi
    
    # 4. Проверка видимости в OpenAPI
    if check_openapi_visibility "$method" "$path"; then
        openapi_visible=true
        echo -e "  ${GREEN}✅ Виден в OpenAPI${NC}"
    else
        echo -e "  ${YELLOW}⚠️  Не виден в OpenAPI (может требовать авторизацию)${NC}"
    fi
    
    # 5. Проверка HTTP работы
    # Сначала без токена
    http_code=$(check_http_work "$method" "$path" "")
    local http_result=$?
    
    if [ $http_result -eq 0 ]; then
        http_works=true
        status="working"
        echo -e "  ${GREEN}✅ HTTP работает (код: ${http_code})${NC}"
    elif [ $http_result -eq 2 ]; then
        # Требует авторизацию - это нормально
        status="requires_auth"
        echo -e "  ${YELLOW}⚠️  Требует авторизацию (код: ${http_code})${NC}"
    else
        status="not_working"
        echo -e "  ${RED}❌ HTTP не работает (код: ${http_code})${NC}"
        problems+=("HTTP запрос возвращает ${http_code}")
    fi
    
    # Определение финального статуса
    if [ "$status" = "working" ] || [ "$status" = "requires_auth" ]; then
        if [ "$endpoint_exists" = true ] && [ "$router_connected" = true ]; then
            status="✅ working"
        else
            status="⚠️ partial"
        fi
    else
        status="❌ not_working"
    fi
    
    # Добавление в JSON отчет
    if [ $endpoint_num -gt 1 ]; then
        echo "," >> "$DIAGNOSIS_REPORT"
    fi
    
    echo "    {" >> "$DIAGNOSIS_REPORT"
    echo "      \"number\": ${endpoint_num}," >> "$DIAGNOSIS_REPORT"
    echo "      \"method\": \"${method}\"," >> "$DIAGNOSIS_REPORT"
    echo "      \"path\": \"${path}\"," >> "$DIAGNOSIS_REPORT"
    echo "      \"category\": \"${category}\"," >> "$DIAGNOSIS_REPORT"
    echo "      \"router_file\": \"${router_file:-null}\"," >> "$DIAGNOSIS_REPORT"
    echo "      \"function_name\": \"${function_name:-null}\"," >> "$DIAGNOSIS_REPORT"
    echo "      \"function_exists\": ${function_exists}," >> "$DIAGNOSIS_REPORT"
    echo "      \"endpoint_exists\": ${endpoint_exists}," >> "$DIAGNOSIS_REPORT"
    echo "      \"router_connected\": ${router_connected}," >> "$DIAGNOSIS_REPORT"
    echo "      \"openapi_visible\": ${openapi_visible}," >> "$DIAGNOSIS_REPORT"
    echo "      \"http_works\": ${http_works}," >> "$DIAGNOSIS_REPORT"
    echo "      \"http_code\": \"${http_code}\"," >> "$DIAGNOSIS_REPORT"
    echo "      \"status\": \"${status}\"," >> "$DIAGNOSIS_REPORT"
    echo "      \"problems\": $(printf '%s\n' "${problems[@]}" | jq -R . | jq -s .)," >> "$DIAGNOSIS_REPORT"
    echo "      \"solutions\": $(printf '%s\n' "${solutions[@]}" | jq -R . | jq -s .)" >> "$DIAGNOSIS_REPORT"
    echo "    }" >> "$DIAGNOSIS_REPORT"
    
    echo ""
}

# Основная функция диагностики
main() {
    # Проверка подключения к серверу
    if ! check_server_connection; then
        echo -e "${RED}❌ Не удалось подключиться к серверу. Проверьте настройки.${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}📋 Начало диагностики всех endpoint'ов...${NC}"
    echo ""
    
    # Список критичных endpoint'ов для начала
    # TODO: Загрузить полный список из файла
    
    # Критичные endpoint'ы
    diagnose_endpoint 1 "POST" "/api/family/create" "Family" "app/routers/family.py" "create_family"
    diagnose_endpoint 2 "POST" "/api/auth/login-by-recovery-code" "Authentication" "app/routers/auth_router.py" "login_by_recovery_code"
    
    # Закрытие JSON
    echo "  ]" >> "$DIAGNOSIS_REPORT"
    echo "}" >> "$DIAGNOSIS_REPORT"
    
    echo -e "${GREEN}✅ Диагностика завершена!${NC}"
    echo -e "${BLUE}📊 Результаты сохранены в: ${RESULTS_DIR}${NC}"
}

# Запуск
main
