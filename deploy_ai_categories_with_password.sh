#!/bin/bash
# Скрипт для переноса AI Categories Agent на сервер с паролем

set -e

# Конфигурация
SERVER="${ALADDIN_SERVER:-149.154.65.180}"
SERVER_USER="${ALADDIN_SERVER_USER:-Sergio675}"
SERVER_PASSWORD="${ALADDIN_SERVER_PASSWORD}"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================================================"
echo "🚀 ДЕПЛОЙ AI CATEGORIES AGENT НА СЕРВЕР"
echo "================================================================================"
echo -e "${NC}"

echo -e "${GREEN}📋 Информация о деплое:${NC}"
echo "   Сервер: $SERVER"
echo "   Пользователь: $SERVER_USER"
echo "   Путь на сервере: /opt/aladdin-backend"
echo ""

# Проверка наличия expect или sshpass
if ! command -v expect &> /dev/null && ! command -v sshpass &> /dev/null; then
    echo -e "${RED}❌ Требуется expect или sshpass для автоматического ввода пароля${NC}"
    echo "   Установите: brew install expect (macOS) или apt-get install expect (Linux)"
    exit 1
fi

# Функция для выполнения SSH команд с паролем
ssh_with_password() {
    local cmd="$1"
    if command -v sshpass &> /dev/null; then
        sshpass -p "$SERVER_PASSWORD" ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER} "$cmd"
    else
        expect << EOF
set timeout 30
spawn ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER} "$cmd"
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}
EOF
    fi
}

# Функция для SCP с паролем
scp_with_password() {
    local src="$1"
    local dst="$2"
    if command -v sshpass &> /dev/null; then
        sshpass -p "$SERVER_PASSWORD" scp -o StrictHostKeyChecking=no "$src" "${SERVER_USER}@${SERVER}:$dst"
    else
        expect << EOF
set timeout 60
spawn scp -o StrictHostKeyChecking=no "$src" ${SERVER_USER}@${SERVER}:$dst
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}
EOF
    fi
}

# Запрос пароля если не указан
if [ -z "$SERVER_PASSWORD" ]; then
    echo -e "${YELLOW}⚠️  Пароль не указан в переменной окружения${NC}"
    read -sp "Введите пароль для $SERVER_USER@$SERVER: " SERVER_PASSWORD
    echo ""
fi

# Шаг 1: Проверка локальных файлов
echo -e "${BLUE}📦 Шаг 1: Проверка локальных файлов...${NC}"
FILES=(
    "security/ai_agents/ai_categories_agent.py"
    "security/api/routers/ai_categories_router.py"
    "security/ai_agents/function_registry_entry_ai_categories.json"
    "register_ai_categories_in_sfm.py"
    "add_ai_categories_to_main.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "   ✅ $file"
    else
        echo -e "   ${RED}❌ $file не найден!${NC}"
        exit 1
    fi
done
echo ""

# Шаг 2: Создание директорий на сервере
echo -e "${BLUE}📁 Шаг 2: Создание директорий на сервере...${NC}"
ssh_with_password "mkdir -p /opt/aladdin-backend/security/ai_agents && mkdir -p /opt/aladdin-backend/security/api/routers && mkdir -p /opt/aladdin-backend/data/sfm && mkdir -p /tmp && echo '✅ Директории созданы'"
echo ""

# Шаг 3: Копирование файлов на сервер
echo -e "${BLUE}📤 Шаг 3: Копирование файлов на сервер...${NC}"
scp_with_password "security/ai_agents/ai_categories_agent.py" "/opt/aladdin-backend/security/ai_agents/"
echo "   ✅ Агент скопирован"

scp_with_password "security/api/routers/ai_categories_router.py" "/opt/aladdin-backend/security/api/routers/"
echo "   ✅ Router скопирован"

scp_with_password "security/ai_agents/function_registry_entry_ai_categories.json" "/tmp/"
echo "   ✅ Registry entry скопирован"

scp_with_password "register_ai_categories_in_sfm.py" "/tmp/"
echo "   ✅ Скрипт регистрации скопирован"

scp_with_password "add_ai_categories_to_main.py" "/tmp/"
echo "   ✅ Скрипт интеграции в main.py скопирован"
echo ""

# Шаг 4: Регистрация в SFM
echo -e "${BLUE}📝 Шаг 4: Регистрация в SFM...${NC}"
ssh_with_password "cd /tmp && python3 register_ai_categories_in_sfm.py <<< 'y'"
echo ""

# Шаг 5: Интеграция в main.py
echo -e "${BLUE}🔧 Шаг 5: Интеграция router в main.py...${NC}"
ssh_with_password "cd /tmp && python3 add_ai_categories_to_main.py"
echo ""

# Шаг 6: Подсчет функций в SFM
echo -e "${BLUE}📊 Шаг 6: Подсчет общего количества функций в SFM...${NC}"
ssh_with_password "python3 << 'PYEOF'
import json
from pathlib import Path

registry_path = Path('/opt/aladdin-backend/data/sfm/function_registry.json')

if not registry_path.exists():
    print('❌ Registry не найден')
    exit(1)

with open(registry_path, 'r', encoding='utf-8') as f:
    registry = json.load(f)

if isinstance(registry, list):
    agents = registry
elif isinstance(registry, dict):
    agents = registry.get('agents', list(registry.values()) if 'agents' not in registry else [])
else:
    agents = []

total_agents = len(agents)
total_functions = 0
agent_details = []

for agent in agents:
    if isinstance(agent, dict):
        agent_name = agent.get('name', 'unknown')
        functions = agent.get('functions', [])
        func_count = len(functions)
        total_functions += func_count
        agent_details.append((agent_name, func_count))

print('=' * 80)
print('📊 СТАТИСТИКА SFM (ВСЕ АГЕНТЫ):')
print('=' * 80)
print(f'Всего агентов: {total_agents}')
print(f'Всего функций: {total_functions}')
print()
print('Детализация по агентам:')
for name, count in agent_details:
    print(f'  • {name}: {count} функций')
print('=' * 80)
PYEOF
"
echo ""

# Шаг 7: Перезапуск сервиса
echo -e "${BLUE}🔄 Шаг 7: Перезапуск backend сервиса...${NC}"
ssh_with_password "
if systemctl list-units --type=service 2>/dev/null | grep -q aladdin-backend; then
    echo '   Перезапуск через systemctl...'
    systemctl restart aladdin-backend
    sleep 2
    systemctl status aladdin-backend --no-pager | head -5
elif command -v supervisorctl &> /dev/null; then
    echo '   Перезапуск через supervisorctl...'
    supervisorctl restart aladdin-backend
else
    echo '   ⚠️  Не найден systemctl или supervisorctl'
    echo '   Перезапустите вручную!'
fi
"
echo ""

# Шаг 8: Проверка health check
echo -e "${BLUE}🔍 Шаг 8: Проверка health check...${NC}"
sleep 3
ssh_with_password "curl -s http://localhost:8000/api/ai-categories/health 2>/dev/null | python3 -m json.tool || echo '⚠️  Health check недоступен (возможно сервис еще не перезапущен)'"
echo ""

echo -e "${GREEN}================================================================================"
echo "✅ ДЕПЛОЙ ЗАВЕРШЕН!"
echo "================================================================================"
echo -e "${NC}"
