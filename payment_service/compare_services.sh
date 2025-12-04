#!/usr/bin/expect -f

# Сравнение старого и нового payment_service

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 СРАВНЕНИЕ СТАРОГО И НОВОГО PAYMENT_SERVICE"
puts "=========================================="
puts ""

# 1. Проверить есть ли dashboard endpoints в старом
puts "1️⃣ Проверяем есть ли dashboard endpoints в старом сервисе..."
spawn ssh $server "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/dashboard/public/stats 2>&1"
expect "password:" { send "$password\r" }
expect eof

set dashboard_code [string trim $expect_out(buffer)]
puts "Результат (HTTP код dashboard endpoint): $dashboard_code"
if {[string match "404" $dashboard_code]} {
    puts "❌ Dashboard endpoints НЕТ в старом сервисе"
} else {
    puts "✅ Dashboard endpoints ЕСТЬ (код: $dashboard_code)"
}
puts ""

# 2. Проверить есть ли dashboard_stats.py на сервере
puts "2️⃣ Проверяем есть ли dashboard_stats.py на сервере..."
spawn ssh $server "find /opt/aladdin-backend -name 'dashboard_stats.py' -type f 2>&1 | head -3"
expect "password:" { send "$password\r" }
expect eof

set dashboard_file [string trim $expect_out(buffer)]
puts "Результат (dashboard_stats.py):"
if {[string length $dashboard_file] > 0} {
    puts "✅ Файл найден: $dashboard_file"
} else {
    puts "❌ Файл dashboard_stats.py НЕ найден"
}
puts ""

# 3. Проверить рабочую директорию старого процесса
puts "3️⃣ Проверяем рабочую директорию старого процесса..."
spawn ssh $server "ls -la /proc/535117/cwd 2>&1 | tail -1"
expect "password:" { send "$password\r" }
expect eof

set process_dir [string trim $expect_out(buffer)]
puts "Результат (рабочая директория):"
puts "$process_dir"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

