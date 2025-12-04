#!/usr/bin/expect -f

# ШАГ 2: Загрузить новый main.py

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "📤 ШАГ 2: Загружаю новый main.py..."
puts ""

spawn scp main.py $server:/opt/aladdin-backend/main.py
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ main.py загружен!"
puts ""

