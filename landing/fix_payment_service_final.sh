#!/usr/bin/expect -f

# Финальное исправление payment_service

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ PAYMENT_SERVICE"
puts "=========================================="
puts ""

# 1. Найти ВСЕ процессы uvicorn
puts "1️⃣ Ищу ВСЕ процессы uvicorn..."
spawn ssh $server "ps aux | grep uvicorn | grep -v grep"
expect "password:" { send "$password\r" }
expect eof

set all_processes [string trim $expect_out(buffer)]
puts "$all_processes"
puts ""

# 2. Остановить ВСЕ процессы uvicorn
puts "2️⃣ Останавливаю ВСЕ процессы uvicorn..."
spawn ssh $server "pkill -9 -f uvicorn 2>&1; sleep 3; echo 'ALL_STOPPED'"
expect "password:" { send "$password\r" }
expect eof

set stop_result [string trim $expect_out(buffer)]
puts "$stop_result"
puts ""

# 3. Проверить что порт свободен
puts "3️⃣ Проверяю что порт 8000 свободен..."
spawn ssh $server "lsof -i :8000 2>&1 || echo 'PORT_FREE'"
expect "password:" { send "$password\r" }
expect eof

set port_check [string trim $expect_out(buffer)]
puts "$port_check"
puts ""

# 4. Запустить ОДИН процесс payment_service
puts "4️⃣ Запускаю ОДИН процесс payment_service..."
spawn ssh $server "cd /opt/aladdin-backend && source venv/bin/activate && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/payment_service.log 2>&1 & sleep 3 && echo 'SERVICE_STARTED'"
expect "password:" { send "$password\r" }
expect eof

set start_result [string trim $expect_out(buffer)]
puts "$start_result"
puts ""

# 5. Проверить что только ОДИН процесс
puts "5️⃣ Проверяю что только ОДИН процесс..."
spawn ssh $server "ps aux | grep 'uvicorn.*main:app' | grep -v grep | wc -l"
expect "password:" { send "$password\r" }
expect eof

set count_result [string trim $expect_out(buffer)]
puts "Количество процессов: $count_result"
puts ""

# 6. Проверить доступность API
puts "6️⃣ Проверяю доступность API..."
spawn ssh $server "sleep 2 && curl -s -o /dev/null -w 'HTTP Status: %{http_code}\n' http://localhost:8000/ 2>&1"
expect "password:" { send "$password\r" }
expect eof

set api_check [string trim $expect_out(buffer)]
puts "$api_check"
puts ""

puts "=========================================="
puts "✅ Payment Service исправлен!"
puts ""

