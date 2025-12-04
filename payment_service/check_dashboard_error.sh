#!/usr/bin/expect -f

# Проверка ошибки на странице /dashboard

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА ОШИБКИ /dashboard"
puts "=========================================="
puts ""

# 1. Проверить логи Nginx
puts "1️⃣ Проверяю логи Nginx для /dashboard..."
spawn ssh $server "tail -20 /var/log/nginx/error.log | grep -i dashboard 2>&1 || echo 'NO_ERRORS'"
expect "password:" { send "$password\r" }
expect eof

set nginx_errors [string trim $expect_out(buffer)]
puts "Результат (Nginx ошибки):"
puts "$nginx_errors"
puts ""

# 2. Проверить содержимое страницы
puts "2️⃣ Проверяю содержимое страницы /dashboard..."
spawn ssh $server "curl -s https://aladdin-ai.ru/dashboard/ 2>&1 | head -30"
expect "password:" { send "$password\r" }
expect eof

set page_content [string trim $expect_out(buffer)]
puts "Результат (первые 30 строк):"
puts "$page_content"
puts ""

# 3. Проверить Nginx конфигурацию для /dashboard
puts "3️⃣ Проверяю Nginx конфигурацию для /dashboard..."
spawn ssh $server "grep -A 10 'location /dashboard' /etc/nginx/sites-enabled/* 2>&1 | head -15"
expect "password:" { send "$password\r" }
expect eof

set nginx_config [string trim $expect_out(buffer)]
puts "Результат (Nginx config):"
puts "$nginx_config"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

