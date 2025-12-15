#!/usr/bin/expect -f
# Автоматическая регистрация и интеграция Location Bubble Agent
# Использование: ./register_and_integrate_location_bubble.sh

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== РЕГИСТРАЦИЯ И ИНТЕГРАЦИЯ LOCATION BUBBLE AGENT ==="
puts ""

# Подключение к серверу
spawn ssh $server
expect {
    "password:" {
        send "$password\r"
        expect "# "
    }
    "yes/no" {
        send "yes\r"
        expect "password:"
        send "$password\r"
        expect "# "
    }
}

# Шаг 1: Регистрация в SFM
puts "1. Регистрация в SFM..."
send "cd /tmp\r"
expect "# "
send "python3 register_location_bubble_in_sfm.py\r"
expect {
    "Перезаписать? (y/n):" {
        send "y\r"
        expect "# "
    }
    "# " {
        # Успешно зарегистрировано
    }
    timeout {
        puts "⚠️  Таймаут при регистрации в SFM"
    }
}

# Шаг 2: Интеграция в main.py
puts "2. Интеграция в main.py..."
send "python3 add_location_bubble_to_main.py\r"
expect {
    "Перезаписать? (y/n):" {
        send "y\r"
        expect "# "
    }
    "# " {
        # Успешно интегрировано
    }
    timeout {
        puts "⚠️  Таймаут при интеграции в main.py"
    }
}

# Шаг 3: Перезапуск сервиса
puts "3. Перезапуск сервиса..."
send "systemctl restart aladdin-backend\r"
expect "# "
sleep 2

# Шаг 4: Проверка статуса
puts "4. Проверка статуса сервиса..."
send "systemctl status aladdin-backend --no-pager | head -10\r"
expect "# "

# Шаг 5: Health check
puts "5. Проверка health endpoint..."
send "curl -s http://localhost:8000/api/location/bubble/health\r"
expect "# "

puts ""
puts "✅ Деплой завершен!"
puts ""

send "exit\r"
expect eof
