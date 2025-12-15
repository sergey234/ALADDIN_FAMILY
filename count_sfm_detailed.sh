#!/usr/bin/expect -f
# Детальная проверка структуры SFM registry

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "================================================================================"
puts "🔍 ДЕТАЛЬНАЯ ПРОВЕРКА СТРУКТУРЫ SFM REGISTRY"
puts "================================================================================"
puts ""

spawn ssh $server {python3 << PYEOF
import json
from pathlib import Path
import sys

registry_path = Path("/opt/aladdin-backend/data/sfm/function_registry.json")

if not registry_path.exists():
    print("❌ Registry не найден:", registry_path)
    sys.exit(1)

# Проверка размера файла
file_size = registry_path.stat().st_size
with open(registry_path, 'r', encoding='utf-8') as f:
    lines = len(f.readlines())
    f.seek(0)
    content = f.read()

print(f"📊 Информация о файле:")
print(f"   Размер: {file_size:,} байт")
print(f"   Строк: {lines:,}")
print()

# Попытка загрузить как JSON
try:
    registry = json.loads(content)
except Exception as e:
    print(f"❌ Ошибка парсинга JSON: {e}")
    sys.exit(1)

print(f"📋 Тип данных: {type(registry).__name__}")
print()

# Если это словарь, проверим все ключи
if isinstance(registry, dict):
    print(f"🔑 Ключи в словаре ({len(registry.keys())}):")
    for i, key in enumerate(list(registry.keys())[:20], 1):
        value = registry[key]
        if isinstance(value, dict):
            func_count = len(value.get("functions", []))
            print(f"   {i:3d}. {key:50s} - {func_count:4d} функций")
        elif isinstance(value, list):
            print(f"   {i:3d}. {key:50s} - список из {len(value)} элементов")
        else:
            print(f"   {i:3d}. {key:50s} - {type(value).__name__}")
    
    if len(registry.keys()) > 20:
        print(f"   ... и еще {len(registry.keys()) - 20} ключей")
    
    print()
    
    # Проверка структуры "agents"
    if "agents" in registry:
        agents = registry["agents"]
        print(f"📦 Найден ключ 'agents' с {len(agents)} элементами")
        
        total_funcs = 0
        for agent in agents:
            if isinstance(agent, dict):
                funcs = agent.get("functions", [])
                total_funcs += len(funcs)
        
        print(f"   Всего функций в agents: {total_funcs}")
        print()
    
    # Подсчет всех функций во всех ключах
    total_all_functions = 0
    agents_count = 0
    
    for key, value in registry.items():
        if isinstance(value, dict):
            if "functions" in value:
                funcs = value.get("functions", [])
                total_all_functions += len(funcs)
                agents_count += 1
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict) and "functions" in item:
                    funcs = item.get("functions", [])
                    total_all_functions += len(funcs)
                    agents_count += 1
    
    print(f"📊 ИТОГО:")
    print(f"   Агентов найдено: {agents_count}")
    print(f"   ВСЕГО ФУНКЦИЙ: {total_all_functions}")
    print()

elif isinstance(registry, list):
    print(f"📦 Registry - это список из {len(registry)} элементов")
    
    total_funcs = 0
    for i, item in enumerate(registry):
        if isinstance(item, dict) and "functions" in item:
            funcs = item.get("functions", [])
            total_funcs += len(funcs)
    
    print(f"   ВСЕГО ФУНКЦИЙ: {total_funcs}")
    print()

print("=" * 80)
PYEOF
}

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait
