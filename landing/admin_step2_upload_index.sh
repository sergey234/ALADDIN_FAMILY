#!/usr/bin/expect -f

# ШАГ 2: Загрузить index.html

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "📤 ШАГ 2: Загружаю index.html..."
puts ""

spawn scp admin/index.html $server:/var/www/aladdin-ai.ru/admin/index.html
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ index.html загружен!"
puts ""

