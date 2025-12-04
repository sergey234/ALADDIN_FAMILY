#!/usr/bin/expect -f

# Проверка и исправление payment_service

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА И ИСПРАВЛЕНИЕ PAYMENT_SERVICE"
puts "=========================================="
puts ""

# 1. Проверить процессы на порту 8000
puts "1️⃣ Проверяю что на порту 8000..."
spawn ssh $server "lsof -i :8000 2>&1 || echo 'PORT_FREE'"
expect "password:" { send "$password\r" }
expect eof

set port_check [string trim $expect_out(buffer)]
puts "$port_check"
puts ""

# 2. Проверить есть ли payment_service процесс
puts "2️⃣ Проверяю процессы payment_service..."
spawn ssh $server "ps aux | grep -E 'uvicorn|payment_service|main:app' | grep -v grep"
expect "password:" { send "$password\r" }
expect eof

set processes [string trim $expect_out(buffer)]
puts "$processes"
puts ""

# 3. Проверить директорию payment_service
puts "3️⃣ Проверяю директорию payment_service..."
spawn ssh $server "ls -la /opt/aladdin-backend/ | head -10"
expect "password:" { send "$password\r" }
expect eof

set dir_check [string trim $expect_out(buffer)]
puts "$dir_check"
puts ""

# 4. Проверить есть ли main.py
puts "4️⃣ Проверяю main.py..."
spawn ssh $server "ls -lh /opt/aladdin-backend/main.py 2>&1"
expect "password:" { send "$password\r" }
expect eof

set main_check [string trim $expect_out(buffer)]
puts "$main_check"
puts ""

# 5. Проверить есть ли venv
puts "5️⃣ Проверяю venv..."
spawn ssh $server "ls -d /opt/aladdin-backend/venv 2>&1 || echo 'VENV_NOT_FOUND'"
expect "password:" { send "$password\r" }
expect eof

set venv_check [string trim $expect_out(buffer)]
puts "$venv_check"
puts ""

# 6. Попробовать запустить payment_service
puts "6️⃣ Запускаю payment_service..."
spawn ssh $server "cd /opt/aladdin-backend && source venv/bin/activate && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/payment_service.log 2>&1 & echo 'PID:' \$!"
expect "password:" { send "$password\r" }
expect eof

set start_result [string trim $expect_out(buffer)]
puts "$start_result"
puts ""

# 7. Подождать и проверить
puts "7️⃣ Жду 3 секунды и проверяю..."
spawn ssh $server "sleep 3 && ps aux | grep 'uvicorn.*main:app' | grep -v grep | head -1"
expect "password:" { send "$password\r" }
expect eof

set after_start [string trim $expect_out(buffer)]
puts "$after_start"
puts ""

# 8. Проверить доступность API
puts "8️⃣ Проверяю доступность API..."
spawn ssh $server "curl -s -o /dev/null -w 'HTTP Status: %{http_code}\n' http://localhost:8000/ 2>&1"
expect "password:" { send "$password\r" }
expect eof

set api_check [string trim $expect_out(buffer)]
puts "$api_check"
puts ""

# 9. Проверить логи запуска
puts "9️⃣ Проверяю логи запуска..."
spawn ssh $server "tail -20 /tmp/payment_service.log 2>&1 || echo 'NO_LOG_FILE'"
expect "password:" { send "$password\r" }
expect eof

set log_check [string trim $expect_out(buffer)]
puts "$log_check"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

