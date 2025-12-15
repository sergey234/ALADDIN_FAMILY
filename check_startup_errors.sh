#!/usr/bin/expect -f
# Проверка ошибок запуска
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== ПРОВЕРКА ОШИБОК ЗАПУСКА ==="
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

# Проверка логов ошибок
puts "1. Логи ошибок..."
send "journalctl -u aladdin-backend -n 50 --no-pager | tail -30\r"
expect "# "

# Попытка запуска вручную для просмотра ошибок
puts "2. Запуск вручную для просмотра ошибок..."
send "cd /opt/aladdin-backend && source venv/bin/activate && timeout 5 python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 2>&1 | head -30 || true\r"
expect "# "

puts ""
puts "Проверка завершена"
puts ""

send "exit\r"
expect eof
