#!/bin/bash
# Скрипт для переноса Identity Theft Protection на сервер и регистрации в SFM

set -e

# Конфигурация (измените под ваш сервер)
SERVER="${ALADDIN_SERVER:-your-server.com}"
SERVER_USER="${ALADDIN_SERVER_USER:-root}"
BACKEND_PATH="/opt/aladdin-backend"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================================================"
echo "🚀 ДЕПЛОЙ IDENTITY THEFT PROTECTION НА СЕРВЕР"
echo "================================================================================"
echo -e "${NC}"

# Проверка переменных окружения
if [ "$SERVER" == "your-server.com" ]; then
    echo -e "${YELLOW}⚠️  ВНИМАНИЕ: Укажите сервер через переменную окружения:${NC}"
    echo "   export ALADDIN_SERVER=your-server.com"
    echo "   export ALADDIN_SERVER_USER=root"
    echo ""
    read -p "Введите адрес сервера: " SERVER
    read -p "Введите пользователя (по умолчанию root): " SERVER_USER
    SERVER_USER=${SERVER_USER:-root}
fi

echo -e "${GREEN}📋 Информация о деплое:${NC}"
echo "   Сервер: $SERVER"
echo "   Пользователь: $SERVER_USER"
echo "   Путь на сервере: $BACKEND_PATH"
echo ""

# Шаг 1: Проверка существования файлов локально
echo -e "${BLUE}📦 Шаг 1: Проверка локальных файлов...${NC}"
FILES=(
    "security/ai_agents/russian_identity_theft_protection_agent.py"
    "security/api/routers/identity_theft_protection_router.py"
    "security/ai_agents/function_registry_entry_identity_theft_protection.json"
    "register_identity_theft_in_sfm.py"
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
ssh ${SERVER_USER}@${SERVER} << EOF
    mkdir -p ${BACKEND_PATH}/security/ai_agents
    mkdir -p ${BACKEND_PATH}/security/api/routers
    mkdir -p ${BACKEND_PATH}/data/sfm
    mkdir -p /tmp
    echo "✅ Директории созданы"
EOF
echo ""

# Шаг 3: Копирование файлов на сервер
echo -e "${BLUE}📤 Шаг 3: Копирование файлов на сервер...${NC}"
scp security/ai_agents/russian_identity_theft_protection_agent.py ${SERVER_USER}@${SERVER}:${BACKEND_PATH}/security/ai_agents/
echo "   ✅ Агент скопирован"

scp security/api/routers/identity_theft_protection_router.py ${SERVER_USER}@${SERVER}:${BACKEND_PATH}/security/api/routers/
echo "   ✅ Router скопирован"

scp security/ai_agents/function_registry_entry_identity_theft_protection.json ${SERVER_USER}@${SERVER}:/tmp/
echo "   ✅ Registry entry скопирован"

scp register_identity_theft_in_sfm.py ${SERVER_USER}@${SERVER}:/tmp/
echo "   ✅ Скрипт регистрации скопирован"
echo ""

# Шаг 4: Регистрация в SFM
echo -e "${BLUE}📝 Шаг 4: Регистрация в SFM...${NC}"
ssh ${SERVER_USER}@${SERVER} << 'EOF'
    cd /tmp
    python3 register_identity_theft_in_sfm.py
    echo ""
EOF
echo ""

# Шаг 5: Подсчет общего количества функций
echo -e "${BLUE}📊 Шаг 5: Подсчет общего количества функций в SFM...${NC}"
ssh ${SERVER_USER}@${SERVER} << 'EOF'
    python3 << 'PYEOF'
import json
from pathlib import Path

registry_path = Path("/opt/aladdin-backend/data/sfm/function_registry.json")

if not registry_path.exists():
    print("❌ Registry не найден")
    exit(1)

with open(registry_path, 'r', encoding='utf-8') as f:
    registry = json.load(f)

# Подсчет
if isinstance(registry, list):
    agents = registry
elif isinstance(registry, dict):
    agents = registry.get("agents", list(registry.values()) if "agents" not in registry else [])
else:
    agents = []

total_agents = len(agents)
total_functions = 0
agent_details = []

for agent in agents:
    if isinstance(agent, dict):
        agent_name = agent.get("name", "unknown")
        functions = agent.get("functions", [])
        func_count = len(functions)
        total_functions += func_count
        agent_details.append((agent_name, func_count))

print("=" * 80)
print("📊 СТАТИСТИКА SFM (ВСЕ АГЕНТЫ):")
print("=" * 80)
print(f"Всего агентов: {total_agents}")
print(f"Всего функций: {total_functions}")
print()
print("Детализация по агентам:")
for name, count in agent_details:
    print(f"  • {name}: {count} функций")
print("=" * 80)
PYEOF
EOF
echo ""

# Шаг 6: Интеграция в main.py (требует ручного вмешательства)
echo -e "${YELLOW}⚠️  Шаг 6: Интеграция в main.py${NC}"
echo "   Требуется добавить в main.py на сервере:"
echo ""
echo "   from security.api.routers.identity_theft_protection_router import router as identity_theft_router"
echo "   app.include_router(identity_theft_router, prefix=\"/api/identity-theft\", tags=[\"Identity Theft Protection\"])"
echo ""

# Шаг 7: Перезапуск сервисов
read -p "Перезапустить backend сервис? (y/n): " RESTART
if [ "$RESTART" == "y" ] || [ "$RESTART" == "Y" ]; then
    echo -e "${BLUE}🔄 Перезапуск сервисов...${NC}"
    ssh ${SERVER_USER}@${SERVER} << 'EOF'
        if systemctl list-units --type=service | grep -q aladdin-backend; then
            echo "   Перезапуск через systemctl..."
            systemctl restart aladdin-backend
            systemctl status aladdin-backend --no-pager | head -5
        elif command -v supervisorctl &> /dev/null; then
            echo "   Перезапуск через supervisorctl..."
            supervisorctl restart aladdin-backend
        else
            echo "   ⚠️  Не найден systemctl или supervisorctl"
            echo "   Перезапустите вручную!"
        fi
EOF
    echo ""
fi

echo -e "${GREEN}================================================================================"
echo "✅ ДЕПЛОЙ ЗАВЕРШЕН!"
echo "================================================================================"
echo -e "${NC}"
