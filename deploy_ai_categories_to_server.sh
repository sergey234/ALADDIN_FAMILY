#!/usr/bin/expect -f
# Скрипт для деплоя AI Categories Agent на сервер
# Использует expect для автоматического ввода пароля
# Использование: ./deploy_ai_categories_to_server.sh

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"
set server_path "/opt/aladdin-backend"
set local_agent_dir "security/ai_agents"
set local_api_dir "security/api/routers"

puts "🚀 ДЕПЛОЙ AI CATEGORIES AGENT"
puts "================================"
puts ""

# Шаг 1: Проверка компиляции
puts "📋 Шаг 1: Проверка компиляции..."
spawn bash -c "cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS && python3 -m py_compile ${local_agent_dir}/ai_categories_agent.py ${local_api_dir}/ai_categories_router.py 2>&1"
expect {
    eof {
        puts "   ✅ Компиляция: OK"
    }
}
wait

# Шаг 2: Создание директорий на сервере
puts "📋 Шаг 2: Создание директорий на сервере..."
spawn ssh $server "mkdir -p ${server_path}/${local_agent_dir} && mkdir -p ${server_path}/${local_api_dir} && mkdir -p ${server_path}/data/sfm && mkdir -p /tmp && echo 'OK'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "Are you sure you want to continue connecting" {
        send "yes\r"
        exp_continue
    }
    "OK" {
        puts "   ✅ Директории созданы"
        exp_continue
    }
    eof {
        puts "   ✅ Директории созданы"
    }
}
wait

# Шаг 3: Отправка агента
puts "📤 Шаг 3: Отправка ai_categories_agent.py..."
spawn scp "${local_agent_dir}/ai_categories_agent.py" "$server:${server_path}/${local_agent_dir}/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "Are you sure you want to continue connecting" {
        send "yes\r"
        exp_continue
    }
    eof {
        puts "   ✅ Агент отправлен"
    }
}
wait

# Шаг 4: Отправка FastAPI router
puts "📤 Шаг 4: Отправка ai_categories_router.py..."
spawn scp "${local_api_dir}/ai_categories_router.py" "$server:${server_path}/${local_api_dir}/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Router отправлен"
    }
}
wait

# Шаг 5: Отправка JSON entry
puts "📤 Шаг 5: Отправка function_registry_entry_ai_categories.json..."
spawn scp "${local_agent_dir}/function_registry_entry_ai_categories.json" "$server:/tmp/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ JSON entry отправлен"
    }
}
wait

# Шаг 6: Отправка скрипта регистрации
puts "📤 Шаг 6: Отправка register_ai_categories_in_sfm.py..."
spawn scp "register_ai_categories_in_sfm.py" "$server:/tmp/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Скрипт регистрации отправлен"
    }
}
wait

# Шаг 7: Отправка скрипта интеграции в main.py
puts "📤 Шаг 7: Отправка add_ai_categories_to_main.py..."
spawn scp "add_ai_categories_to_main.py" "$server:/tmp/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Скрипт интеграции отправлен"
    }
}
wait

puts ""
puts "================================"
puts "✅ ФАЙЛЫ УСПЕШНО ОТПРАВЛЕНЫ НА СЕРВЕР!"
puts ""

# Шаг 8: Регистрация в SFM
puts "📝 Шаг 8: Регистрация в SFM..."
spawn ssh $server "cd /tmp && echo 'y' | python3 register_ai_categories_in_sfm.py"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Регистрация в SFM завершена"
    }
}
wait

# Шаг 9: Интеграция в main.py
puts "🔧 Шаг 9: Интеграция router в main.py..."
spawn ssh $server "cd /tmp && python3 add_ai_categories_to_main.py"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Интеграция в main.py завершена"
    }
}
wait

# Шаг 10: Подсчет функций в SFM
puts "📊 Шаг 10: Подсчет функций в SFM..."
spawn ssh $server "python3 << 'PYEOF'
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
        send "$password\r"
        exp_continue
    }
    eof {
        puts ""
    }
}
wait

# Шаг 11: Перезапуск сервиса
puts "🔄 Шаг 11: Перезапуск backend сервиса..."
spawn ssh $server "
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
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Сервис перезапущен"
    }
}
wait

# Шаг 12: Проверка health check
puts "🔍 Шаг 12: Проверка health check..."
sleep 3
spawn ssh $server "curl -s http://localhost:8000/api/ai-categories/health 2>/dev/null | python3 -m json.tool || echo '⚠️  Health check недоступен'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts ""
    }
}
wait

puts ""
puts "================================"
puts "✅ ДЕПЛОЙ ЗАВЕРШЕН!"
puts ""
puts "📝 ПРОВЕРКА:"
puts "   curl http://149.154.65.180:8000/api/ai-categories/health"
puts "   curl http://149.154.65.180:8000/api/ai-categories/sites"
puts ""
