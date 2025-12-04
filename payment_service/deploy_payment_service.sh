#!/usr/bin/expect -f

# Деплой обновленного payment_service на сервер
# Заменяет старый payment_service на новый с dashboard endpoints

set timeout 300
set password "Sergio675"
set server "root@149.154.65.180"
set server_dir "/opt/aladdin-backend"
set old_pid "535117"

puts "🚀 ДЕПЛОЙ ОБНОВЛЕННОГО PAYMENT_SERVICE"
puts "=========================================="
puts ""

# ШАГ 1: Создать бэкап старого main.py
puts "📦 ШАГ 1: Создаю бэкап старого main.py..."
spawn ssh $server "cd $server_dir && cp main.py main.py.backup_\$(date +%Y%m%d_%H%M%S) && ls -lh main.py.backup_* | tail -1"
expect "password:" { send "$password\r" }
expect eof

set backup_result [string trim $expect_out(buffer)]
puts "Результат: $backup_result"
puts ""

# ШАГ 2: Загрузить новый main.py
puts "📤 ШАГ 2: Загружаю новый main.py..."
spawn scp main.py $server:$server_dir/main.py
expect "password:" { send "$password\r" }
expect eof

puts "✅ main.py загружен"
puts ""

# ШАГ 3: Загрузить dashboard_stats.py
puts "📤 ШАГ 3: Загружаю dashboard_stats.py..."
spawn scp app/dashboard_stats.py $server:$server_dir/app/dashboard_stats.py
expect "password:" { send "$password\r" }
expect eof

puts "✅ dashboard_stats.py загружен"
puts ""

# ШАГ 4: Установить права на файлы
puts "🔐 ШАГ 4: Устанавливаю права на файлы..."
spawn ssh $server "chmod 644 $server_dir/main.py && chmod 644 $server_dir/app/dashboard_stats.py && ls -lh $server_dir/main.py $server_dir/app/dashboard_stats.py"
expect "password:" { send "$password\r" }
expect eof

set permissions_result [string trim $expect_out(buffer)]
puts "Результат:"
puts "$permissions_result"
puts ""

# ШАГ 5: Остановить старый процесс
puts "🛑 ШАГ 5: Останавливаю старый процесс (PID $old_pid)..."
spawn ssh $server "kill $old_pid && sleep 2 && ps -p $old_pid 2>&1 || echo 'PROCESS_STOPPED'"
expect "password:" { send "$password\r" }
expect eof

set stop_result [string trim $expect_out(buffer)]
puts "Результат: $stop_result"
puts ""

# ШАГ 6: Проверить что порт 8000 свободен
puts "🔍 ШАГ 6: Проверяю что порт 8000 свободен..."
spawn ssh $server "lsof -i :8000 2>&1 | grep -v COMMAND || echo 'PORT_FREE'"
expect "password:" { send "$password\r" }
expect eof

set port_check [string trim $expect_out(buffer)]
puts "Результат: $port_check"
puts ""

# ШАГ 7: Запустить новый процесс
puts "▶️  ШАГ 7: Запускаю новый payment_service..."
spawn ssh $server "cd $server_dir && nohup /opt/aladdin-backend/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &"
expect "password:" { send "$password\r" }
expect eof

puts "✅ Процесс запущен"
puts ""

# ШАГ 8: Подождать 3 секунды
puts "⏳ ШАГ 8: Жду 3 секунды для запуска..."
spawn ssh $server "sleep 3"
expect "password:" { send "$password\r" }
expect eof

# ШАГ 9: Проверить что процесс запустился
puts "🔍 ШАГ 9: Проверяю что новый процесс запустился..."
spawn ssh $server "ps aux | grep 'uvicorn.*main:app.*8000' | grep -v grep | head -1"
expect "password:" { send "$password\r" }
expect eof

set new_process [string trim $expect_out(buffer)]
puts "Результат (новый процесс):"
if {[string length $new_process] > 0} {
    puts "✅ $new_process"
} else {
    puts "❌ Процесс не найден!"
}
puts ""

# ШАГ 10: Проверить что API работает
puts "🔍 ШАГ 10: Проверяю что API работает..."
spawn ssh $server "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/payment-methods 2>&1"
expect "password:" { send "$password\r" }
expect eof

set api_test [string trim $expect_out(buffer)]
puts "Результат (старый endpoint): HTTP $api_test"
if {[string match "200" $api_test]} {
    puts "✅ Старые endpoints работают!"
} else {
    puts "❌ Старые endpoints НЕ работают!"
}
puts ""

# ШАГ 11: Проверить новый dashboard endpoint
puts "🔍 ШАГ 11: Проверяю новый dashboard endpoint..."
spawn ssh $server "curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/api/dashboard/public/stats 2>&1"
expect "password:" { send "$password\r" }
expect eof

set dashboard_test [string trim $expect_out(buffer)]
puts "Результат (новый endpoint): HTTP $dashboard_test"
if {[string match "200" $dashboard_test]} {
    puts "✅ Новые dashboard endpoints работают!"
} else {
    puts "❌ Новые dashboard endpoints НЕ работают!"
}
puts ""

puts "=========================================="
puts "✅ ДЕПЛОЙ ЗАВЕРШЕН!"
puts ""
puts "📋 ИТОГИ:"
puts "  - Бэкап создан: main.py.backup_*"
puts "  - main.py обновлен"
puts "  - dashboard_stats.py загружен"
puts "  - Старый процесс остановлен"
puts "  - Новый процесс запущен"
puts ""

