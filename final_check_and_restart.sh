#!/usr/bin/expect -f
# Финальная проверка и перезапуск
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== ФИНАЛЬНАЯ ПРОВЕРКА И ПЕРЕЗАПУСК ==="
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

# Остановка сервиса
puts "1. Остановка сервиса..."
send "systemctl stop aladdin-backend\r"
expect "# "
sleep 2

# Проверка что процесс остановлен
send "ps aux | grep uvicorn | grep -v grep\r"
expect "# "

# Запуск сервиса
puts "2. Запуск сервиса..."
send "systemctl start aladdin-backend\r"
expect "# "
sleep 5

# Проверка статуса
send "systemctl status aladdin-backend --no-pager | head -15\r"
expect "# "

# Проверка логов запуска
puts "3. Логи запуска..."
send "journalctl -u aladdin-backend -n 30 --no-pager | grep -E 'Location Bubble|Router|started|error|Error' | tail -10\r"
expect "# "

# Health check
puts "4. Health check..."
send "sleep 2 && curl -s http://localhost:8000/api/location/bubble/health | python3 -m json.tool\r"
expect "# "

# Проверка других endpoints для сравнения
puts "5. Проверка других endpoints..."
send "curl -s http://localhost:8000/api/ai-categories/health | python3 -m json.tool | head -5\r"
expect "# "

puts ""
puts "✅ Проверка завершена"
puts ""

send "exit\r"
expect eof
