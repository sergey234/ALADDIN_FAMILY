#!/usr/bin/expect -f
# Финальное исправление отступов

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ ОТСТУПОВ"
puts "================================"
puts ""

# Удалить все uvicorn.run вне блока if __name__
puts "📋 Очистка лишних uvicorn.run..."
spawn ssh $server "sed -i '898d' /opt/aladdin-backend/main.py && echo '✅ Удалена строка 898'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

# Проверка
puts ""
puts "🧪 Проверка синтаксиса..."
spawn ssh $server "cd /opt/aladdin-backend && /opt/aladdin-backend/venv/bin/python3 -m py_compile main.py && echo '✅ Синтаксис правильный!'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅ Синтаксис правильный" {
        puts "   🎉 ИСПРАВЛЕНО!"
        exp_continue
    }
    eof {
    }
}

wait

puts ""
puts "🧪 Тест импорта..."
spawn ssh $server "cd /opt/aladdin-backend && /opt/aladdin-backend/venv/bin/python3 -c 'from main import app; print(\"✅✅✅ РАБОТАЕТ!\")' 2>&1 | head -3"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅✅✅ РАБОТАЕТ" {
        puts ""
        puts "🎉🎉🎉 ВСЕ РАБОТАЕТ!"
        exp_continue
    }
    eof {
    }
}

wait

puts ""
puts "🔄 Перезапуск backend..."
spawn ssh $server "systemctl restart aladdin-backend && sleep 8 && systemctl status aladdin-backend --no-pager | head -15"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "Active: active" {
        puts "   ✅✅✅ BACKEND РАБОТАЕТ!"
        exp_continue
    }
    eof {
    }
}

wait

puts ""
puts "🌐 Проверка health check..."
spawn ssh $server "sleep 3 && curl -s http://localhost:8000/api/darkweb/health 2>&1"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "healthy" {
        puts "   ✅✅✅ ENDPOINT РАБОТАЕТ!"
        exp_continue
    }
    eof {
    }
}

wait
