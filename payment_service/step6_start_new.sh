#!/usr/bin/expect -f

# ШАГ 6: Запустить новый payment_service

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "▶️  ШАГ 6: Запускаю новый payment_service..."
puts ""

spawn ssh $server "cd /opt/aladdin-backend && nohup /opt/aladdin-backend/venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &"
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ Процесс запущен!"
puts ""

# Ждем 3 секунды
puts "⏳ Жду 3 секунды для запуска..."
spawn ssh $server "sleep 3"
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ Ожидание завершено!"
puts ""

