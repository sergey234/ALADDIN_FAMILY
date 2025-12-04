#!/usr/bin/expect -f

# Поиск путей к payment_service на сервере

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПОИСК ПУТЕЙ К PAYMENT_SERVICE НА СЕРВЕРЕ"
puts "=========================================="
puts ""

# 1. Проверить рабочую директорию процесса
puts "1️⃣ Проверяем рабочую директорию процесса 535117..."
spawn ssh $server "readlink /proc/535117/cwd 2>&1"
expect "password:" { send "$password\r" }
expect eof

set process_cwd [string trim $expect_out(buffer)]
puts "Результат (рабочая директория): $process_cwd"
puts ""

# 2. Найти main.py
puts "2️⃣ Ищем main.py..."
spawn ssh $server "find /opt/aladdin-backend -name 'main.py' -type f 2>&1 | head -3"
expect "password:" { send "$password\r" }
expect eof

set main_paths [string trim $expect_out(buffer)]
puts "Результат (main.py):"
puts "$main_paths"
puts ""

# 3. Найти директорию app/
puts "3️⃣ Ищем директорию app/..."
spawn ssh $server "find /opt/aladdin-backend -type d -name 'app' 2>&1 | head -3"
expect "password:" { send "$password\r" }
expect eof

set app_dirs [string trim $expect_out(buffer)]
puts "Результат (app/):"
puts "$app_dirs"
puts ""

# 4. Проверить структуру
puts "4️⃣ Проверяем структуру директории..."
spawn ssh $server "ls -la $process_cwd 2>&1 | head -15"
expect "password:" { send "$password\r" }
expect eof

set dir_structure [string trim $expect_out(buffer)]
puts "Результат (структура):"
puts "$dir_structure"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

