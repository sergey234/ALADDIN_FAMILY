#!/usr/bin/expect -f

# Загрузка новых admin endpoints

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "📤 ЗАГРУЗКА ADMIN ENDPOINTS"
puts "=========================================="
puts ""

# 1. admin_endpoints.py
puts "1️⃣ Загружаю admin_endpoints.py..."
spawn scp ../payment_service/app/admin_endpoints.py $server:/opt/aladdin-backend/app/admin_endpoints.py
expect "password:" { send "$password\r" }
expect eof

puts "✅ admin_endpoints.py загружен"
puts ""

# 2. main.py
puts "2️⃣ Загружаю main.py..."
spawn scp ../payment_service/main.py $server:/opt/aladdin-backend/main.py
expect "password:" { send "$password\r" }
expect eof

puts "✅ main.py загружен"
puts ""

# 3. Перезапустить payment_service
puts "3️⃣ Перезапускаю payment_service..."
spawn ssh $server "lsof -ti :8000 | xargs kill 2>&1; sleep 2; cd /opt/aladdin-backend && nohup /opt/aladdin-backend/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 & sleep 3 && echo 'SERVICE_RESTARTED'"
expect "password:" { send "$password\r" }
expect eof

set restart_result [string trim $expect_out(buffer)]
puts "Результат: $restart_result"
puts ""

puts "=========================================="
puts "✅ Все файлы загружены!"
puts ""

