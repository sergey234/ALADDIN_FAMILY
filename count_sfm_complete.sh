#!/usr/bin/expect -f
# Полный подсчет всех функций в SFM, включая functions и handlers

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "================================================================================"
puts "🔍 ПОЛНЫЙ ПОДСЧЕТ ВСЕХ ФУНКЦИЙ В SFM"
puts "================================================================================"
puts ""

spawn ssh $server {python3 << PYEOF
import json
from pathlib import Path

registry_path = Path("/opt/aladdin-backend/data/sfm/function_registry.json")

with open(registry_path, 'r', encoding='utf-8') as f:
    registry = json.load(f)

print("=" * 80)
print("📊 ПОЛНЫЙ ПОДСЧЕТ ФУНКЦИЙ В SFM")
print("=" * 80)
print()

total_functions = 0
total_handlers = 0
total_agents = 0

# 1. Проверка ключа "functions"
if "functions" in registry:
    functions = registry["functions"]
    if isinstance(functions, dict):
        total_functions += len(functions)
        print(f"📌 Ключ 'functions' (dict): {len(functions)} функций")
    elif isinstance(functions, list):
        total_functions += len(functions)
        print(f"📌 Ключ 'functions' (list): {len(functions)} функций")
    else:
        print(f"📌 Ключ 'functions': {type(functions).__name__}")
        # Если это строка с JSON, попробуем распарсить
        if isinstance(functions, str):
            try:
                parsed = json.loads(functions)
                if isinstance(parsed, dict):
                    total_functions += len(parsed)
                    print(f"   После парсинга: {len(parsed)} функций")
                elif isinstance(parsed, list):
                    total_functions += len(parsed)
                    print(f"   После парсинга: {len(parsed)} функций")
            except:
                pass

# 2. Проверка ключа "handlers"
if "handlers" in registry:
    handlers = registry["handlers"]
    if isinstance(handlers, dict):
        total_handlers += len(handlers)
        print(f"📌 Ключ 'handlers' (dict): {len(handlers)} handlers")
    elif isinstance(handlers, list):
        total_handlers += len(handlers)
        print(f"📌 Ключ 'handlers' (list): {len(handlers)} handlers")
    else:
        print(f"📌 Ключ 'handlers': {type(handlers).__name__}")

# 3. Проверка всех агентов (ключи, которые являются словарями с "functions")
agents_functions = 0
agents_list = []

for key, value in registry.items():
    if key in ["functions", "handlers", "last_updated"]:
        continue
    
    if isinstance(value, dict):
        if "functions" in value:
            funcs = value.get("functions", [])
            func_count = len(funcs)
            agents_functions += func_count
            total_agents += 1
            agents_list.append({
                "name": key,
                "functions": func_count,
                "status": value.get("status", "unknown")
            })

if agents_list:
    print(f"📌 Агенты (отдельные ключи): {total_agents} агентов")
    agents_list.sort(key=lambda x: x["functions"], reverse=True)
    for agent in agents_list:
        print(f"   • {agent['name']:50s} - {agent['functions']:4d} функций")

# 4. Проверка структуры "agents" если есть
if "agents" in registry:
    agents = registry["agents"]
    if isinstance(agents, list):
        print(f"📌 Ключ 'agents' (list): {len(agents)} агентов")
        for agent in agents:
            if isinstance(agent, dict) and "functions" in agent:
                funcs = agent.get("functions", [])
                func_count = len(funcs)
                agents_functions += func_count
                agents_list.append({
                    "name": agent.get("name", "unknown"),
                    "functions": func_count,
                    "status": agent.get("status", "unknown")
                })

print()
print("=" * 80)
print("📊 ИТОГОВАЯ СТАТИСТИКА:")
print("=" * 80)
print(f"Функций в ключе 'functions': {total_functions}")
print(f"Handlers в ключе 'handlers': {total_handlers}")
print(f"Функций в агентах: {agents_functions}")
print(f"Всего агентов: {total_agents}")
print()
print(f"✅ ВСЕГО ФУНКЦИЙ: {total_functions + agents_functions}")
print("=" * 80)

# Детальная информация о ключе "functions" если он большой
if "functions" in registry:
    funcs_data = registry["functions"]
    if isinstance(funcs_data, dict):
        print()
        print("📋 Первые 20 функций из ключа 'functions':")
        for i, (func_name, func_data) in enumerate(list(funcs_data.items())[:20], 1):
            print(f"   {i:3d}. {func_name}")
        if len(funcs_data) > 20:
            print(f"   ... и еще {len(funcs_data) - 20} функций")

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

puts ""
