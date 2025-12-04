#!/usr/bin/expect -f

# Проверка API endpoints админки

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"
set admin_key "ADMIN_SECRET_KEY_CHANGE_IN_PRODUCTION"

puts "🔍 ПРОВЕРКА ADMIN API ENDPOINTS"
puts "=========================================="
puts ""

# 1. Проверить что payment_service работает
puts "1️⃣ Проверяю payment_service..."
spawn ssh $server "ps aux | grep 'uvicorn.*main:app' | grep -v grep | head -1"
expect "password:" { send "$password\r" }
expect eof

set service_status [string trim $expect_out(buffer)]
puts "$service_status"
puts ""

# 2. Проверить доступность API
puts "2️⃣ Проверяю доступность API на порту 8000..."
spawn ssh $server "curl -s -o /dev/null -w 'HTTP Status: %{http_code}\n' http://localhost:8000/ || echo 'API_NOT_ACCESSIBLE'"
expect "password:" { send "$password\r" }
expect eof

set api_status [string trim $expect_out(buffer)]
puts "$api_status"
puts ""

# 3. Проверить /api/admin/metrics/system
puts "3️⃣ Проверяю /api/admin/metrics/system..."
spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' http://localhost:8000/api/admin/metrics/system | head -30"
expect "password:" { send "$password\r" }
expect eof

set system_metrics [string trim $expect_out(buffer)]
puts "$system_metrics"
puts ""

# 4. Проверить /api/admin/metrics/users
puts "4️⃣ Проверяю /api/admin/metrics/users..."
spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' http://localhost:8000/api/admin/metrics/users | head -30"
expect "password:" { send "$password\r" }
expect eof

set users_metrics [string trim $expect_out(buffer)]
puts "$users_metrics"
puts ""

# 5. Проверить /api/admin/metrics/threats
puts "5️⃣ Проверяю /api/admin/metrics/threats..."
spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' http://localhost:8000/api/admin/metrics/threats | head -30"
expect "password:" { send "$password\r" }
expect eof

set threats_metrics [string trim $expect_out(buffer)]
puts "$threats_metrics"
puts ""

# 6. Проверить /api/admin/users/list
puts "6️⃣ Проверяю /api/admin/users/list..."
spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' 'http://localhost:8000/api/admin/users/list?limit=5' | head -30"
expect "password:" { send "$password\r" }
expect eof

set users_list [string trim $expect_out(buffer)]
puts "$users_list"
puts ""

# 7. Проверить /api/admin/threats/list
puts "7️⃣ Проверяю /api/admin/threats/list..."
spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' 'http://localhost:8000/api/admin/threats/list?limit=5' | head -30"
expect "password:" { send "$password\r" }
expect eof

set threats_list [string trim $expect_out(buffer)]
puts "$threats_list"
puts ""

# 8. Проверить /api/admin/logs
puts "8️⃣ Проверяю /api/admin/logs..."
spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' 'http://localhost:8000/api/admin/logs?service=payment_service&limit=5' | head -30"
expect "password:" { send "$password\r" }
expect eof

set logs_result [string trim $expect_out(buffer)]
puts "$logs_result"
puts ""

# 9. Проверить права на выполнение команд для логов
puts "9️⃣ Проверяю права на выполнение команд..."
spawn ssh $server "whoami && id && journalctl --version 2>&1 | head -1"
expect "password:" { send "$password\r" }
expect eof

set permissions [string trim $expect_out(buffer)]
puts "$permissions"
puts ""

# 10. Проверить что команды для логов работают
puts "🔟 Проверяю команду journalctl..."
spawn ssh $server "journalctl -u payment_service -n 3 --no-pager 2>&1 | head -5"
expect "password:" { send "$password\r" }
expect eof

set journalctl_test [string trim $expect_out(buffer)]
puts "$journalctl_test"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

