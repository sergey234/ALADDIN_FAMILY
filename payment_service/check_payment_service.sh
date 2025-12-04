#!/usr/bin/expect -f

# Проверка systemd service для payment_service

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА PAYMENT_SERVICE НА СЕРВЕРЕ"
puts "=========================================="
puts ""

# 1. Проверить есть ли systemd service
puts "1️⃣ Проверяем systemd service..."
spawn ssh $server "systemctl list-units --type=service | grep -i payment 2>&1"
expect "password:" { send "$password\r" }
expect eof

set service_list [string trim $expect_out(buffer)]
puts "Результат (systemd services):"
if {[string length $service_list] > 0} {
    puts "$service_list"
} else {
    puts "❌ Payment service не найден в systemd"
}
puts ""

# 2. Проверить статус payment_service
puts "2️⃣ Проверяем статус payment_service..."
spawn ssh $server "systemctl status payment_service 2>&1 || systemctl status payment-service 2>&1 || echo 'SERVICE_NOT_FOUND'"
expect "password:" { send "$password\r" }
expect eof

set service_status [string trim $expect_out(buffer)]
puts "Результат (статус service):"
puts "$service_status"
puts ""

# 3. Проверить где находится payment_service
puts "3️⃣ Проверяем где находится payment_service..."
spawn ssh $server "ls -la /opt/aladdin-backend/venv/bin/uvicorn 2>&1 && echo '---' && ls -la /opt/aladdin-backend/venv/main.py 2>&1 || ls -la /opt/aladdin-backend/venv/*/main.py 2>&1 || find /opt/aladdin-backend -name 'main.py' -type f 2>&1 | head -5"
expect "password:" { send "$password\r" }
expect eof

set service_path [string trim $expect_out(buffer)]
puts "Результат (путь к service):"
puts "$service_path"
puts ""

# 4. Проверить рабочую директорию процесса
puts "4️⃣ Проверяем рабочую директорию процесса 535117..."
spawn ssh $server "pwdx 535117 2>&1 || ls -la /proc/535117/cwd 2>&1"
expect "password:" { send "$password\r" }
expect eof

set process_cwd [string trim $expect_out(buffer)]
puts "Результат (рабочая директория):"
puts "$process_cwd"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

