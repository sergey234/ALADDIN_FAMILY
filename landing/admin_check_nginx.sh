#!/usr/bin/expect -f

# Проверка Nginx конфигурации для /admin

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА NGINX ДЛЯ /admin"
puts "=========================================="
puts ""

# Проверить конфигурацию
puts "1️⃣ Проверяю Nginx конфигурацию для /admin..."
spawn ssh $server "grep -A 10 'location /admin' /etc/nginx/sites-enabled/aladdin-ai.ru 2>&1 | head -15"
expect "password:" { send "$password\r" }
expect eof

set nginx_config [string trim $expect_out(buffer)]
puts "Результат:"
puts "$nginx_config"
puts ""

# Проверить логи
puts "2️⃣ Проверяю логи Nginx..."
spawn ssh $server "tail -10 /var/log/nginx/error.log | grep -i admin 2>&1 || echo 'NO_ERRORS'"
expect "password:" { send "$password\r" }
expect eof

set nginx_errors [string trim $expect_out(buffer)]
puts "Результат:"
puts "$nginx_errors"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

