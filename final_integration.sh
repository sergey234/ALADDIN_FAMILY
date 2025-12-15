#!/usr/bin/expect -f
# Финальная интеграция Location Bubble Router
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== ФИНАЛЬНАЯ ИНТЕГРАЦИЯ LOCATION BUBBLE ROUTER ==="
puts ""

spawn ssh $server
expect {
    "password:" {
        send "$password\r"
        expect "# "
    }
}

send "cd /opt/aladdin-backend\r"
expect "# "

# Восстановление из backup
send "cp main.py.backup_20251213_160926 main.py\r"
expect "# "

# Запуск правильного скрипта
send "cd /tmp\r"
expect "# "
send "python3 add_location_bubble_final.py\r"
expect "# "

# Проверка синтаксиса
send "cd /opt/aladdin-backend\r"
expect "# "
send "python3 -m py_compile main.py && echo '✅ Синтаксис OK'\r"
expect "# "

# Перезапуск
send "systemctl restart aladdin-backend\r"
expect "# "
sleep 3

# Health check
send "curl -s http://localhost:8000/api/location/bubble/health\r"
expect "# "
send "echo ''\r"
expect "# "

puts ""
puts "✅ Интеграция завершена!"
puts ""

send "exit\r"
expect eof
