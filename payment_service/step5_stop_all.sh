#!/usr/bin/expect -f

# ШАГ 5: Остановить все процессы на порту 8000

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🛑 ШАГ 5: Останавливаю все процессы на порту 8000..."
puts ""

spawn ssh $server "lsof -ti :8000 | xargs kill 2>&1; sleep 2; lsof -i :8000 2>&1 | grep -v COMMAND || echo 'PORT_FREE'"
expect "password:" { send "$password\r" }
expect eof

set result [string trim $expect_out(buffer)]
puts "Результат:"
puts "$result"
puts ""

if {[string match "*PORT_FREE*" $result]} {
    puts "✅ Порт 8000 свободен!"
} else {
    puts "⚠️ Порт еще занят, попробую еще раз..."
}
puts ""

