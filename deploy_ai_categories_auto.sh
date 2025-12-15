#!/usr/bin/env expect
# Автоматический деплой AI Categories Agent с паролем

set timeout 300
set SERVER "149.154.65.180"
set SERVER_USER "Sergio675"
set SERVER_PASSWORD [lindex $argv 0]

if {[llength $argv] == 0} {
    puts "Использование: ./deploy_ai_categories_auto.sh <пароль>"
    exit 1
}

puts "🚀 ДЕПЛОЙ AI CATEGORIES AGENT НА СЕРВЕР"
puts "Сервер: $SERVER"
puts "Пользователь: $SERVER_USER"
puts ""

# Шаг 1: Проверка файлов
puts "📦 Шаг 1: Проверка локальных файлов..."
set files {
    "security/ai_agents/ai_categories_agent.py"
    "security/api/routers/ai_categories_router.py"
    "security/ai_agents/function_registry_entry_ai_categories.json"
    "register_ai_categories_in_sfm.py"
    "add_ai_categories_to_main.py"
}

foreach file $files {
    if {[file exists $file]} {
        puts "   ✅ $file"
    } else {
        puts "   ❌ $file не найден!"
        exit 1
    }
}
puts ""

# Шаг 2: Создание директорий
puts "📁 Шаг 2: Создание директорий на сервере..."
spawn ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER} "mkdir -p /opt/aladdin-backend/security/ai_agents && mkdir -p /opt/aladdin-backend/security/api/routers && mkdir -p /opt/aladdin-backend/data/sfm && mkdir -p /tmp && echo '✅ Директории созданы'"
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
puts ""

# Шаг 3: Копирование файлов
puts "📤 Шаг 3: Копирование файлов на сервер..."

spawn scp -o StrictHostKeyChecking=no security/ai_agents/ai_categories_agent.py ${SERVER_USER}@${SERVER}:/opt/aladdin-backend/security/ai_agents/
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
puts "   ✅ Агент скопирован"

spawn scp -o StrictHostKeyChecking=no security/api/routers/ai_categories_router.py ${SERVER_USER}@${SERVER}:/opt/aladdin-backend/security/api/routers/
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        exp_continue
    }
    eof
}
puts "   ✅ Router скопирован"

spawn scp -o StrictHostKeyChecking=no security/ai_agents/function_registry_entry_ai_categories.json ${SERVER_USER}@${SERVER}:/tmp/
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        exp_continue
    }
    eof
}
puts "   ✅ Registry entry скопирован"

spawn scp -o StrictHostKeyChecking=no register_ai_categories_in_sfm.py ${SERVER_USER}@${SERVER}:/tmp/
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        exp_continue
    }
    eof
}
puts "   ✅ Скрипт регистрации скопирован"

spawn scp -o StrictHostKeyChecking=no add_ai_categories_to_main.py ${SERVER_USER}@${SERVER}:/tmp/
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        exp_continue
    }
    eof
}
puts "   ✅ Скрипт интеграции скопирован"
puts ""

# Шаг 4: Регистрация в SFM
puts "📝 Шаг 4: Регистрация в SFM..."
spawn ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER} "cd /tmp && echo 'y' | python3 register_ai_categories_in_sfm.py"
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        exp_continue
    }
    eof
}
puts ""

# Шаг 5: Интеграция в main.py
puts "🔧 Шаг 5: Интеграция router в main.py..."
spawn ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER} "cd /tmp && python3 add_ai_categories_to_main.py"
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        exp_continue
    }
    eof
}
puts ""

# Шаг 6: Подсчет функций
puts "📊 Шаг 6: Подсчет функций в SFM..."
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
puts ""

# Шаг 7: Перезапуск сервиса
puts "🔄 Шаг 7: Перезапуск backend сервиса..."
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
puts ""

# Шаг 8: Health check
puts "🔍 Шаг 8: Проверка health check..."
spawn ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER} "sleep 3 && curl -s http://localhost:8000/api/ai-categories/health 2>/dev/null | python3 -m json.tool || echo '⚠️  Health check недоступен'"
expect {
    "password:" {
        send "$SERVER_PASSWORD\r"
        exp_continue
    }
    eof
}
puts ""

puts "✅ ДЕПЛОЙ ЗАВЕРШЕН!"
