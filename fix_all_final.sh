#!/usr/bin/expect -f
# Финальное исправление всех проблем

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ ВСЕХ ПРОБЛЕМ"
puts "===================================="
puts ""

spawn scp fix_indentation_final.py "$server:/tmp/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

spawn ssh $server "python3 /tmp/fix_indentation_final.py"

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
spawn ssh $server "sleep 3 && curl -s http://localhost:8000/api/darkweb/health 2>&1"

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

puts ""
puts "✅✅✅ ВСЕ ГОТОВО!"
