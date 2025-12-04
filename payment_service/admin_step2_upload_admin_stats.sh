#!/usr/bin/expect -f

# ШАГ 2: Загрузить admin_stats.py

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "📤 ШАГ 2: Загружаю admin_stats.py..."
puts ""

spawn scp app/admin_stats.py $server:/opt/aladdin-backend/app/admin_stats.py
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ admin_stats.py загружен!"
puts ""

