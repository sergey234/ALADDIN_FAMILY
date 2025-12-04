#!/usr/bin/expect -f

# ШАГ 5: Установить права и проверить

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔐 ШАГ 5: Устанавливаю права и проверяю..."
puts ""

# Установить права
spawn ssh $server "chown -R www-data:www-data /var/www/aladdin-ai.ru/admin && chmod -R 755 /var/www/aladdin-ai.ru/admin && ls -lh /var/www/aladdin-ai.ru/admin/*.html 2>&1"
expect "password:" { send "$password\r" }
expect eof

set permissions_result [string trim $expect_out(buffer)]
puts "Результат (права):"
puts "$permissions_result"
puts ""

# Проверить структуру
spawn ssh $server "find /var/www/aladdin-ai.ru/admin -type f 2>&1 | sort"
expect "password:" { send "$password\r" }
expect eof

set structure_result [string trim $expect_out(buffer)]
puts "Результат (структура файлов):"
puts "$structure_result"
puts ""

# Проверить доступность страницы
spawn ssh $server "curl -s -o /dev/null -w 'HTTP %{http_code}' https://aladdin-ai.ru/admin/login.html 2>&1"
expect "password:" { send "$password\r" }
expect eof

set page_test [string trim $expect_out(buffer)]
puts "Результат (доступность): $page_test"
if {[string match "*200*" $page_test]} {
    puts "✅ Страница /admin/login.html доступна!"
} else {
    puts "⚠️ Проверьте доступность страницы"
}
puts ""

puts "✅ Проверка завершена!"
puts ""

