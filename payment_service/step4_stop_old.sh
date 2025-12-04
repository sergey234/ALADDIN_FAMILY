#!/usr/bin/expect -f

# ШАГ 4: Остановить старый процесс

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🛑 ШАГ 4: Останавливаю старый процесс (PID 535117)..."
puts ""

spawn ssh $server "kill 535117 && sleep 2 && ps -p 535117 2>&1 || echo 'PROCESS_STOPPED'"
expect "password:" { send "$password\r" }
expect eof

set result [string trim $expect_out(buffer)]
puts "Результат: $result"
puts ""

if {[string match "*PROCESS_STOPPED*" $result]} {
    puts "✅ Старый процесс остановлен!"
} else {
    puts "⚠️ Проверяю статус процесса..."
}
puts ""

