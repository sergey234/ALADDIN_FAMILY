#!/usr/bin/expect -f

# ШАГ 7: Проверить что все работает

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ШАГ 7: Проверяю что все работает..."
puts ""

# 1. Проверить что процесс запустился
puts "1️⃣ Проверяю что процесс запустился..."
spawn ssh $server "ps aux | grep 'uvicorn.*main:app.*8000' | grep -v grep | head -1"
expect "password:" { send "$password\r" }
expect eof

set process_info [string trim $expect_out(buffer)]
puts "Результат (процесс):"
if {[string length $process_info] > 0} {
    puts "✅ $process_info"
} else {
    puts "❌ Процесс не найден!"
}
puts ""

# 2. Проверить старый endpoint
puts "2️⃣ Проверяю старый endpoint /api/payment-methods..."
spawn ssh $server "curl -s -o /dev/null -w 'HTTP %{http_code}' http://localhost:8000/api/payment-methods 2>&1"
expect "password:" { send "$password\r" }
expect eof

set old_endpoint [string trim $expect_out(buffer)]
puts "Результат: $old_endpoint"
if {[string match "*200*" $old_endpoint]} {
    puts "✅ Старые endpoints работают!"
} else {
    puts "❌ Старые endpoints НЕ работают!"
}
puts ""

# 3. Проверить новый dashboard endpoint
puts "3️⃣ Проверяю новый endpoint /api/dashboard/public/stats..."
spawn ssh $server "curl -s -o /dev/null -w 'HTTP %{http_code}' http://localhost:8000/api/dashboard/public/stats 2>&1"
expect "password:" { send "$password\r" }
expect eof

set new_endpoint [string trim $expect_out(buffer)]
puts "Результат: $new_endpoint"
if {[string match "*200*" $new_endpoint]} {
    puts "✅ Новые dashboard endpoints работают!"
} else {
    puts "❌ Новые dashboard endpoints НЕ работают!"
}
puts ""

# 4. Проверить содержимое dashboard endpoint
puts "4️⃣ Проверяю содержимое dashboard endpoint..."
spawn ssh $server "curl -s http://localhost:8000/api/dashboard/public/stats 2>&1 | head -20"
expect "password:" { send "$password\r" }
expect eof

set dashboard_content [string trim $expect_out(buffer)]
puts "Результат (первые 20 строк):"
puts "$dashboard_content"
puts ""

puts "=========================================="
puts "✅ ПРОВЕРКА ЗАВЕРШЕНА!"
puts ""

