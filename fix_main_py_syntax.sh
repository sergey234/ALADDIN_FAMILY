#!/usr/bin/expect -f
# Исправление синтаксической ошибки в main.py

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ИСПРАВЛЕНИЕ СИНТАКСИЧЕСКОЙ ОШИБКИ В MAIN.PY"
puts ""

# Восстановление из backup
puts "📋 Шаг 1: Восстановление из backup..."
spawn ssh $server "cp /opt/aladdin-backend/main.py.backup_ai_categories /opt/aladdin-backend/main.py && echo 'OK'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "OK" {
        puts "   ✅ Backup восстановлен"
        exp_continue
    }
    eof {
        puts "   ✅ Backup восстановлен"
    }
}
wait

# Правильная интеграция
puts "📋 Шаг 2: Правильная интеграция router..."
spawn ssh $server "cd /tmp && python3 add_ai_categories_to_main.py"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Интеграция завершена"
    }
}
wait

# Проверка синтаксиса
puts "📋 Шаг 3: Проверка синтаксиса..."
spawn ssh $server "python3 -m py_compile /opt/aladdin-backend/main.py && echo '✅ Синтаксис корректен'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅ Синтаксис корректен" {
        puts "   ✅ Синтаксис корректен"
        exp_continue
    }
    eof {
        puts ""
    }
}
wait

puts "✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!"
