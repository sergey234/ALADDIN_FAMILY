#!/usr/bin/expect -f

# Загрузка исправлений

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "📤 ЗАГРУЗКА ИСПРАВЛЕНИЙ"
puts "=========================================="
puts ""

# 1. admin_endpoints.py
puts "1️⃣ Загружаю admin_endpoints.py..."
spawn scp ../payment_service/app/admin_endpoints.py $server:/opt/aladdin-backend/app/admin_endpoints.py
expect "password:" { send "$password\r" }
expect eof

puts "✅ admin_endpoints.py загружен"
puts ""

# 2. Остановить и перезапустить payment_service
puts "2️⃣ Перезапускаю payment_service..."
spawn ssh $server "lsof -ti :8000 | xargs kill -9 2>&1; sleep 2; cd /opt/aladdin-backend && source venv/bin/activate && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/payment_service.log 2>&1 & sleep 3 && echo 'SERVICE_RESTARTED'"
expect "password:" { send "$password\r" }
expect eof

set restart_result [string trim $expect_out(buffer)]
puts "$restart_result"
puts ""

# 3. Проверить что работает
puts "3️⃣ Проверяю что работает..."
spawn ssh $server "sleep 2 && curl -s -H 'X-Admin-Key: ADMIN_SECRET_KEY_CHANGE_IN_PRODUCTION' 'http://localhost:8000/api/admin/users/list?limit=2' | python3 -m json.tool 2>&1 | head -10"
expect "password:" { send "$password\r" }
expect eof

set test_result [string trim $expect_out(buffer)]
puts "$test_result"
puts ""

puts "=========================================="
puts "✅ Исправления загружены!"
puts ""

