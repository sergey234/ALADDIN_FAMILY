#!/usr/bin/expect -f

# Финальная проверка админки

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ФИНАЛЬНАЯ ПРОВЕРКА АДМИНКИ"
puts "=========================================="
puts ""

# 1. Проверить все страницы
puts "1️⃣ Проверяю страницы..."
spawn ssh $server "curl -s -o /dev/null -w 'login.html: %{http_code}, ' https://aladdin-ai.ru/admin/login.html 2>&1 && curl -s -o /dev/null -w 'index.html: %{http_code}' https://aladdin-ai.ru/admin/index.html 2>&1"
expect "password:" { send "$password\r" }
expect eof

set pages_test [string trim $expect_out(buffer)]
puts "Результат: $pages_test"
puts ""

# 2. Проверить CSS и JS
puts "2️⃣ Проверяю CSS и JS..."
spawn ssh $server "curl -s -o /dev/null -w 'admin.css: %{http_code}, ' https://aladdin-ai.ru/admin/css/admin.css 2>&1 && curl -s -o /dev/null -w 'admin.js: %{http_code}' https://aladdin-ai.ru/admin/js/admin.js 2>&1"
expect "password:" { send "$password\r" }
expect eof

set assets_test [string trim $expect_out(buffer)]
puts "Результат: $assets_test"
puts ""

# 3. Проверить структуру файлов
puts "3️⃣ Проверяю структуру файлов..."
spawn ssh $server "ls -lh /var/www/aladdin-ai.ru/admin/*.html /var/www/aladdin-ai.ru/admin/css/*.css /var/www/aladdin-ai.ru/admin/js/*.js 2>&1"
expect "password:" { send "$password\r" }
expect eof

set files_structure [string trim $expect_out(buffer)]
puts "Результат:"
puts "$files_structure"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

