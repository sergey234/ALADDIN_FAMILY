#!/usr/bin/expect -f
# Исправление и повторная интеграция Location Bubble Agent
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== ИСПРАВЛЕНИЕ И ПОВТОРНАЯ ИНТЕГРАЦИЯ ==="
puts ""

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

# Восстановление из backup
puts "1. Восстановление main.py из backup..."
send "cd /opt/aladdin-backend\r"
expect "# "
send "cp main.py.backup_20251213_160926 main.py\r"
expect "# "

# Повторная интеграция
puts "2. Повторная интеграция с исправленным скриптом..."
send "cd /tmp\r"
expect "# "
send "python3 add_location_bubble_to_main.py\r"
expect {
    "Перезаписать? (y/n):" {
        send "y\r"
        expect "# "
    }
    "# " {}
    timeout {}
}

# Проверка синтаксиса
puts "3. Проверка синтаксиса..."
send "cd /opt/aladdin-backend\r"
expect "# "
send "python3 -m py_compile main.py\r"
expect "# "

# Перезапуск
puts "4. Перезапуск сервиса..."
send "systemctl restart aladdin-backend\r"
expect "# "
sleep 3

# Health check
puts "5. Проверка health endpoint..."
send "curl -s http://localhost:8000/api/location/bubble/health | python3 -m json.tool\r"
expect "# "

puts ""
puts "✅ Готово!"
puts ""

send "exit\r"
expect eof
