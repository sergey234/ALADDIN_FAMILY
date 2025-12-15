#!/usr/bin/expect -f
# Исправление импортов

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ИСПРАВЛЕНИЕ ИМПОРТОВ"
puts "======================"
puts ""

spawn scp fix_main_py_imports.py "$server:/tmp/"

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

spawn ssh $server "python3 /tmp/fix_main_py_imports.py"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅ Синтаксис правильный" {
        puts "   ✅ Исправлено!"
        exp_continue
    }
    eof {
    }
}

wait

# Проверка импорта
puts ""
puts "Проверка импорта..."
spawn ssh $server "cd /opt/aladdin-backend && /opt/aladdin-backend/venv/bin/python3 -c 'from main import app; print(\"✅ Импорт успешен\")' 2>&1"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅ Импорт успешен" {
        puts "   ✅ Все работает!"
        exp_continue
    }
    eof {
    }
}

wait
