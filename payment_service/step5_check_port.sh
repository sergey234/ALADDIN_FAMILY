#!/usr/bin/expect -f

# ШАГ 5: Проверить что порт 8000 свободен

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ШАГ 5: Проверяю что порт 8000 свободен..."
puts ""

spawn ssh $server "lsof -i :8000 2>&1 | grep -v COMMAND || echo 'PORT_FREE'"
expect "password:" { send "$password\r" }
expect eof

set result [string trim $expect_out(buffer)]
puts "Результат:"
puts "$result"
puts ""

if {[string match "*PORT_FREE*" $result]} {
    puts "✅ Порт 8000 свободен!"
} else {
    puts "⚠️ Порт 8000 еще занят, но это нормально если процесс только что остановился"
}
puts ""

