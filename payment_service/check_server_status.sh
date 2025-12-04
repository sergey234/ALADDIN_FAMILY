#!/usr/bin/expect -f

# Проверка текущего состояния payment_service на сервере

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА ТЕКУЩЕГО СОСТОЯНИЯ НА СЕРВЕРЕ"
puts "=========================================="
puts ""

# 1. Проверить есть ли dashboard endpoints
puts "1️⃣ Проверяем есть ли dashboard endpoints на сервере..."
spawn ssh $server "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/dashboard/public/stats 2>&1"
expect "password:" { send "$password\r" }
expect eof

set dashboard_code [string trim $expect_out(buffer)]
puts "Результат (HTTP код): $dashboard_code"
if {[string match "404" $dashboard_code]} {
    puts "❌ Dashboard endpoints НЕТ - нужно заменить!"
} else {
    puts "✅ Dashboard endpoints ЕСТЬ - уже обновлено?"
}
puts ""

# 2. Проверить есть ли dashboard_stats.py
puts "2️⃣ Проверяем есть ли dashboard_stats.py на сервере..."
spawn ssh $server "ls -la /opt/aladdin-backend/venv/app/dashboard_stats.py 2>&1 || ls -la /opt/aladdin-backend/app/dashboard_stats.py 2>&1 || echo 'NOT_FOUND'"
expect "password:" { send "$password\r" }
expect eof

set dashboard_file [string trim $expect_out(buffer)]
puts "Результат:"
if {[string match "*NOT_FOUND*" $dashboard_file] || [string match "*No such file*" $dashboard_file]} {
    puts "❌ dashboard_stats.py НЕТ - нужно загрузить!"
} else {
    puts "✅ dashboard_stats.py ЕСТЬ:"
    puts "$dashboard_file"
}
puts ""

# 3. Проверить версию main.py (есть ли dashboard)
puts "3️⃣ Проверяем версию main.py на сервере..."
spawn ssh $server "grep -c 'dashboard_stats' /opt/aladdin-backend/venv/main.py 2>&1 || grep -c 'dashboard_stats' /opt/aladdin-backend/main.py 2>&1 || echo '0'"
expect "password:" { send "$password\r" }
expect eof

set main_check [string trim $expect_out(buffer)]
puts "Результат (количество упоминаний dashboard_stats): $main_check"
if {[string match "0" $main_check]} {
    puts "❌ main.py НЕ содержит dashboard_stats - нужно обновить!"
} else {
    puts "✅ main.py содержит dashboard_stats - уже обновлено?"
}
puts ""

# 4. Проверить текущий процесс
puts "4️⃣ Проверяем текущий процесс payment_service..."
spawn ssh $server "ps aux | grep 'uvicorn.*main:app.*8000' | grep -v grep | head -1"
expect "password:" { send "$password\r" }
expect eof

set process_info [string trim $expect_out(buffer)]
puts "Результат (процесс):"
if {[string length $process_info] > 0} {
    puts "$process_info"
} else {
    puts "❌ Процесс не найден"
}
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

