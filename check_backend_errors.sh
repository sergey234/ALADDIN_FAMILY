#!/usr/bin/expect -f
# Проверка ошибок backend

set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА ОШИБОК BACKEND"
puts "==========================="
puts ""

spawn ssh $server "journalctl -u aladdin-backend -n 50 --no-pager | tail -30"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

puts ""
puts "📋 Попытка запуска вручную для проверки ошибок..."
spawn ssh $server "cd /opt/aladdin-backend && python3 -c 'import sys; sys.path.insert(0, \".\"); from main import app; print(\"✅ Импорт успешен\")' 2>&1"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait
