#!/usr/bin/expect -f
# Проверка текущего состояния main.py

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА СОСТОЯНИЯ MAIN.PY"
puts ""

# Проверка синтаксиса
puts "📋 Проверка синтаксиса..."
spawn ssh $server "python3 -m py_compile /opt/aladdin-backend/main.py 2>&1 || echo 'ERROR'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "ERROR" {
        puts "   ❌ Есть синтаксическая ошибка"
        exp_continue
    }
    eof {
        puts "   ✅ Синтаксис корректен"
    }
}
wait

# Проверка наличия ai_categories_router
puts "📋 Проверка ai_categories_router..."
spawn ssh $server "grep -n 'ai_categories_router' /opt/aladdin-backend/main.py | head -5"

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

# Проверка контекста вокруг проблемной строки
puts "📋 Проверка контекста (строки 880-900)..."
spawn ssh $server "sed -n '880,900p' /opt/aladdin-backend/main.py"

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

puts "✅ ПРОВЕРКА ЗАВЕРШЕНА"
