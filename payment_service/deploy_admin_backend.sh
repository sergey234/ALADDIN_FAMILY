#!/usr/bin/expect -f

# Деплой обновлений для админского dashboard

set timeout 300
set password "Sergio675"
set server "root@149.154.65.180"

puts "🚀 ДЕПЛОЙ ОБНОВЛЕНИЙ ДЛЯ АДМИНСКОГО DASHBOARD"
puts "=========================================="
puts ""

# ШАГ 1: Создать бэкап
puts "📦 ШАГ 1: Создаю бэкап..."
spawn ssh $server "cd /opt/aladdin-backend && cp main.py main.py.backup_admin_\$(date +%Y%m%d_%H%M%S) && echo 'BACKUP_CREATED'"
expect "password:" { send "$password\r" }
expect eof

set backup_result [string trim $expect_out(buffer)]
puts "Результат: $backup_result"
puts ""

# ШАГ 2: Загрузить обновленный main.py
puts "📤 ШАГ 2: Загружаю обновленный main.py..."
spawn scp main.py $server:/opt/aladdin-backend/main.py
expect "password:" { send "$password\r" }
expect eof

puts "✅ main.py загружен"
puts ""

# ШАГ 3: Загрузить admin_stats.py
puts "📤 ШАГ 3: Загружаю admin_stats.py..."
spawn scp app/admin_stats.py $server:/opt/aladdin-backend/app/admin_stats.py
expect "password:" { send "$password\r" }
expect eof

puts "✅ admin_stats.py загружен"
puts ""

# ШАГ 4: Загрузить requirements.txt
puts "📤 ШАГ 4: Загружаю requirements.txt..."
spawn scp requirements.txt $server:/opt/aladdin-backend/requirements.txt
expect "password:" { send "$password\r" }
expect eof

puts "✅ requirements.txt загружен"
puts ""

# ШАГ 5: Установить psutil
puts "📦 ШАГ 5: Устанавливаю psutil на сервере..."
spawn ssh $server "cd /opt/aladdin-backend && source venv/bin/activate && pip install psutil==5.9.6 2>&1 | tail -5"
expect "password:" { send "$password\r" }
expect eof

set psutil_result [string trim $expect_out(buffer)]
puts "Результат:"
puts "$psutil_result"
puts ""

# ШАГ 6: Остановить старый процесс
puts "🛑 ШАГ 6: Останавливаю старый payment_service..."
spawn ssh $server "lsof -ti :8000 | xargs kill 2>&1; sleep 2; lsof -i :8000 2>&1 | grep -v COMMAND || echo 'PORT_FREE'"
expect "password:" { send "$password\r" }
expect eof

set stop_result [string trim $expect_out(buffer)]
puts "Результат: $stop_result"
puts ""

# ШАГ 7: Запустить новый процесс
puts "▶️  ШАГ 7: Запускаю обновленный payment_service..."
spawn ssh $server "cd /opt/aladdin-backend && nohup /opt/aladdin-backend/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &"
expect "password:" { send "$password\r" }
expect eof

puts "✅ Процесс запущен"
puts ""

# ШАГ 8: Ждем 3 секунды
puts "⏳ ШАГ 8: Жду 3 секунды..."
spawn ssh $server "sleep 3"
expect "password:" { send "$password\r" }
expect eof

# ШАГ 9: Проверить что процесс запустился
puts "🔍 ШАГ 9: Проверяю что процесс запустился..."
spawn ssh $server "ps aux | grep 'uvicorn.*main:app.*8000' | grep -v grep | head -1"
expect "password:" { send "$password\r" }
expect eof

set process_info [string trim $expect_out(buffer)]
puts "Результат:"
if {[string length $process_info] > 0} {
    puts "✅ $process_info"
} else {
    puts "❌ Процесс не найден!"
}
puts ""

# ШАГ 10: Проверить старые endpoints
puts "🔍 ШАГ 10: Проверяю старые endpoints..."
spawn ssh $server "curl -s -o /dev/null -w 'HTTP %{http_code}' http://localhost:8000/api/payment-methods 2>&1"
expect "password:" { send "$password\r" }
expect eof

set old_endpoint [string trim $expect_out(buffer)]
puts "Результат: $old_endpoint"
puts ""

# ШАГ 11: Проверить новые admin endpoints
puts "🔍 ШАГ 11: Проверяю новые admin endpoints..."
spawn ssh $server "curl -s -o /dev/null -w 'system: %{http_code}, ' -H 'X-Admin-Key: test' http://localhost:8000/api/admin/metrics/system 2>&1"
expect "password:" { send "$password\r" }
expect eof

set admin_endpoint [string trim $expect_out(buffer)]
puts "Результат: $admin_endpoint"
puts ""

puts "=========================================="
puts "✅ ДЕПЛОЙ ЗАВЕРШЕН!"
puts ""

