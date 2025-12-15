#!/usr/bin/expect -f
# Финальный тест

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "🧪 ФИНАЛЬНЫЙ ТЕСТ"
puts "================"
puts ""

# Проверка логов теста
puts "📋 Логи тестового запуска..."
spawn ssh $server "cat /tmp/test.log 2>/dev/null | tail -20"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

# Перезапуск и проверка
puts ""
puts "🔄 Перезапуск backend..."
spawn ssh $server "systemctl restart aladdin-backend && sleep 8 && systemctl status aladdin-backend --no-pager | head -20"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "Active: active" {
        puts "   ✅✅✅ BACKEND ЗАПУЩЕН!"
        exp_continue
    }
    eof {
    }
}

wait

puts ""
puts "🌐 Проверка health check..."
spawn ssh $server "sleep 2 && curl -s http://localhost:8000/api/darkweb/health 2>&1"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "healthy" {
        puts "   ✅✅✅ HEALTH CHECK РАБОТАЕТ!"
        exp_continue
    }
    eof {
    }
}

wait
