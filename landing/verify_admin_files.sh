#!/usr/bin/expect -f

# Проверка файлов админки на сервере

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА ФАЙЛОВ АДМИНКИ НА СЕРВЕРЕ"
puts "=========================================="
puts ""

# 1. Проверить admin.js
puts "1️⃣ Проверяю admin.js..."
spawn ssh $server "grep -n 'window.adminAPI' /var/www/aladdin-ai.ru/admin/js/admin.js | head -5"
expect "password:" { send "$password\r" }
expect eof

set admin_js_check [string trim $expect_out(buffer)]
puts "$admin_js_check"
puts ""

# 2. Проверить наличие apiRequest в экспорте
puts "2️⃣ Проверяю экспорт apiRequest..."
spawn ssh $server "grep -A 10 'window.adminAPI =' /var/www/aladdin-ai.ru/admin/js/admin.js"
expect "password:" { send "$password\r" }
expect eof

set export_check [string trim $expect_out(buffer)]
puts "$export_check"
puts ""

# 3. Проверить logs.html
puts "3️⃣ Проверяю logs.html..."
spawn ssh $server "grep -n 'window.adminAPI.apiRequest' /var/www/aladdin-ai.ru/admin/logs.html | head -3"
expect "password:" { send "$password\r" }
expect eof

set logs_check [string trim $expect_out(buffer)]
puts "$logs_check"
puts ""

# 4. Проверить users.html
puts "4️⃣ Проверяю users.html..."
spawn ssh $server "grep -n 'window.adminAPI.apiRequest' /var/www/aladdin-ai.ru/admin/users.html | head -3"
expect "password:" { send "$password\r" }
expect eof

set users_check [string trim $expect_out(buffer)]
puts "$users_check"
puts ""

# 5. Проверить размеры файлов
puts "5️⃣ Проверяю размеры файлов..."
spawn ssh $server "ls -lh /var/www/aladdin-ai.ru/admin/js/admin.js /var/www/aladdin-ai.ru/admin/logs.html /var/www/aladdin-ai.ru/admin/users.html"
expect "password:" { send "$password\r" }
expect eof

set sizes_check [string trim $expect_out(buffer)]
puts "$sizes_check"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

