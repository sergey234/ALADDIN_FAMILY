#!/usr/bin/expect -f

# ШАГ 5: Проверить что все работает

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ШАГ 5: Проверяю что все работает..."
puts ""

# 1. Проверить что процесс запустился
puts "1️⃣ Проверяю что процесс запустился..."
spawn ssh $server "ps aux | grep 'uvicorn.*main:app.*8000' | grep -v grep | head -1"
expect "password:" { send "$password\r" }
expect eof

set process_info [string trim $expect_out(buffer)]
puts "Результат:"
if {[string length $process_info] > 0} {
    puts "✅ $process_info"
} else {
    puts "❌ Процесс не найден!"
}
puts ""

# 2. Проверить старые endpoints
puts "2️⃣ Проверяю старые endpoints..."
spawn ssh $server "curl -s -o /dev/null -w 'payment-methods: %{http_code}, ' http://localhost:8000/api/payment-methods 2>&1 && curl -s -o /dev/null -w 'dashboard/public/stats: %{http_code}' http://localhost:8000/api/dashboard/public/stats 2>&1"
expect "password:" { send "$password\r" }
expect eof

set old_endpoints [string trim $expect_out(buffer)]
puts "Результат: $old_endpoints"
puts ""

# 3. Проверить новые admin endpoints (без ключа - должна быть ошибка 401)
puts "3️⃣ Проверяю admin endpoints (без ключа - должна быть 401)..."
spawn ssh $server "curl -s -o /dev/null -w 'system: %{http_code}, ' http://localhost:8000/api/admin/metrics/system 2>&1 && curl -s -o /dev/null -w 'users: %{http_code}, ' http://localhost:8000/api/admin/metrics/users 2>&1 && curl -s -o /dev/null -w 'threats: %{http_code}' http://localhost:8000/api/admin/metrics/threats 2>&1"
expect "password:" { send "$password\r" }
expect eof

set admin_endpoints_no_key [string trim $expect_out(buffer)]
puts "Результат (без ключа): $admin_endpoints_no_key"
puts ""

# 4. Проверить admin endpoints с правильным ключом (нужно получить admin_key из настроек)
puts "4️⃣ Проверяю admin endpoints с ключом..."
spawn ssh $server "ADMIN_KEY=\$(grep ADMIN_KEY /opt/aladdin-backend/.env 2>/dev/null | cut -d'=' -f2 | tr -d '\"') || ADMIN_KEY='test'; curl -s -o /dev/null -w 'system: %{http_code}' -H \"X-Admin-Key: \$ADMIN_KEY\" http://localhost:8000/api/admin/metrics/system 2>&1"
expect "password:" { send "$password\r" }
expect eof

set admin_with_key [string trim $expect_out(buffer)]
puts "Результат (с ключом): $admin_with_key"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

