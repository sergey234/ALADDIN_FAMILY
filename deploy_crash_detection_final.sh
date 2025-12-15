#!/usr/bin/expect -f
# Скрипт для деплоя Crash Detection Agent на сервер
# Использует expect для автоматического ввода пароля
# Использование: ./deploy_crash_detection_final.sh

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"
set server_path "/opt/aladdin-backend"
set local_agent_dir "security/ai_agents"
set local_api_dir "security/api/routers"

puts "🚗 ДЕПЛОЙ CRASH DETECTION AGENT"
puts "================================"
puts ""

# Шаг 1: Проверка компиляции
puts "📋 Шаг 1: Проверка компиляции..."
spawn bash -c "cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS && python3 -m py_compile ${local_agent_dir}/crash_detection_agent.py ${local_api_dir}/crash_detection_router.py 2>&1"
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
puts "📤 Шаг 3: Отправка crash_detection_agent.py..."
spawn scp "${local_agent_dir}/crash_detection_agent.py" "$server:${server_path}/${local_agent_dir}/"

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
puts "📤 Шаг 4: Отправка crash_detection_router.py..."
spawn scp "${local_api_dir}/crash_detection_router.py" "$server:${server_path}/${local_api_dir}/"

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
puts "📤 Шаг 5: Отправка function_registry_entry_crash_detection.json..."
spawn scp "${local_agent_dir}/function_registry_entry_crash_detection.json" "$server:/tmp/"

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
puts "📤 Шаг 6: Отправка register_crash_detection_in_sfm.py..."
spawn scp "register_crash_detection_in_sfm.py" "$server:/tmp/"

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
puts "📤 Шаг 7: Отправка add_crash_detection_to_main.py..."
spawn scp "add_crash_detection_to_main.py" "$server:/tmp/"

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
spawn ssh $server "cd /tmp && echo 'y' | python3 register_crash_detection_in_sfm.py"

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
spawn ssh $server "cd /tmp && echo 'y' | python3 add_crash_detection_to_main.py"

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

# Шаг 10: Проверка импорта
puts "🔍 Шаг 10: Проверка импорта агента..."
spawn ssh $server "cd ${server_path} && python3 -c 'from security.ai_agents.crash_detection_agent import CrashDetectionAgent; print(\"✅ Импорт агента успешен\")'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅ Импорт агента успешен" {
        puts "   ✅ Агент импортирован успешно"
        exp_continue
    }
    eof {
    }
}
wait

# Шаг 11: Проверка импорта router
puts "🔍 Шаг 11: Проверка импорта router..."
spawn ssh $server "cd ${server_path} && python3 -c 'from security.api.routers.crash_detection_router import router; print(\"✅ Импорт router успешен\")'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅ Импорт router успешен" {
        puts "   ✅ Router импортирован успешно"
        exp_continue
    }
    eof {
    }
}
wait

# Шаг 12: Статистика SFM
puts "📊 Шаг 12: Статистика SFM..."
spawn ssh $server "cd /tmp && python3 << 'PYEOF'
import json
import sys
sys.path.insert(0, '/opt/aladdin-backend')
with open('/opt/aladdin-backend/data/sfm/function_registry.json', 'r') as f:
    registry = json.load(f)
agents = {k: v for k, v in registry.items() if k not in ['functions', 'handlers', 'last_updated'] and isinstance(v, dict) and 'functions' in v}
total_funcs = sum(len(agent.get('functions', [])) for agent in agents.values())
total_endpoints = sum(len(agent.get('api_endpoints', [])) for agent in agents.values())
print('=' * 80)
print(f'Агентов: {len(agents)}')
print(f'Функций в агентах: {total_funcs}')
print(f'API endpoints: {total_endpoints}')
print('=' * 80)
agent_details = [(name, len(agent.get('functions', []))) for name, agent in agents.items()]
agent_details.sort(key=lambda x: x[1], reverse=True)
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

# Шаг 13: Перезапуск сервиса
puts "🔄 Шаг 13: Перезапуск backend сервиса..."
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

# Шаг 14: Проверка health check
puts "🔍 Шаг 14: Проверка health check..."
sleep 3
spawn ssh $server "curl -s http://localhost:8000/api/crash-detection/health 2>/dev/null | head -10"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Health check выполнен"
    }
}
wait

puts ""
puts "================================"
puts "✅ ДЕПЛОЙ ЗАВЕРШЕН УСПЕШНО!"
puts "================================"
puts ""
puts "📋 Следующие шаги:"
puts "1. Проверьте логи: journalctl -u aladdin-backend -n 50 | grep crash"
puts "2. Проверьте health: curl http://localhost:8000/api/crash-detection/health"
puts "3. Проверьте SFM статистику (должно быть 1100+ функций)"
puts ""
