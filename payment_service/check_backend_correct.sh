#!/usr/bin/expect -f

# Правильная проверка payment_service

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"
set service_dir "/opt/aladdin-backend"

puts "🔍 ПРОВЕРКА BACKEND (правильная директория)"
puts "=========================================="
puts ""

# 1. Проверить директорию /opt/aladdin-backend
puts "1️⃣ Проверяем директорию /opt/aladdin-backend..."
spawn ssh $server "ls -la ${service_dir}/ 2>&1 | head -20"
expect "password:" { send "$password\r" }
expect eof

set dir_list [string trim $expect_out(buffer)]
puts "Результат:"
puts "$dir_list"
puts ""

# 2. Проверить main.py
puts "2️⃣ Проверяем main.py..."
spawn ssh $server "ls -lh ${service_dir}/main.py 2>&1"
expect "password:" { send "$password\r" }
expect eof

set main_file [string trim $expect_out(buffer)]
puts "Результат: $main_file"
puts ""

# 3. Проверить директорию app/
puts "3️⃣ Проверяем директорию app/..."
spawn ssh $server "ls -la ${service_dir}/app/ 2>&1 | head -20"
expect "password:" { send "$password\r" }
expect eof

set app_dir [string trim $expect_out(buffer)]
puts "Результат:"
puts "$app_dir"
puts ""

# 4. Проверить dashboard_stats.py
puts "4️⃣ Проверяем dashboard_stats.py..."
spawn ssh $server "ls -lh ${service_dir}/app/dashboard_stats.py 2>&1"
expect "password:" { send "$password\r" }
expect eof

set dashboard_file [string trim $expect_out(buffer)]
puts "Результат: $dashboard_file"
puts ""

# 5. Проверить импорты в main.py
puts "5️⃣ Проверяем импорты dashboard_stats в main.py..."
spawn ssh $server "grep -n 'dashboard_stats' ${service_dir}/main.py 2>&1 | head -5"
expect "password:" { send "$password\r" }
expect eof

set imports [string trim $expect_out(buffer)]
puts "Результат:"
if {[string length $imports] > 0} {
    puts "$imports"
} else {
    puts "❌ Импорты dashboard_stats НЕ найдены"
}
puts ""

# 6. Проверить endpoints dashboard
puts "6️⃣ Проверяем endpoints /api/dashboard в main.py..."
spawn ssh $server "grep -n '/api/dashboard' ${service_dir}/main.py 2>&1 | head -5"
expect "password:" { send "$password\r" }
expect eof

set endpoints [string trim $expect_out(buffer)]
puts "Результат:"
if {[string length $endpoints] > 0} {
    puts "$endpoints"
} else {
    puts "❌ Endpoints dashboard НЕ найдены"
}
puts ""

# 7. Проверить логи service
puts "7️⃣ Проверяем последние логи payment_service..."
spawn ssh $server "tail -20 /tmp/payment_service.log 2>&1 || journalctl -u payment_service -n 20 --no-pager 2>&1"
expect "password:" { send "$password\r" }
expect eof

set logs [string trim $expect_out(buffer)]
puts "Результат:"
puts "$logs"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

