#!/usr/bin/expect -f

# Деплой всех логов в админку

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "📤 ДЕПЛОЙ ВСЕХ ЛОГОВ В АДМИНКУ"
puts "=========================================="
puts ""

# 1. Загрузить admin_endpoints.py
puts "1️⃣ Загружаю admin_endpoints.py..."
spawn scp ../payment_service/app/admin_endpoints.py $server:/opt/aladdin-backend/app/admin_endpoints.py
expect "password:" { send "$password\r" }
expect eof

puts "✅ admin_endpoints.py загружен"
puts ""

# 2. Загрузить logs.html
puts "2️⃣ Загружаю logs.html..."
spawn scp admin/logs.html $server:/var/www/aladdin-ai.ru/admin/logs.html
expect "password:" { send "$password\r" }
expect eof

puts "✅ logs.html загружен"
puts ""

# 3. Перезапустить payment_service
puts "3️⃣ Перезапускаю payment_service..."
spawn ssh $server "lsof -ti :8000 | xargs kill -9 2>&1; sleep 2; cd /opt/aladdin-backend && source venv/bin/activate && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/payment_service.log 2>&1 & sleep 3 && echo 'SERVICE_RESTARTED'"
expect "password:" { send "$password\r" }
expect eof

set restart_result [string trim $expect_out(buffer)]
puts "$restart_result"
puts ""

# 4. Проверить что работает
puts "4️⃣ Проверяю что работает..."
spawn ssh $server "sleep 2 && curl -s -H 'X-Admin-Key: ADMIN_SECRET_KEY_CHANGE_IN_PRODUCTION' 'http://localhost:8000/api/admin/logs?service=security&limit=5' | python3 -m json.tool 2>&1 | head -10"
expect "password:" { send "$password\r" }
expect eof

set test_result [string trim $expect_out(buffer)]
puts "$test_result"
puts ""

puts "=========================================="
puts "✅ Все логи добавлены в админку!"
puts ""

