#!/usr/bin/expect -f
# Добавление Identity Theft Protection в SFM на сервере

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "================================================================================"
puts "🚀 ДОБАВЛЕНИЕ IDENTITY THEFT PROTECTION В SFM"
puts "================================================================================"
puts ""

# Определяем рабочий каталог
set script_dir [file dirname [file normalize $argv0]]
cd $script_dir

# Шаг 1: Копирование файлов на сервер
puts "📤 Шаг 1: Копирование файлов на сервер..."
spawn scp "$script_dir/security/ai_agents/russian_identity_theft_protection_agent.py" "$server:/opt/aladdin-backend/security/ai_agents/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Агент скопирован"
    }
}

wait

spawn scp "$script_dir/security/api/routers/identity_theft_protection_router.py" "$server:/opt/aladdin-backend/security/api/routers/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Router скопирован"
    }
}

wait

spawn scp "$script_dir/security/ai_agents/function_registry_entry_identity_theft_protection.json" "$server:/tmp/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Registry entry скопирован"
    }
}

wait

puts ""

# Шаг 2: Регистрация в SFM
puts "📝 Шаг 2: Регистрация в SFM..."
spawn ssh $server {python3 << PYEOF
import json
from pathlib import Path
from datetime import datetime

registry_path = Path("/opt/aladdin-backend/data/sfm/function_registry.json")
entry_path = Path("/tmp/function_registry_entry_identity_theft_protection.json")

# Backup
backup_path = registry_path.with_suffix(f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
if registry_path.exists():
    import shutil
    shutil.copy2(registry_path, backup_path)
    print(f"✅ Backup создан: {backup_path.name}")

# Загрузка registry
with open(registry_path, 'r', encoding='utf-8') as f:
    registry = json.load(f)

# Загрузка новой entry
with open(entry_path, 'r', encoding='utf-8') as f:
    new_entry = json.load(f)

agent_name = new_entry.get("name")

# Проверка, не зарегистрирован ли уже
existing = registry.get(agent_name)
if existing:
    print(f"⚠️  Агент '{agent_name}' уже зарегистрирован, обновляем...")
    registry[agent_name] = new_entry
else:
    print(f"✅ Добавляем новый агент '{agent_name}'...")
    registry[agent_name] = new_entry

# Обновление метаданных
registry["last_updated"] = datetime.now().isoformat()

# Сохранение
with open(registry_path, 'w', encoding='utf-8') as f:
    json.dump(registry, f, indent=2, ensure_ascii=False)

print(f"✅ Агент '{agent_name}' зарегистрирован в SFM!")
print()

# Подсчет после добавления
functions_in_key = len(registry.get("functions", {}))
handlers_count = len(registry.get("handlers", {}))
agents_count = sum(1 for k, v in registry.items() if isinstance(v, dict) and "functions" in v and k not in ["functions", "handlers"])
agents_functions = sum(len(v.get("functions", [])) for k, v in registry.items() if isinstance(v, dict) and "functions" in v and k not in ["functions", "handlers"])

print("=" * 80)
print("📊 СТАТИСТИКА ПОСЛЕ ДОБАВЛЕНИЯ:")
print("=" * 80)
print(f"Функций в ключе 'functions': {functions_in_key}")
print(f"Handlers: {handlers_count}")
print(f"Агентов (отдельные ключи): {agents_count}")
print(f"Функций в агентах: {agents_functions}")
print()
print(f"✅ ВСЕГО ФУНКЦИЙ: {functions_in_key + agents_functions}")
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

puts ""
puts "✅ Identity Theft Protection добавлен в SFM!"
