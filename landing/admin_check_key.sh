#!/usr/bin/expect -f

# Проверка админ-ключа на сервере

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔑 ПРОВЕРКА АДМИН-КЛЮЧА"
puts "=========================================="
puts ""

# 1. Проверить в .env файле
puts "1️⃣ Проверяю .env файл..."
spawn ssh $server "grep -i ADMIN_KEY /opt/aladdin-backend/.env 2>&1 || echo 'NOT_FOUND_IN_ENV'"
expect "password:" { send "$password\r" }
expect eof

set env_key [string trim $expect_out(buffer)]
puts "Результат (.env):"
puts "$env_key"
puts ""

# 2. Проверить в config.py (значение по умолчанию)
puts "2️⃣ Проверяю значение по умолчанию в config.py..."
spawn ssh $server "grep -A 1 'admin_key.*Field' /opt/aladdin-backend/app/config.py 2>&1 | head -2"
expect "password:" { send "$password\r" }
expect eof

set default_key [string trim $expect_out(buffer)]
puts "Результат (default):"
puts "$default_key"
puts ""

# 3. Проверить переменные окружения процесса
puts "3️⃣ Проверяю переменные окружения процесса..."
spawn ssh $server "ps aux | grep 'uvicorn.*main:app' | grep -v grep | head -1 | awk '{print \$2}' | xargs -I {} cat /proc/{}/environ 2>/dev/null | tr '\\0' '\\n' | grep -i ADMIN_KEY || echo 'NOT_FOUND_IN_PROCESS'"
expect "password:" { send "$password\r" }
expect eof

set process_key [string trim $expect_out(buffer)]
puts "Результат (process env):"
puts "$process_key"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

