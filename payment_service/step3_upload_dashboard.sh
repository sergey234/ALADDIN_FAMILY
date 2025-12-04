#!/usr/bin/expect -f

# ШАГ 3: Загрузить dashboard_stats.py

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "📤 ШАГ 3: Загружаю dashboard_stats.py..."
puts ""

spawn scp app/dashboard_stats.py $server:/opt/aladdin-backend/app/dashboard_stats.py
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ dashboard_stats.py загружен!"
puts ""

