#!/usr/bin/expect -f

# Тестирование admin API endpoints

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"
set admin_key "ADMIN_SECRET_KEY_CHANGE_IN_PRODUCTION"

puts "🧪 ТЕСТИРОВАНИЕ ADMIN API"
puts "=========================================="
puts ""

# 1. System metrics
puts "1️⃣ Тестирую /api/admin/metrics/system..."
spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' http://localhost:8000/api/admin/metrics/system | head -20"
expect "password:" { send "$password\r" }
expect eof

set system_result [string trim $expect_out(buffer)]
puts "$system_result"
puts ""

# 2. Users metrics
puts "2️⃣ Тестирую /api/admin/metrics/users..."
spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' http://localhost:8000/api/admin/metrics/users | head -20"
expect "password:" { send "$password\r" }
expect eof

set users_result [string trim $expect_out(buffer)]
puts "$users_result"
puts ""

# 3. Threats metrics
puts "3️⃣ Тестирую /api/admin/metrics/threats..."
spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' http://localhost:8000/api/admin/metrics/threats | head -20"
expect "password:" { send "$password\r" }
expect eof

set threats_result [string trim $expect_out(buffer)]
puts "$threats_result"
puts ""

# 4. Users list
puts "4️⃣ Тестирую /api/admin/users/list..."
spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' 'http://localhost:8000/api/admin/users/list?limit=5' | head -30"
expect "password:" { send "$password\r" }
expect eof

set users_list_result [string trim $expect_out(buffer)]
puts "$users_list_result"
puts ""

# 5. Threats list
puts "5️⃣ Тестирую /api/admin/threats/list..."
spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' 'http://localhost:8000/api/admin/threats/list?limit=5' | head -30"
expect "password:" { send "$password\r" }
expect eof

set threats_list_result [string trim $expect_out(buffer)]
puts "$threats_list_result"
puts ""

# 6. Logs
puts "6️⃣ Тестирую /api/admin/logs..."
spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' 'http://localhost:8000/api/admin/logs?service=payment_service&limit=10' | head -30"
expect "password:" { send "$password\r" }
expect eof

set logs_result [string trim $expect_out(buffer)]
puts "$logs_result"
puts ""

puts "=========================================="
puts "✅ Тестирование завершено!"
puts ""

