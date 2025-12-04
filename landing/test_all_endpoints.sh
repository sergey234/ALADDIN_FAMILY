#!/usr/bin/expect -f

# Тестирование всех endpoints

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"
set admin_key "ADMIN_SECRET_KEY_CHANGE_IN_PRODUCTION"

puts "🧪 ТЕСТИРОВАНИЕ ВСЕХ ENDPOINTS"
puts "=========================================="
puts ""

# 1. System metrics
puts "1️⃣ /api/admin/metrics/system"
spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' http://localhost:8000/api/admin/metrics/system | python3 -m json.tool 2>&1 | head -15"
expect "password:" { send "$password\r" }
expect eof

set system_result [string trim $expect_out(buffer)]
puts "$system_result"
puts ""

# 2. Users metrics
puts "2️⃣ /api/admin/metrics/users"
spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' http://localhost:8000/api/admin/metrics/users | python3 -m json.tool 2>&1 | head -10"
expect "password:" { send "$password\r" }
expect eof

set users_result [string trim $expect_out(buffer)]
puts "$users_result"
puts ""

# 3. Threats metrics
puts "3️⃣ /api/admin/metrics/threats"
spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' http://localhost:8000/api/admin/metrics/threats | python3 -m json.tool 2>&1 | head -10"
expect "password:" { send "$password\r" }
expect eof

set threats_result [string trim $expect_out(buffer)]
puts "$threats_result"
puts ""

# 4. Users list
puts "4️⃣ /api/admin/users/list"
spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' 'http://localhost:8000/api/admin/users/list?limit=3' | python3 -m json.tool 2>&1 | head -20"
expect "password:" { send "$password\r" }
expect eof

set users_list_result [string trim $expect_out(buffer)]
puts "$users_list_result"
puts ""

# 5. Threats list
puts "5️⃣ /api/admin/threats/list"
spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' 'http://localhost:8000/api/admin/threats/list?limit=3' | python3 -m json.tool 2>&1 | head -20"
expect "password:" { send "$password\r" }
expect eof

set threats_list_result [string trim $expect_out(buffer)]
puts "$threats_list_result"
puts ""

# 6. Logs
puts "6️⃣ /api/admin/logs"
spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' 'http://localhost:8000/api/admin/logs?service=payment_service&limit=5' | python3 -m json.tool 2>&1 | head -20"
expect "password:" { send "$password\r" }
expect eof

set logs_result [string trim $expect_out(buffer)]
puts "$logs_result"
puts ""

# 7. Проверить права на команды для логов
puts "7️⃣ Проверяю права на команды..."
spawn ssh $server "journalctl --version > /dev/null 2>&1 && echo 'journalctl: OK' || echo 'journalctl: FAIL'; tail --version > /dev/null 2>&1 && echo 'tail: OK' || echo 'tail: FAIL'"
expect "password:" { send "$password\r" }
expect eof

set commands_check [string trim $expect_out(buffer)]
puts "$commands_check"
puts ""

# 8. Проверить что команды выполняются
puts "8️⃣ Тестирую команду journalctl..."
spawn ssh $server "journalctl -u nginx -n 2 --no-pager 2>&1 | head -3"
expect "password:" { send "$password\r" }
expect eof

set journalctl_test [string trim $expect_out(buffer)]
puts "$journalctl_test"
puts ""

puts "=========================================="
puts "✅ Тестирование завершено!"
puts ""

