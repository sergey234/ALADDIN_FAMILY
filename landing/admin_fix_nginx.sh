#!/usr/bin/expect -f

# Исправление Nginx конфигурации для /admin

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ИСПРАВЛЕНИЕ NGINX ДЛЯ /admin"
puts "=========================================="
puts ""

# Исправить путь
puts "1️⃣ Исправляю путь в конфигурации..."
spawn ssh $server "sed -i 's|alias /var/www/html/admin/;|alias /var/www/aladdin-ai.ru/admin/;|g' /etc/nginx/sites-enabled/aladdin-ai.ru && echo 'PATH_FIXED'"
expect "password:" { send "$password\r" }
expect eof

set fix_result [string trim $expect_out(buffer)]
puts "Результат: $fix_result"
puts ""

# Проверить конфигурацию
puts "2️⃣ Проверяю конфигурацию..."
spawn ssh $server "nginx -t 2>&1 | tail -2"
expect "password:" { send "$password\r" }
expect eof

set test_result [string trim $expect_out(buffer)]
puts "Результат:"
puts "$test_result"
puts ""

# Перезагрузить Nginx
puts "3️⃣ Перезагружаю Nginx..."
spawn ssh $server "systemctl reload nginx && echo 'NGINX_RELOADED'"
expect "password:" { send "$password\r" }
expect eof

set reload_result [string trim $expect_out(buffer)]
puts "Результат: $reload_result"
puts ""

# Проверить страницу
puts "4️⃣ Проверяю страницу /admin/login.html..."
spawn ssh $server "sleep 2 && curl -s -o /dev/null -w 'HTTP %{http_code}' https://aladdin-ai.ru/admin/login.html 2>&1"
expect "password:" { send "$password\r" }
expect eof

set page_test [string trim $expect_out(buffer)]
puts "Результат: $page_test"
if {[string match "*200*" $page_test]} {
    puts "✅ Страница /admin/login.html работает!"
} else {
    puts "⚠️ Страница все еще не работает"
}
puts ""

puts "=========================================="
puts "✅ Исправление завершено!"
puts ""

