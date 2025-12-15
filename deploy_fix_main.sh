#!/usr/bin/expect -f
# Отправка и выполнение скрипта исправления main.py

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ИСПРАВЛЕНИЕ MAIN.PY"
puts ""

# Отправка скрипта
puts "📤 Отправка fix_main_py_syntax.py..."
spawn scp fix_main_py_syntax.py $server:/tmp/

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Скрипт отправлен"
    }
}
wait

# Выполнение скрипта
puts "🔧 Выполнение исправления..."
spawn ssh $server "cd /tmp && python3 fix_main_py_syntax.py"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts ""
    }
}
wait

puts "✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!"
