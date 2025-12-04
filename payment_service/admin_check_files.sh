#!/usr/bin/expect -f

# Проверка загруженных файлов на сервере

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА ЗАГРУЖЕННЫХ ФАЙЛОВ"
puts "=========================================="
puts ""

# 1. Проверить main.py
puts "1️⃣ Проверяю main.py..."
spawn ssh $server "ls -lh /opt/aladdin-backend/main.py && grep -c 'admin_stats' /opt/aladdin-backend/main.py 2>&1"
expect "password:" { send "$password\r" }
expect eof

set main_check [string trim $expect_out(buffer)]
puts "Результат:"
puts "$main_check"
puts ""

# 2. Проверить admin_stats.py
puts "2️⃣ Проверяю admin_stats.py..."
spawn ssh $server "ls -lh /opt/aladdin-backend/app/admin_stats.py && head -5 /opt/aladdin-backend/app/admin_stats.py 2>&1"
expect "password:" { send "$password\r" }
expect eof

set admin_check [string trim $expect_out(buffer)]
puts "Результат:"
puts "$admin_check"
puts ""

# 3. Проверить что psutil установлен
puts "3️⃣ Проверяю что psutil установлен..."
spawn ssh $server "cd /opt/aladdin-backend && source venv/bin/activate && python3 -c 'import psutil; print(\"psutil version:\", psutil.__version__)' 2>&1"
expect "password:" { send "$password\r" }
expect eof

set psutil_check [string trim $expect_out(buffer)]
puts "Результат:"
puts "$psutil_check"
puts ""

# 4. Проверить синтаксис main.py
puts "4️⃣ Проверяю синтаксис main.py..."
spawn ssh $server "cd /opt/aladdin-backend && source venv/bin/activate && python3 -m py_compile main.py 2>&1 && echo 'SYNTAX_OK'"
expect "password:" { send "$password\r" }
expect eof

set syntax_check [string trim $expect_out(buffer)]
puts "Результат:"
puts "$syntax_check"
puts ""

# 5. Проверить синтаксис admin_stats.py
puts "5️⃣ Проверяю синтаксис admin_stats.py..."
spawn ssh $server "cd /opt/aladdin-backend && source venv/bin/activate && python3 -m py_compile app/admin_stats.py 2>&1 && echo 'SYNTAX_OK'"
expect "password:" { send "$password\r" }
expect eof

set admin_syntax [string trim $expect_out(buffer)]
puts "Результат:"
puts "$admin_syntax"
puts ""

# 6. Проверить импорты
puts "6️⃣ Проверяю импорты..."
spawn ssh $server "cd /opt/aladdin-backend && source venv/bin/activate && python3 -c 'from app.admin_stats import get_system_metrics, get_users_metrics, get_threats_metrics; print(\"✅ Импорты работают\")' 2>&1"
expect "password:" { send "$password\r" }
expect eof

set import_check [string trim $expect_out(buffer)]
puts "Результат:"
puts "$import_check"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

