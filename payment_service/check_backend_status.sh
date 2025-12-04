#!/usr/bin/expect -f

# Проверка текущего состояния payment_service на сервере

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ШАГ 1: ПРОВЕРКА ТЕКУЩЕГО СОСТОЯНИЯ BACKEND"
puts "=========================================="
puts ""

# 1. Найти директорию payment_service
puts "1️⃣ Ищем директорию payment_service..."
spawn ssh $server "find /opt /home /root -name 'main.py' -path '*/payment_service/*' -o -name 'main.py' -path '*/aladdin-backend/*' 2>/dev/null | head -1 | xargs dirname 2>/dev/null || echo 'NOT_FOUND'"
expect "password:" { send "$password\r" }
expect eof

set service_dir [string trim $expect_out(buffer)]
puts "Результат: $service_dir"
puts ""

# 2. Проверить по systemd service
puts "2️⃣ Проверяем systemd service..."
spawn ssh $server "systemctl status payment_service --no-pager 2>&1 | head -10 || echo 'SERVICE_NOT_FOUND'"
expect "password:" { send "$password\r" }
expect eof

set service_status [string trim $expect_out(buffer)]
puts "Результат:"
puts "$service_status"
puts ""

# 3. Проверить WorkingDirectory из service файла
puts "3️⃣ Проверяем WorkingDirectory из service файла..."
spawn ssh $server "grep -E 'WorkingDirectory|ExecStart' /etc/systemd/system/payment_service.service 2>/dev/null || echo 'SERVICE_FILE_NOT_FOUND'"
expect "password:" { send "$password\r" }
expect eof

set service_config [string trim $expect_out(buffer)]
puts "Результат:"
puts "$service_config"
puts ""

# 4. Если нашли директорию, проверить файлы
if {![string match "*NOT_FOUND*" $service_dir] && [string length $service_dir] > 5} {
    puts "4️⃣ Проверяем файлы в найденной директории..."
    spawn ssh $server "ls -la ${service_dir}/main.py ${service_dir}/app/dashboard_stats.py 2>&1"
    expect "password:" { send "$password\r" }
    expect eof
    
    set files_check [string trim $expect_out(buffer)]
    puts "Результат:"
    puts "$files_check"
    puts ""
    
    # 5. Проверить импорты dashboard_stats в main.py
    puts "5️⃣ Проверяем импорты dashboard_stats в main.py..."
    spawn ssh $server "grep -n 'dashboard_stats' ${service_dir}/main.py 2>/dev/null | head -5 || echo 'NO_IMPORTS'"
    expect "password:" { send "$password\r" }
    expect eof
    
    set imports_check [string trim $expect_out(buffer)]
    puts "Результат:"
    puts "$imports_check"
    puts ""
    
    # 6. Проверить endpoints dashboard в main.py
    puts "6️⃣ Проверяем endpoints dashboard в main.py..."
    spawn ssh $server "grep -n '/api/dashboard' ${service_dir}/main.py 2>&1 | head -5 || echo 'NO_ENDPOINTS'"
    expect "password:" { send "$password\r" }
    expect eof
    
    set endpoints_check [string trim $expect_out(buffer)]
    puts "Результат:"
    puts "$endpoints_check"
    puts ""
}

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

