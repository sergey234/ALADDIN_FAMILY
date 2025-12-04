#!/usr/bin/expect -f

# ШАГ 1: Создать бэкап старого main.py

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "📦 ШАГ 1: Создаю бэкап старого main.py..."
puts ""

spawn ssh $server "cd /opt/aladdin-backend && cp main.py main.py.backup_\$(date +%Y%m%d_%H%M%S) && ls -lh main.py.backup_* | tail -1"
expect "password:" { send "$password\r" }
expect eof

set result [string trim $expect_out(buffer)]
puts "Результат:"
puts "$result"
puts ""
puts "✅ Бэкап создан!"
puts ""

