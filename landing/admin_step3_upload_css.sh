#!/usr/bin/expect -f

# ШАГ 3: Загрузить CSS

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "📤 ШАГ 3: Загружаю admin.css..."
puts ""

spawn scp admin/css/admin.css $server:/var/www/aladdin-ai.ru/admin/css/admin.css
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ admin.css загружен!"
puts ""

