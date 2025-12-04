#!/usr/bin/expect -f

# Исправление и запуск payment_service

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ИСПРАВЛЕНИЕ И ЗАПУСК PAYMENT_SERVICE"
puts "=========================================="
puts ""

# 1. Загрузить исправленный admin_endpoints.py
puts "1️⃣ Загружаю исправленный admin_endpoints.py..."
spawn scp ../payment_service/app/admin_endpoints.py $server:/opt/aladdin-backend/app/admin_endpoints.py
expect "password:" { send "$password\r" }
expect eof

puts "✅ admin_endpoints.py загружен"
puts ""

# 2. Остановить старые процессы на порту 8000
puts "2️⃣ Останавливаю старые процессы..."
spawn ssh $server "lsof -ti :8000 | xargs kill -9 2>&1; sleep 2; echo 'PROCESSES_STOPPED'"
expect "password:" { send "$password\r" }
expect eof

set stop_result [string trim $expect_out(buffer)]
puts "$stop_result"
puts ""

# 3. Запустить payment_service
puts "3️⃣ Запускаю payment_service..."
spawn ssh $server "cd /opt/aladdin-backend && source venv/bin/activate && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/payment_service.log 2>&1 & sleep 3 && echo 'SERVICE_STARTED'"
expect "password:" { send "$password\r" }
expect eof

set start_result [string trim $expect_out(buffer)]
puts "$start_result"
puts ""

# 4. Проверить что процесс запустился
puts "4️⃣ Проверяю процесс..."
spawn ssh $server "ps aux | grep 'uvicorn.*main:app' | grep -v grep | head -1"
expect "password:" { send "$password\r" }
expect eof

set process_check [string trim $expect_out(buffer)]
puts "$process_check"
puts ""

# 5. Проверить доступность API
puts "5️⃣ Проверяю доступность API..."
spawn ssh $server "sleep 2 && curl -s -o /dev/null -w 'HTTP Status: %{http_code}\n' http://localhost:8000/ 2>&1"
expect "password:" { send "$password\r" }
expect eof

set api_check [string trim $expect_out(buffer)]
puts "$api_check"
puts ""

# 6. Проверить логи на ошибки
puts "6️⃣ Проверяю логи на ошибки..."
spawn ssh $server "tail -30 /tmp/payment_service.log 2>&1 | grep -i error || echo 'NO_ERRORS'"
expect "password:" { send "$password\r" }
expect eof

set errors_check [string trim $expect_out(buffer)]
puts "$errors_check"
puts ""

# 7. Тестировать admin endpoint
puts "7️⃣ Тестирую admin endpoint..."
spawn ssh $server "curl -s -H 'X-Admin-Key: ADMIN_SECRET_KEY_CHANGE_IN_PRODUCTION' http://localhost:8000/api/admin/metrics/system 2>&1 | head -10"
expect "password:" { send "$password\r" }
expect eof

set test_endpoint [string trim $expect_out(buffer)]
puts "$test_endpoint"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

