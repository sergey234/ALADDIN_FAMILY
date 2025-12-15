#!/usr/bin/expect -f
# Тестирование запуска backend

set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"

puts "🧪 ТЕСТИРОВАНИЕ BACKEND"
puts "======================"
puts ""

spawn ssh $server "cd /opt/aladdin-backend && /opt/aladdin-backend/venv/bin/python3 -c 'from main import app; print(\"✅ Импорт успешен - backend готов к запуску\")' 2>&1"

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

puts ""
puts "Перезапуск backend..."
spawn ssh $server "systemctl restart aladdin-backend && sleep 5 && systemctl status aladdin-backend --no-pager | head -15"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "Active: active" {
        puts "   ✅ Backend запущен!"
        exp_continue
    }
    eof {
    }
}

wait
