#!/bin/bash
# Скрипт деплоя Location Bubble Agent на сервер
# Дата: 12 декабря 2025

set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Конфигурация сервера
SERVER="149.154.65.180"
SERVER_USER="root"
SERVER_PATH="/opt/aladdin-backend"

echo -e "${GREEN}=== ДЕПЛОЙ LOCATION BUBBLE AGENT ===${NC}"
echo ""

# Проверка файлов локально
echo -e "${YELLOW}1. Проверка файлов локально...${NC}"
if [ ! -f "security/ai_agents/location_bubble_agent.py" ]; then
    echo -e "${RED}❌ Файл location_bubble_agent.py не найден!${NC}"
    exit 1
fi

if [ ! -f "security/api/routers/location_bubble_router.py" ]; then
    echo -e "${RED}❌ Файл location_bubble_router.py не найден!${NC}"
    exit 1
fi

if [ ! -f "security/ai_agents/function_registry_entry_location_bubble.json" ]; then
    echo -e "${RED}❌ Файл function_registry_entry_location_bubble.json не найден!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Все файлы найдены${NC}"
echo ""

# Копирование файлов на сервер
echo -e "${YELLOW}2. Копирование файлов на сервер...${NC}"

echo "  - Копирование location_bubble_agent.py..."
scp security/ai_agents/location_bubble_agent.py \
    ${SERVER_USER}@${SERVER}:${SERVER_PATH}/security/ai_agents/

echo "  - Копирование location_bubble_router.py..."
scp security/api/routers/location_bubble_router.py \
    ${SERVER_USER}@${SERVER}:${SERVER_PATH}/security/api/routers/

echo "  - Копирование function_registry_entry_location_bubble.json..."
scp security/ai_agents/function_registry_entry_location_bubble.json \
    ${SERVER_USER}@${SERVER}:/tmp/

echo -e "${GREEN}✅ Все файлы скопированы${NC}"
echo ""

# Регистрация в SFM
echo -e "${YELLOW}3. Регистрация в SFM...${NC}"
echo "  Выполните на сервере:"
echo "  ssh ${SERVER_USER}@${SERVER}"
echo "  cd /tmp"
echo "  python3 register_location_bubble_in_sfm.py"
echo ""

# Интеграция в main.py
echo -e "${YELLOW}4. Интеграция в main.py...${NC}"
echo "  Выполните на сервере:"
echo "  python3 add_location_bubble_to_main.py"
echo ""

echo -e "${GREEN}=== ДЕПЛОЙ ЗАВЕРШЕН ===${NC}"
echo ""
echo "Следующие шаги:"
echo "1. Подключитесь к серверу: ssh ${SERVER_USER}@${SERVER}"
echo "2. Зарегистрируйте в SFM: python3 /tmp/register_location_bubble_in_sfm.py"
echo "3. Интегрируйте в main.py: python3 /tmp/add_location_bubble_to_main.py"
echo "4. Проверьте работу: curl http://localhost:8000/api/location/bubble/health"
