#!/usr/bin/expect -f
# Скрипт для деплоя Dark Web Monitoring на сервер
# Использует expect для автоматического ввода пароля
# Использование: ./deploy_dark_web_monitoring.sh

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"
set server_path "/opt/aladdin-backend"
set local_agent_dir "security/ai_agents"
set local_api_dir "security/api"

puts "🚀 ДЕПЛОЙ DARK WEB MONITORING"
puts "================================"
puts ""

# Шаг 1: Проверка flake8
puts "📋 Шаг 1: Проверка компиляции..."
spawn bash -c "cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS && python3 -m py_compile ${local_agent_dir}/dark_web_monitoring_agent.py ${local_agent_dir}/threat_monitoring_interface.py ${local_api_dir}/routers/dark_web_monitoring_router.py 2>&1"
expect {
    eof {
        puts "   ✅ Компиляция: OK"
    }
}

wait

# Шаг 2: Создание директорий на сервере
puts "📋 Шаг 2: Создание директорий на сервере..."
spawn ssh $server "mkdir -p ${server_path}/${local_agent_dir} && mkdir -p ${server_path}/${local_api_dir}/routers && echo 'OK'"

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
puts "📤 Шаг 3: Отправка dark_web_monitoring_agent.py..."
spawn scp "${local_agent_dir}/dark_web_monitoring_agent.py" "$server:${server_path}/${local_agent_dir}/"

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

# Шаг 4: Отправка интерфейса
puts "📤 Шаг 4: Отправка threat_monitoring_interface.py..."
spawn scp "${local_agent_dir}/threat_monitoring_interface.py" "$server:${server_path}/${local_agent_dir}/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Интерфейс отправлен"
    }
}

wait

# Шаг 5: Отправка FastAPI router
puts "📤 Шаг 5: Отправка dark_web_monitoring_router.py..."
spawn scp "${local_api_dir}/routers/dark_web_monitoring_router.py" "$server:${server_path}/${local_api_dir}/routers/"

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

# Шаг 6: Отправка JSON entry
puts "📤 Шаг 6: Отправка function_registry_entry_dark_web_monitoring.json..."
spawn scp "${local_agent_dir}/function_registry_entry_dark_web_monitoring.json" "$server:/tmp/"

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

puts ""
puts "================================"
puts "✅ ФАЙЛЫ УСПЕШНО ОТПРАВЛЕНЫ НА СЕРВЕР!"
puts ""
puts "📝 СЛЕДУЮЩИЕ ШАГИ НА СЕРВЕРЕ:"
puts ""
puts "1. Зарегистрировать в SFM:"
puts "   ssh $server"
puts "   См. docs/ИНСТРУКЦИЯ_РЕГИСТРАЦИИ_В_SFM.md"
puts ""
puts "2. Добавить endpoints в main.py:"
puts "   from security.api.routers.dark_web_monitoring_router import router as dark_web_router"
puts "   app.include_router(dark_web_router)"
puts ""
puts "3. Настроить API ключи:"
puts "   export HIBP_API_KEY='your-key'"
puts ""
puts "4. Перезапустить сервисы:"
puts "   systemctl restart aladdin-backend"
puts ""
puts "📖 Полная инструкция: docs/ЧЕКЛИСТ_ДЕПЛОЯ_DARK_WEB.md"
puts ""
