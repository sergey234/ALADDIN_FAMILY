#!/usr/bin/expect -f

# ШАГ 1: Создать бэкап и загрузить main.py

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "📦 ШАГ 1: Создаю бэкап и загружаю main.py..."
puts ""

# Бэкап
spawn ssh $server "cd /opt/aladdin-backend && cp main.py main.py.backup_admin_\$(date +%Y%m%d_%H%M%S) && echo 'BACKUP_CREATED'"
expect "password:" { send "$password\r" }
expect eof

set backup_result [string trim $expect_out(buffer)]
puts "Бэкап: $backup_result"
puts ""

# Загрузка main.py
spawn scp main.py $server:/opt/aladdin-backend/main.py
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ main.py загружен!"
puts ""

