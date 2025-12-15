#!/usr/bin/expect -f
# Финальный правильный деплой по инструкции
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== ФИНАЛЬНЫЙ ДЕПЛОЙ ПО ИНСТРУКЦИИ ==="
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
send "python3 add_location_bubble_correct_final.py\r"
expect "# "

# Проверка синтаксиса
send "cd /opt/aladdin-backend\r"
expect "# "
send "python3 -m py_compile main.py && echo '✅ Синтаксис OK'\r"
expect "# "

# Проверка что все добавлено правильно
send "grep -A 2 'Location Bubble Router' main.py | head -5\r"
expect "# "

# Перезапуск
send "systemctl restart aladdin-backend\r"
expect "# "
sleep 4

# Health check
send "curl -s http://localhost:8000/api/location/bubble/health\r"
expect "# "
send "echo ''\r"
expect "# "

# Проверка логов
send "journalctl -u aladdin-backend -n 20 | grep -i 'location_bubble' | tail -3\r"
expect "# "

puts ""
puts "✅ Деплой завершен!"
puts ""

send "exit\r"
expect eof
