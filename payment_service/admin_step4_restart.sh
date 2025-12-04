#!/usr/bin/expect -f

# ШАГ 4: Перезапустить payment_service

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔄 ШАГ 4: Перезапускаю payment_service..."
puts ""

# Остановить старый процесс
puts "Останавливаю старый процесс..."
spawn ssh $server "lsof -ti :8000 | xargs kill 2>&1; sleep 2; lsof -i :8000 2>&1 | grep -v COMMAND || echo 'PORT_FREE'"
expect "password:" { send "$password\r" }
expect eof

set stop_result [string trim $expect_out(buffer)]
puts "Результат: $stop_result"
puts ""

# Запустить новый процесс
puts "Запускаю новый процесс..."
spawn ssh $server "cd /opt/aladdin-backend && nohup /opt/aladdin-backend/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &"
expect "password:" { send "$password\r" }
expect eof

puts "✅ Процесс запущен"
puts ""

# Ждем 3 секунды
puts "Жду 3 секунды..."
spawn ssh $server "sleep 3"
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ Перезапуск завершен!"
puts ""

