#!/usr/bin/expect -f

# Проверка текущего состояния

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА ТЕКУЩЕГО СОСТОЯНИЯ"
puts "=========================================="
puts ""

# 1. Проверить payment_service
puts "1️⃣ Проверяю payment_service..."
spawn ssh $server "ps aux | grep 'uvicorn.*main:app' | grep -v grep | head -1"
expect "password:" { send "$password\r" }
expect eof

set payment_status [string trim $expect_out(buffer)]
puts "$payment_status"
puts ""

# 2. Проверить порт 8000
puts "2️⃣ Проверяю порт 8000..."
spawn ssh $server "lsof -i :8000 2>&1 | head -3"
expect "password:" { send "$password\r" }
expect eof

set port_status [string trim $expect_out(buffer)]
puts "$port_status"
puts ""

# 3. Проверить API
puts "3️⃣ Проверяю API..."
spawn ssh $server "curl -s -o /dev/null -w 'HTTP Status: %{http_code}\n' http://localhost:8000/ 2>&1"
expect "password:" { send "$password\r" }
expect eof

set api_status [string trim $expect_out(buffer)]
puts "$api_status"
puts ""

# 4. Проверить последние логи Nginx (только новые)
puts "4️⃣ Проверяю ПОСЛЕДНИЕ логи Nginx (последние 3 строки)..."
spawn ssh $server "tail -3 /var/log/nginx/aladdin-ai.ru-error.log 2>&1"
expect "password:" { send "$password\r" }
expect eof

set nginx_recent [string trim $expect_out(buffer)]
puts "$nginx_recent"
puts ""

# 5. Проверить последние логи Payment Service
puts "5️⃣ Проверяю ПОСЛЕДНИЕ логи Payment Service (последние 5 строк)..."
spawn ssh $server "tail -5 /tmp/payment_service.log 2>&1"
expect "password:" { send "$password\r" }
expect eof

set payment_recent [string trim $expect_out(buffer)]
puts "$payment_recent"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

