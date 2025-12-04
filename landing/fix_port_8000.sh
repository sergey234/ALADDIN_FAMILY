#!/usr/bin/expect -f

# Исправление проблемы с портом 8000

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ИСПРАВЛЕНИЕ ПРОБЛЕМЫ С ПОРТОМ 8000"
puts "=========================================="
puts ""

# 1. Найти все процессы на порту 8000
puts "1️⃣ Ищу процессы на порту 8000..."
spawn ssh $server "lsof -i :8000 2>&1"
expect "password:" { send "$password\r" }
expect eof

set port_check [string trim $expect_out(buffer)]
puts "$port_check"
puts ""

# 2. Найти все процессы uvicorn
puts "2️⃣ Ищу все процессы uvicorn..."
spawn ssh $server "ps aux | grep 'uvicorn.*main:app' | grep -v grep"
expect "password:" { send "$password\r" }
expect eof

set uvicorn_processes [string trim $expect_out(buffer)]
puts "$uvicorn_processes"
puts ""

# 3. Остановить все процессы uvicorn
puts "3️⃣ Останавливаю все процессы uvicorn..."
spawn ssh $server "pkill -f 'uvicorn main:app' 2>&1; sleep 2; echo 'PROCESSES_STOPPED'"
expect "password:" { send "$password\r" }
expect eof

set stop_result [string trim $expect_out(buffer)]
puts "$stop_result"
puts ""

# 4. Проверить что порт свободен
puts "4️⃣ Проверяю что порт свободен..."
spawn ssh $server "lsof -i :8000 2>&1 || echo 'PORT_FREE'"
expect "password:" { send "$password\r" }
expect eof

set port_free [string trim $expect_out(buffer)]
puts "$port_free"
puts ""

# 5. Запустить один процесс payment_service
puts "5️⃣ Запускаю payment_service..."
spawn ssh $server "cd /opt/aladdin-backend && source venv/bin/activate && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/payment_service.log 2>&1 & sleep 3 && echo 'SERVICE_STARTED'"
expect "password:" { send "$password\r" }
expect eof

set start_result [string trim $expect_out(buffer)]
puts "$start_result"
puts ""

# 6. Проверить что процесс запустился
puts "6️⃣ Проверяю процесс..."
spawn ssh $server "ps aux | grep 'uvicorn.*main:app' | grep -v grep | head -1"
expect "password:" { send "$password\r" }
expect eof

set process_check [string trim $expect_out(buffer)]
puts "$process_check"
puts ""

# 7. Проверить доступность API
puts "7️⃣ Проверяю доступность API..."
spawn ssh $server "sleep 2 && curl -s -o /dev/null -w 'HTTP Status: %{http_code}\n' http://localhost:8000/ 2>&1"
expect "password:" { send "$password\r" }
expect eof

set api_check [string trim $expect_out(buffer)]
puts "$api_check"
puts ""

# 8. Проверить логи на ошибки
puts "8️⃣ Проверяю логи на ошибки..."
spawn ssh $server "tail -10 /tmp/payment_service.log 2>&1 | grep -i error || echo 'NO_ERRORS'"
expect "password:" { send "$password\r" }
expect eof

set errors_check [string trim $expect_out(buffer)]
puts "$errors_check"
puts ""

puts "=========================================="
puts "✅ Проблема исправлена!"
puts ""

