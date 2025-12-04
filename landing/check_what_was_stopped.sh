#!/usr/bin/expect -f

# Проверка что было остановлено и что работает

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА: ЧТО БЫЛО ОСТАНОВЛЕНО И ЧТО РАБОТАЕТ"
puts "=========================================="
puts ""

# 1. Проверить текущие процессы payment_service
puts "1️⃣ Текущие процессы payment_service:"
spawn ssh $server "ps aux | grep 'uvicorn.*main:app' | grep -v grep"
expect "password:" { send "$password\r" }
expect eof

set current_processes [string trim $expect_out(buffer)]
puts "$current_processes"
puts ""

# 2. Проверить что API работает
puts "2️⃣ Проверяю что API работает..."
spawn ssh $server "curl -s -H 'X-Admin-Key: ADMIN_SECRET_KEY_CHANGE_IN_PRODUCTION' http://localhost:8000/api/admin/metrics/system | python3 -m json.tool 2>&1 | head -5"
expect "password:" { send "$password\r" }
expect eof

set api_test [string trim $expect_out(buffer)]
puts "$api_test"
puts ""

# 3. Проверить другие важные сервисы
puts "3️⃣ Проверяю другие важные сервисы..."
spawn ssh $server "ps aux | grep -E 'nginx|api_gateway|mysql|postgres' | grep -v grep | head -10"
expect "password:" { send "$password\r" }
expect eof

set other_services [string trim $expect_out(buffer)]
puts "$other_services"
puts ""

# 4. Проверить что сайт доступен
puts "4️⃣ Проверяю что сайт доступен..."
spawn ssh $server "curl -s -o /dev/null -w 'HTTP Status: %{http_code}\n' https://aladdin-ai.ru/ 2>&1"
expect "password:" { send "$password\r" }
expect eof

set site_check [string trim $expect_out(buffer)]
puts "$site_check"
puts ""

# 5. Проверить что админка доступна
puts "5️⃣ Проверяю что админка доступна..."
spawn ssh $server "curl -s -o /dev/null -w 'HTTP Status: %{http_code}\n' https://aladdin-ai.ru/admin/login.html 2>&1"
expect "password:" { send "$password\r" }
expect eof

set admin_check [string trim $expect_out(buffer)]
puts "$admin_check"
puts ""

# 6. Проверить порт 8000
puts "6️⃣ Проверяю порт 8000..."
spawn ssh $server "lsof -i :8000 2>&1"
expect "password:" { send "$password\r" }
expect eof

set port_check [string trim $expect_out(buffer)]
puts "$port_check"
puts ""

# 7. Проверить порт 8001 (api_gateway)
puts "7️⃣ Проверяю порт 8001 (api_gateway)..."
spawn ssh $server "lsof -i :8001 2>&1 | head -3"
expect "password:" { send "$password\r" }
expect eof

set port_8001 [string trim $expect_out(buffer)]
puts "$port_8001"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

