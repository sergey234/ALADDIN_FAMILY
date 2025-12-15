#!/usr/bin/expect -f
# Исправление main.py

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ИСПРАВЛЕНИЕ MAIN.PY"
puts "======================"
puts ""

spawn scp fix_main_py_indentation.py "$server:/tmp/"

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

spawn ssh $server "python3 /tmp/fix_main_py_indentation.py"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅ Синтаксис правильный" {
        puts "   ✅ Исправлено и проверено!"
        exp_continue
    }
    eof {
    }
}

wait

puts ""
puts "Попытка запуска..."
spawn ssh $server "cd /opt/aladdin-backend && python3 -m py_compile main.py 2>&1 && echo '✅ Компиляция успешна'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait
