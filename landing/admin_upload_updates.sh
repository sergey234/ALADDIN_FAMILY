#!/usr/bin/expect -f

# Загрузка обновленных файлов админки

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "📤 ЗАГРУЗКА ОБНОВЛЕННЫХ ФАЙЛОВ"
puts "=========================================="
puts ""

# 1. index.html
puts "1️⃣ Загружаю index.html..."
spawn scp admin/index.html $server:/var/www/aladdin-ai.ru/admin/index.html
expect "password:" { send "$password\r" }
expect eof

puts "✅ index.html загружен"
puts ""

# 2. admin.js
puts "2️⃣ Загружаю admin.js..."
spawn scp admin/js/admin.js $server:/var/www/aladdin-ai.ru/admin/js/admin.js
expect "password:" { send "$password\r" }
expect eof

puts "✅ admin.js загружен"
puts ""

# 3. admin.css
puts "3️⃣ Загружаю admin.css..."
spawn scp admin/css/admin.css $server:/var/www/aladdin-ai.ru/admin/css/admin.css
expect "password:" { send "$password\r" }
expect eof

puts "✅ admin.css загружен"
puts ""

# 4. login.html
puts "4️⃣ Загружаю login.html..."
spawn scp admin/login.html $server:/var/www/aladdin-ai.ru/admin/login.html
expect "password:" { send "$password\r" }
expect eof

puts "✅ login.html загружен"
puts ""

# 5. main.py (с логированием)
puts "5️⃣ Загружаю main.py (с логированием)..."
spawn scp ../payment_service/main.py $server:/opt/aladdin-backend/main.py
expect "password:" { send "$password\r" }
expect eof

puts "✅ main.py загружен"
puts ""

# 6. Установить права
puts "6️⃣ Устанавливаю права..."
spawn ssh $server "chown -R www-data:www-data /var/www/aladdin-ai.ru/admin && echo 'PERMISSIONS_SET'"
expect "password:" { send "$password\r" }
expect eof

set perm_result [string trim $expect_out(buffer)]
puts "Результат: $perm_result"
puts ""

# 7. Перезапустить payment_service
puts "7️⃣ Перезапускаю payment_service..."
spawn ssh $server "lsof -ti :8000 | xargs kill 2>&1; sleep 2; cd /opt/aladdin-backend && nohup /opt/aladdin-backend/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 & sleep 3 && echo 'SERVICE_RESTARTED'"
expect "password:" { send "$password\r" }
expect eof

set restart_result [string trim $expect_out(buffer)]
puts "Результат: $restart_result"
puts ""

puts "=========================================="
puts "✅ Все файлы загружены!"
puts ""

