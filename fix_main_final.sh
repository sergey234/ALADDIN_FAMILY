#!/usr/bin/expect -f
# Финальное исправление main.py

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ"
puts "======================="
puts ""

# Сначала проверим структуру
puts "📋 Проверка структуры..."
spawn scp check_main_structure.py "$server:/tmp/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

spawn ssh $server "python3 /tmp/check_main_structure.py"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

# Исправление
puts ""
puts "📋 Исправление..."
spawn scp fix_main_properly.py "$server:/tmp/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

spawn ssh $server "python3 /tmp/fix_main_properly.py"

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

# Проверка
puts ""
puts "Проверка импорта..."
spawn ssh $server "cd /opt/aladdin-backend && /opt/aladdin-backend/venv/bin/python3 -c 'from main import app; print(\"✅ Импорт успешен\")' 2>&1"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait
