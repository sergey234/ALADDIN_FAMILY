#!/usr/bin/expect -f
# Финальная проверка деплоя
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== ФИНАЛЬНАЯ ПРОВЕРКА ДЕПЛОЯ ==="
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

# Статус сервиса
puts "1. Статус сервиса..."
send "systemctl status aladdin-backend --no-pager | head -10\r"
expect "# "

# Проверка что процесс работает
send "ps aux | grep 'uvicorn main:app' | grep -v grep\r"
expect "# "

# Проверка порта
send "netstat -tlnp | grep 8000\r"
expect "# "

# Health check с подробностями
puts "2. Health check..."
send "curl -v http://localhost:8000/api/location/bubble/health 2>&1 | head -20\r"
expect "# "

# Проверка что router зарегистрирован в логах
puts "3. Проверка логов регистрации..."
send "journalctl -u aladdin-backend --since '1 minute ago' --no-pager | grep -i 'location\\|router' | tail -10\r"
expect "# "

# Проверка всех endpoints
puts "4. Проверка всех endpoints..."
send "curl -s http://localhost:8000/docs 2>&1 | grep -o '/api/location/bubble[^\"<]*' | head -5\r"
expect "# "

puts ""
puts "Проверка завершена"
puts ""

send "exit\r"
expect eof
