#!/usr/bin/expect -f
# Проверка регистрации в SFM

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА РЕГИСТРАЦИИ В SFM"
puts "=============================="
puts ""

# Шаг 1: Проверить структуру registry
puts "📋 Шаг 1: Структура function_registry.json..."
spawn ssh $server "python3 << 'PYEOF'
import json
from pathlib import Path

registry_path = Path('/opt/aladdin-backend/data/sfm/function_registry.json')

if not registry_path.exists():
    print('❌ Registry не найден!')
    exit(1)

with open(registry_path, 'r', encoding='utf-8') as f:
    registry = json.load(f)

print(f'📊 Тип registry: {type(registry).__name__}')

if isinstance(registry, dict):
    if 'agents' in registry:
        agents = registry['agents']
        print(f'📊 Всего агентов: {len(agents)}')
        print('')
        for i, agent in enumerate(agents, 1):
            print(f'{i}. {agent.get(\"name\", \"unknown\")} - {agent.get(\"status\", \"unknown\")}')
    else:
        print(f'📊 Ключей в словаре: {len(registry)}')
        for key in list(registry.keys())[:10]:
            print(f'  - {key}')
elif isinstance(registry, list):
    print(f'📊 Всего записей: {len(registry)}')
    print('')
    for i, item in enumerate(registry, 1):
        name = item.get('name', 'unknown') if isinstance(item, dict) else str(item)[:50]
        status = item.get('status', 'unknown') if isinstance(item, dict) else 'N/A'
        print(f'{i}. {name} - {status}')
PYEOF
"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

# Шаг 2: Проверить наш агент
puts ""
puts "📋 Шаг 2: Проверка dark_web_monitoring_agent..."
spawn ssh $server "python3 << 'PYEOF'
import json
from pathlib import Path

registry_path = Path('/opt/aladdin-backend/data/sfm/function_registry.json')

with open(registry_path, 'r', encoding='utf-8') as f:
    registry = json.load(f)

# Найти наш агент
if isinstance(registry, list):
    agent = next((a for a in registry if a.get('name') == 'dark_web_monitoring_agent'), None)
elif isinstance(registry, dict):
    if 'agents' in registry:
        agent = next((a for a in registry['agents'] if a.get('name') == 'dark_web_monitoring_agent'), None)
    else:
        agent = registry.get('dark_web_monitoring_agent')

if agent:
    print('✅ Агент найден!')
    print(f'   Имя: {agent.get(\"name\")}')
    print(f'   Статус: {agent.get(\"status\")}')
    print(f'   Путь: {agent.get(\"path\")}')
    print(f'   Класс: {agent.get(\"class\")}')
    print(f'   Функций: {len(agent.get(\"functions\", []))}')
else:
    print('❌ Агент НЕ найден!')
PYEOF
"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

# Шаг 3: Сравнить с другими агентами
puts ""
puts "📋 Шаг 3: Сравнение со структурой других агентов..."
spawn ssh $server "python3 << 'PYEOF'
import json
from pathlib import Path

registry_path = Path('/opt/aladdin-backend/data/sfm/function_registry.json')

with open(registry_path, 'r', encoding='utf-8') as f:
    registry = json.load(f)

if isinstance(registry, list):
    agents = registry
elif isinstance(registry, dict):
    agents = registry.get('agents', list(registry.values()))

if agents:
    # Взять первый агент для сравнения
    sample_agent = agents[0] if isinstance(agents[0], dict) else None
    if sample_agent:
        print('📋 Структура первого агента:')
        print(f'   Ключи: {list(sample_agent.keys())[:10]}')
        if 'functions' in sample_agent:
            print(f'   Пример функции: {sample_agent[\"functions\"][0] if sample_agent[\"functions\"] else \"нет\"}')
PYEOF
"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait
