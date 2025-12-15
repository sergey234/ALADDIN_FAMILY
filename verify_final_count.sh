#!/usr/bin/expect -f
# Финальная проверка количества функций после добавления Identity Theft Protection

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "================================================================================"
puts "🔍 ФИНАЛЬНАЯ ПРОВЕРКА ПОСЛЕ ДОБАВЛЕНИЯ IDENTITY THEFT PROTECTION"
puts "================================================================================"
puts ""

spawn ssh $server {python3 << PYEOF
import json
from pathlib import Path

registry_path = Path("/opt/aladdin-backend/data/sfm/function_registry.json")

with open(registry_path, 'r', encoding='utf-8') as f:
    registry = json.load(f)

print("=" * 80)
print("📊 ФИНАЛЬНАЯ СТАТИСТИКА SFM:")
print("=" * 80)
print()

# Функции в ключе 'functions'
functions_in_key = len(registry.get("functions", {}))
print(f"📌 Функций в ключе 'functions': {functions_in_key}")

# Handlers
handlers_count = len(registry.get("handlers", {}))
print(f"📌 Handlers: {handlers_count}")

# Агенты (отдельные ключи)
agents_list = []
for key, value in registry.items():
    if key in ["functions", "handlers", "last_updated"]:
        continue
    if isinstance(value, dict) and "functions" in value:
        agents_list.append({
            "name": key,
            "functions": len(value.get("functions", [])),
            "status": value.get("status", "unknown")
        })

agents_functions = sum(a["functions"] for a in agents_list)

print(f"📌 Агентов (отдельные ключи): {len(agents_list)}")
print()
print("   Детализация агентов:")
for agent in sorted(agents_list, key=lambda x: x["functions"], reverse=True):
    status_icon = "✅" if agent["status"] == "active" else "⚠️"
    print(f"   • {status_icon} {agent['name']:50s} - {agent['functions']:4d} функций")

print()
print("=" * 80)
print(f"✅ ВСЕГО ФУНКЦИЙ: {functions_in_key + agents_functions}")
print("=" * 80)
print()

# Проверка наличия Identity Theft Protection
if "russian_identity_theft_protection_agent" in registry:
    itp = registry["russian_identity_theft_protection_agent"]
    print("✅ Identity Theft Protection найден в registry!")
    print(f"   Статус: {itp.get('status', 'unknown')}")
    print(f"   Функций: {len(itp.get('functions', []))}")
else:
    print("❌ Identity Theft Protection НЕ найден в registry!")

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
