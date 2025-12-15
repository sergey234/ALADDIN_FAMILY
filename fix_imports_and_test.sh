#!/usr/bin/expect -f
# Исправление импортов и тестирование
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== ИСПРАВЛЕНИЕ ИМПОРТОВ ==="
puts ""

# Копирование скрипта
spawn scp fix_import_order_final.py $server:/tmp/
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
send "python3 /tmp/fix_import_order_final.py\r"
expect "# "

# Проверка
send "python3 -m py_compile main.py && echo '✅ OK'\r"
expect "# "

# Показываем порядок
send "grep -n 'location_bubble_router' main.py\r"
expect "# "

# Убиваем старый процесс
send "pkill -f 'uvicorn main:app'\r"
expect "# "
sleep 2

# Запуск сервиса
send "systemctl start aladdin-backend\r"
expect "# "
sleep 5

# Health check
send "curl -s http://localhost:8000/api/location/bubble/health | python3 -m json.tool\r"
expect "# "

# Логи
send "journalctl -u aladdin-backend -n 10 --no-pager | grep -i 'location\\|router\\|error' | tail -5\r"
expect "# "

puts ""
puts "✅ Готово!"
puts ""

send "exit\r"
expect eof
