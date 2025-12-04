#!/usr/bin/expect -f

# Загрузка обновленного logs.html

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "📤 ЗАГРУЗКА ОБНОВЛЕННОГО logs.html"
puts "=========================================="
puts ""

spawn scp admin/logs.html $server:/var/www/aladdin-ai.ru/admin/logs.html
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ Файл загружен!"
puts ""
puts "💡 Обновите страницу в браузере (Ctrl+F5) чтобы увидеть все кнопки!"
puts ""

