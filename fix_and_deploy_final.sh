#!/usr/bin/expect -f
# Финальное исправление и деплой
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ ==="
puts ""

# Копирование скрипта
spawn scp fix_import_position.py $server:/tmp/
expect {
    "password:" {
        send "$password\r"
        expect eof
    }
    eof
}

# Подключение
spawn ssh $server
expect {
    "password:" {
        send "$password\r"
        expect "# "
    }
}

send "cd /opt/aladdin-backend\r"
expect "# "

# Исправление
send "python3 /tmp/fix_import_position.py\r"
expect "# "

# Проверка
send "python3 -m py_compile main.py && echo '✅ OK'\r"
expect "# "

# Показываем порядок
send "grep -n 'location_bubble_router\\|crash_detection_router' main.py | grep import | tail -2\r"
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

# Логи
send "journalctl -u aladdin-backend -n 15 | grep -i 'location\\|router' | tail -5\r"
expect "# "

puts ""
puts "✅ Готово!"
puts ""

send "exit\r"
expect eof
