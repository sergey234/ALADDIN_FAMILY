#!/usr/bin/expect -f

# ШАГ 3: Установить psutil

set timeout 180
set password "Sergio675"
set server "root@149.154.65.180"

puts "📦 ШАГ 3: Устанавливаю psutil на сервере..."
puts ""

spawn ssh $server "cd /opt/aladdin-backend && source venv/bin/activate && pip install psutil==5.9.6 2>&1"
expect "password:" { send "$password\r" }
expect eof

set result [string trim $expect_out(buffer)]
puts "Результат:"
puts "$result"
puts ""

if {[string match "*Successfully installed*" $result] || [string match "*already satisfied*" $result]} {
    puts "✅ psutil установлен!"
} else {
    puts "⚠️ Проверьте результат установки"
}
puts ""

