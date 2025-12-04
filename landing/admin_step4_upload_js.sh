#!/usr/bin/expect -f

# ШАГ 4: Загрузить JavaScript

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "📤 ШАГ 4: Загружаю admin.js..."
puts ""

spawn scp admin/js/admin.js $server:/var/www/aladdin-ai.ru/admin/js/admin.js
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ admin.js загружен!"
puts ""

