#!/usr/bin/expect -f

# Загрузка финальных исправлений админки

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "📤 ЗАГРУЗКА ФИНАЛЬНЫХ ИСПРАВЛЕНИЙ"
puts "=========================================="
puts ""

# 1. admin.js
puts "1️⃣ Загружаю admin.js..."
spawn scp admin/js/admin.js $server:/var/www/aladdin-ai.ru/admin/js/admin.js
expect "password:" { send "$password\r" }
expect eof

puts "✅ admin.js загружен"
puts ""

# 2. users.html
puts "2️⃣ Загружаю users.html..."
spawn scp admin/users.html $server:/var/www/aladdin-ai.ru/admin/users.html
expect "password:" { send "$password\r" }
expect eof

puts "✅ users.html загружен"
puts ""

# 3. threats.html
puts "3️⃣ Загружаю threats.html..."
spawn scp admin/threats.html $server:/var/www/aladdin-ai.ru/admin/threats.html
expect "password:" { send "$password\r" }
expect eof

puts "✅ threats.html загружен"
puts ""

# 4. logs.html
puts "4️⃣ Загружаю logs.html..."
spawn scp admin/logs.html $server:/var/www/aladdin-ai.ru/admin/logs.html
expect "password:" { send "$password\r" }
expect eof

puts "✅ logs.html загружен"
puts ""

# 5. Установить права
puts "5️⃣ Устанавливаю права..."
spawn ssh $server "chown -R www-data:www-data /var/www/aladdin-ai.ru/admin && echo 'PERMISSIONS_SET'"
expect "password:" { send "$password\r" }
expect eof

set perm_result [string trim $expect_out(buffer)]
puts "Результат: $perm_result"
puts ""

puts "=========================================="
puts "✅ Все файлы загружены!"
puts ""

