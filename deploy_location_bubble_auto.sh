#!/usr/bin/expect -f
# Автоматический деплой Location Bubble Agent с использованием expect
# Использование: ./deploy_location_bubble_auto.sh

set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== ДЕПЛОЙ LOCATION BUBBLE AGENT ==="
puts ""

# Шаг 1: Копирование агента
puts "1. Копирование location_bubble_agent.py..."
spawn scp security/ai_agents/location_bubble_agent.py $server:/opt/aladdin-backend/security/ai_agents/
expect {
    "password:" {
        send "$password\r"
        expect eof
    }
    "Permission denied" {
        puts "❌ Ошибка авторизации"
        exit 1
    }
    eof
}

# Шаг 2: Копирование router
puts "2. Копирование location_bubble_router.py..."
spawn scp security/api/routers/location_bubble_router.py $server:/opt/aladdin-backend/security/api/routers/
expect {
    "password:" {
        send "$password\r"
        expect eof
    }
    eof
}

# Шаг 3: Копирование registry entry
puts "3. Копирование function_registry_entry_location_bubble.json..."
spawn scp security/ai_agents/function_registry_entry_location_bubble.json $server:/tmp/
expect {
    "password:" {
        send "$password\r"
        expect eof
    }
    eof
}

# Шаг 4: Копирование скриптов
puts "4. Копирование скриптов регистрации..."
spawn scp register_location_bubble_in_sfm.py add_location_bubble_to_main.py $server:/tmp/
expect {
    "password:" {
        send "$password\r"
        expect eof
    }
    eof
}

puts ""
puts "✅ Все файлы скопированы на сервер!"
puts ""
puts "Следующие шаги (выполните на сервере):"
puts "1. ssh root@149.154.65.180"
puts "2. cd /tmp"
puts "3. python3 register_location_bubble_in_sfm.py"
puts "4. python3 add_location_bubble_to_main.py"
puts "5. systemctl restart aladdin-backend"
puts "6. curl http://localhost:8000/api/location/bubble/health"
