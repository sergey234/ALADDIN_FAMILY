#!/bin/bash
# Интерактивный деплой AI Categories Agent

set -e

SERVER="149.154.65.180"
SERVER_USER="Sergio675"
BACKEND_PATH="/opt/aladdin-backend"

echo "🚀 ДЕПЛОЙ AI CATEGORIES AGENT НА СЕРВЕР"
echo "Сервер: $SERVER"
echo "Пользователь: $SERVER_USER"
echo ""

# Запрос пароля
read -sp "Введите пароль для $SERVER_USER@$SERVER: " SERVER_PASSWORD
echo ""
echo ""

# Проверка файлов
echo "📦 Проверка локальных файлов..."
FILES=(
    "security/ai_agents/ai_categories_agent.py"
    "security/api/routers/ai_categories_router.py"
    "security/ai_agents/function_registry_entry_ai_categories.json"
    "register_ai_categories_in_sfm.py"
    "add_ai_categories_to_main.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file не найден!"
        exit 1
    fi
done
echo ""

# Создание директорий
echo "📁 Создание директорий на сервере..."
expect << EOF
set timeout 30
spawn ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER} "mkdir -p ${BACKEND_PATH}/security/ai_agents && mkdir -p ${BACKEND_PATH}/security/api/routers && mkdir -p ${BACKEND_PATH}/data/sfm && mkdir -p /tmp && echo '✅ Директории созданы'"
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
echo ""

# Копирование файлов
echo "📤 Копирование файлов на сервер..."

expect << EOF
set timeout 60
spawn scp -o StrictHostKeyChecking=no security/ai_agents/ai_categories_agent.py ${SERVER_USER}@${SERVER}:${BACKEND_PATH}/security/ai_agents/
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
echo "   ✅ Агент скопирован"

expect << EOF
set timeout 60
spawn scp -o StrictHostKeyChecking=no security/api/routers/ai_categories_router.py ${SERVER_USER}@${SERVER}:${BACKEND_PATH}/security/api/routers/
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        exp_continue
    }
    eof
}
EOF
echo "   ✅ Router скопирован"

expect << EOF
set timeout 60
spawn scp -o StrictHostKeyChecking=no security/ai_agents/function_registry_entry_ai_categories.json ${SERVER_USER}@${SERVER}:/tmp/
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        exp_continue
    }
    eof
}
EOF
echo "   ✅ Registry entry скопирован"

expect << EOF
set timeout 60
spawn scp -o StrictHostKeyChecking=no register_ai_categories_in_sfm.py ${SERVER_USER}@${SERVER}:/tmp/
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        exp_continue
    }
    eof
}
EOF
echo "   ✅ Скрипт регистрации скопирован"

expect << EOF
set timeout 60
spawn scp -o StrictHostKeyChecking=no add_ai_categories_to_main.py ${SERVER_USER}@${SERVER}:/tmp/
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        exp_continue
    }
    eof
}
EOF
echo "   ✅ Скрипт интеграции скопирован"
echo ""

# Регистрация в SFM
echo "📝 Регистрация в SFM..."
expect << EOF
set timeout 60
spawn ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER} "cd /tmp && echo 'y' | python3 register_ai_categories_in_sfm.py"
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        exp_continue
    }
    eof
}
EOF
echo ""

# Интеграция в main.py
echo "🔧 Интеграция router в main.py..."
expect << EOF
set timeout 60
spawn ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER} "cd /tmp && python3 add_ai_categories_to_main.py"
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        exp_continue
    }
    eof
}
EOF
echo ""

# Подсчет функций
echo "📊 Подсчет функций в SFM..."
expect << EOF
set timeout 60
spawn ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER} "python3 << 'PYEOF'
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
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        exp_continue
    }
    eof
}
EOF
echo ""

# Перезапуск сервиса
echo "🔄 Перезапуск backend сервиса..."
expect << EOF
set timeout 60
spawn ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER} "
if systemctl list-units --type=service 2>/dev/null | grep -q aladdin-backend; then
    systemctl restart aladdin-backend
    sleep 2
    systemctl status aladdin-backend --no-pager | head -5
elif command -v supervisorctl &> /dev/null; then
    supervisorctl restart aladdin-backend
else
    echo '⚠️  Перезапустите вручную!'
fi
"
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        exp_continue
    }
    eof
}
EOF
echo ""

# Health check
echo "🔍 Проверка health check..."
sleep 3
expect << EOF
set timeout 30
spawn ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER} "curl -s http://localhost:8000/api/ai-categories/health 2>/dev/null | python3 -m json.tool || echo '⚠️  Health check недоступен'"
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        exp_continue
    }
    eof
}
EOF
echo ""

echo "✅ ДЕПЛОЙ ЗАВЕРШЕН!"
