#!/usr/bin/expect -f
# Простое добавление AI Categories Router в main.py (БЕЗ восстановления backup)

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ДОБАВЛЕНИЕ AI CATEGORIES ROUTER В MAIN.PY"
puts ""

# Отправка исправленного скрипта
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
puts "🔧 Добавление AI Categories Router..."
spawn ssh $server "cd /tmp && python3 fix_main_py_syntax.py"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts ""
    }
wait

# Проверка синтаксиса
puts "📋 Проверка синтаксиса..."
spawn ssh $server "python3 -m py_compile /opt/aladdin-backend/main.py && echo '✅ Синтаксис корректен'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅ Синтаксис корректен" {
        puts "   ✅ Синтаксис корректен!"
        exp_continue
    }
    eof {
        puts ""
    }
}
wait

# Перезапуск сервиса
puts "🔄 Перезапуск сервиса..."
spawn ssh $server "systemctl restart aladdin-backend && sleep 2 && systemctl status aladdin-backend --no-pager | head -5"

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

# Проверка health check
puts "🔍 Проверка health check..."
sleep 3
spawn ssh $server "curl -s http://localhost:8000/api/ai-categories/health 2>/dev/null | python3 -m json.tool || echo '⚠️  Health check недоступен'"

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

puts "✅ ГОТОВО!"
