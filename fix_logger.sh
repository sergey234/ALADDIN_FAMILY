#!/usr/bin/expect -f
# Исправление logger

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ИСПРАВЛЕНИЕ LOGGER"
puts "===================="
puts ""

spawn scp fix_logger_properly.py "$server:/tmp/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

spawn ssh $server "python3 /tmp/fix_logger_properly.py"

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

# Финальная проверка
puts ""
puts "Финальная проверка..."
spawn ssh $server "cd /opt/aladdin-backend && /opt/aladdin-backend/venv/bin/python3 -c 'from main import app; print(\"✅✅✅ ИМПОРТ УСПЕШЕН!\")' 2>&1"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅✅✅ ИМПОРТ УСПЕШЕН" {
        puts ""
        puts "🎉🎉🎉 ВСЕ РАБОТАЕТ!"
        exp_continue
    }
    eof {
    }
}

wait
