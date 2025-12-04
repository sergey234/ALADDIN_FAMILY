#!/usr/bin/expect -f

# Проверка что занимает порт 8000 на сервере

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА ПОРТА 8000 НА СЕРВЕРЕ"
puts "=========================================="
puts ""

# 1. Проверить что слушает порт 8000 (lsof)
puts "1️⃣ Проверяем что слушает порт 8000 (lsof)..."
spawn ssh $server "lsof -i :8000 2>&1"
expect "password:" { send "$password\r" }
expect eof

set lsof_result [string trim $expect_out(buffer)]
puts "Результат lsof:"
puts "$lsof_result"
puts ""

# 2. Проверить через netstat
puts "2️⃣ Проверяем через netstat..."
spawn ssh $server "netstat -tulpn | grep :8000 2>&1"
expect "password:" { send "$password\r" }
expect eof

set netstat_result [string trim $expect_out(buffer)]
puts "Результат netstat:"
if {[string length $netstat_result] > 0} {
    puts "$netstat_result"
} else {
    puts "❌ Порт 8000 не найден в netstat"
}
puts ""

# 3. Проверить через ss
puts "3️⃣ Проверяем через ss..."
spawn ssh $server "ss -tulpn | grep :8000 2>&1"
expect "password:" { send "$password\r" }
expect eof

set ss_result [string trim $expect_out(buffer)]
puts "Результат ss:"
if {[string length $ss_result] > 0} {
    puts "$ss_result"
} else {
    puts "❌ Порт 8000 не найден в ss"
}
puts ""

# 4. Проверить все процессы python/uvicorn
puts "4️⃣ Проверяем все процессы python/uvicorn..."
spawn ssh $server "ps aux | grep -E 'python|uvicorn' | grep -v grep 2>&1"
expect "password:" { send "$password\r" }
expect eof

set python_procs [string trim $expect_out(buffer)]
puts "Результат (процессы python/uvicorn):"
if {[string length $python_procs] > 0} {
    puts "$python_procs"
} else {
    puts "❌ Процессы python/uvicorn не найдены"
}
puts ""

# 5. Проверить доступность API на порту 8000
puts "5️⃣ Проверяем доступность API на порту 8000..."
spawn ssh $server "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/payment-methods 2>&1 || echo 'ERROR'"
expect "password:" { send "$password\r" }
expect eof

set api_test [string trim $expect_out(buffer)]
puts "Результат (HTTP код): $api_test"
puts ""

# 6. Проверить что отвечает на порту 8000
puts "6️⃣ Проверяем что отвечает на порту 8000..."
spawn ssh $server "curl -s http://localhost:8000/docs 2>&1 | head -10 || curl -s http://localhost:8000/ 2>&1 | head -10 || echo 'NO_RESPONSE'"
expect "password:" { send "$password\r" }
expect eof

set port_response [string trim $expect_out(buffer)]
puts "Результат (ответ сервера):"
puts "$port_response"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""
