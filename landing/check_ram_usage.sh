#!/usr/bin/expect -f

# Проверка использования RAM на сервере

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА ИСПОЛЬЗОВАНИЯ RAM"
puts "=========================================="
puts ""

# 1. Общая информация о RAM
puts "1️⃣ Общая информация о RAM..."
spawn ssh $server "free -h"
expect "password:" { send "$password\r" }
expect eof

set ram_info [string trim $expect_out(buffer)]
puts "$ram_info"
puts ""

# 2. Топ процессов по использованию памяти
puts "2️⃣ Топ-10 процессов по использованию памяти..."
spawn ssh $server "ps aux --sort=-%mem | head -11"
expect "password:" { send "$password\r" }
expect eof

set top_processes [string trim $expect_out(buffer)]
puts "$top_processes"
puts ""

# 3. Детальная информация о payment_service
puts "3️⃣ Информация о payment_service..."
spawn ssh $server "ps aux | grep 'uvicorn.*main:app' | grep -v grep"
expect "password:" { send "$password\r" }
expect eof

set payment_service [string trim $expect_out(buffer)]
puts "$payment_service"
puts ""

# 4. Информация о Python процессах
puts "4️⃣ Все Python процессы..."
spawn ssh $server "ps aux | grep python | grep -v grep"
expect "password:" { send "$password\r" }
expect eof

set python_processes [string trim $expect_out(buffer)]
puts "$python_processes"
puts ""

# 5. Использование памяти по типам
puts "5️⃣ Использование памяти по типам..."
spawn ssh $server "cat /proc/meminfo | grep -E 'MemTotal|MemFree|MemAvailable|Buffers|Cached|SwapTotal|SwapFree'"
expect "password:" { send "$password\r" }
expect eof

set mem_details [string trim $expect_out(buffer)]
puts "$mem_details"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

