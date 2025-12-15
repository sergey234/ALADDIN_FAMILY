#!/usr/bin/expect -f
# Скрипт для точного подсчета функций в SFM на сервере

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "================================================================================"
puts "🔍 ТОЧНЫЙ ПОДСЧЕТ ФУНКЦИЙ В SFM НА СЕРВЕРЕ"
puts "================================================================================"
puts ""

puts "📡 Подключение к серверу: $server"
puts ""

spawn ssh $server {python3 << PYEOF
import json
from pathlib import Path

registry_path = Path('/opt/aladdin-backend/data/sfm/function_registry.json')

try:
    with open(registry_path, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    if isinstance(registry, list):
        agents = registry
    elif isinstance(registry, dict):
        if "agents" in registry:
            agents = registry["agents"]
        else:
            agents = [v for v in registry.values() if isinstance(v, dict) and "functions" in v]
    else:
        agents = []
    
    total_agents = len(agents)
    total_functions = 0
    active_agents = 0
    agents_info = []
    
    for agent in agents:
        if isinstance(agent, dict):
            agent_name = agent.get("name", "unknown")
            functions = agent.get("functions", [])
            func_count = len(functions)
            total_functions += func_count
            status = agent.get("status", "unknown")
            
            if status == "active":
                active_agents += 1
            
            agents_info.append({
                "name": agent_name,
                "functions": func_count,
                "status": status
            })
    
    agents_info.sort(key=lambda x: x["functions"], reverse=True)
    
    print("=" * 80)
    print("📊 ТОЧНАЯ СТАТИСТИКА SFM:")
    print("=" * 80)
    print(f"Всего агентов: {total_agents}")
    print(f"Активных агентов: {active_agents}")
    print(f"ВСЕГО ФУНКЦИЙ: {total_functions}")
    print("=" * 80)
    print()
    print("🏆 ТОП-30 АГЕНТОВ ПО КОЛИЧЕСТВУ ФУНКЦИЙ:")
    print()
    for i, info in enumerate(agents_info[:30], 1):
        status_icon = "✅" if info["status"] == "active" else "⚠️"
        print(f"  {i:3d}. {status_icon} {info['name']:50s} - {info['functions']:4d} функций")
    
    if len(agents_info) > 30:
        print(f"  ... и еще {len(agents_info) - 30} агентов")
    
    print()
    print("=" * 80)
    print(f"✅ ИТОГО: {total_functions} ФУНКЦИЙ")
    print("=" * 80)
    
except FileNotFoundError:
    print("❌ Registry не найден")
except Exception as e:
    print(f"❌ Ошибка: {e}")
PYEOF
}

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof {
    }
}

wait

puts ""
