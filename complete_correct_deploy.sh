#!/usr/bin/expect -f
# Полный правильный деплой - копирование и интеграция
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== ПОЛНЫЙ ПРАВИЛЬНЫЙ ДЕПЛОЙ ==="
puts ""

# Копирование скрипта
puts "1. Копирование скрипта интеграции..."
spawn scp add_location_bubble_correct_final.py $server:/tmp/
expect {
    "password:" {
        send "$password\r"
        expect eof
    }
    eof
}

# Подключение и выполнение
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

# Запуск скрипта
send "cd /tmp\r"
expect "# "
send "python3 add_location_bubble_correct_final.py\r"
expect "# "

# Проверка
send "cd /opt/aladdin-backend\r"
expect "# "
send "python3 -m py_compile main.py && echo '✅ Синтаксис OK'\r"
expect "# "

# Показываем что добавлено
send "grep -n 'location_bubble_router' main.py\r"
expect "# "

# Перезапуск
send "systemctl restart aladdin-backend\r"
expect "# "
sleep 4

# Health check
send "curl -s http://localhost:8000/api/location/bubble/health | python3 -m json.tool\r"
expect "# "

puts ""
puts "✅ Деплой завершен!"
puts ""

send "exit\r"
expect eof
