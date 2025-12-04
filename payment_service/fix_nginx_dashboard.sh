#!/usr/bin/expect -f

# Исправление Nginx конфигурации для /dashboard

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ИСПРАВЛЕНИЕ NGINX КОНФИГУРАЦИИ"
puts "=========================================="
puts ""

# 1. Создать бэкап
puts "1️⃣ Создаю бэкап текущей конфигурации..."
spawn ssh $server "cp /etc/nginx/sites-enabled/aladdin-ai.ru /etc/nginx/sites-enabled/aladdin-ai.ru.backup_\$(date +%Y%m%d_%H%M%S) && echo 'BACKUP_CREATED'"
expect "password:" { send "$password\r" }
expect eof

set backup_result [string trim $expect_out(buffer)]
puts "Результат: $backup_result"
puts ""

# 2. Исправить путь в конфигурации
puts "2️⃣ Исправляю путь в конфигурации..."
spawn ssh $server "sed -i 's|alias /var/www/html/dashboard/;|alias /var/www/aladdin-ai.ru/dashboard/;|g' /etc/nginx/sites-enabled/aladdin-ai.ru && echo 'PATH_FIXED'"
expect "password:" { send "$password\r" }
expect eof

set fix_result [string trim $expect_out(buffer)]
puts "Результат: $fix_result"
puts ""

# 3. Проверить конфигурацию
puts "3️⃣ Проверяю конфигурацию Nginx..."
spawn ssh $server "nginx -t 2>&1"
expect "password:" { send "$password\r" }
expect eof

set test_result [string trim $expect_out(buffer)]
puts "Результат:"
puts "$test_result"
puts ""

# 4. Перезагрузить Nginx
puts "4️⃣ Перезагружаю Nginx..."
spawn ssh $server "systemctl reload nginx && echo 'NGINX_RELOADED'"
expect "password:" { send "$password\r" }
expect eof

set reload_result [string trim $expect_out(buffer)]
puts "Результат: $reload_result"
puts ""

# 5. Проверить что страница работает
puts "5️⃣ Проверяю что страница /dashboard работает..."
spawn ssh $server "sleep 2 && curl -s -o /dev/null -w 'HTTP %{http_code}' https://aladdin-ai.ru/dashboard/ 2>&1"
expect "password:" { send "$password\r" }
expect eof

set page_test [string trim $expect_out(buffer)]
puts "Результат: $page_test"
if {[string match "*200*" $page_test]} {
    puts "✅ Страница /dashboard работает!"
} else {
    puts "❌ Страница /dashboard все еще не работает"
}
puts ""

puts "=========================================="
puts "✅ Исправление завершено!"
puts ""

