#!/usr/bin/expect -f
# Детальная проверка ошибок

set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ДЕТАЛЬНАЯ ПРОВЕРКА ОШИБОК"
puts "============================"
puts ""

puts "📋 Проверка логов backend..."
spawn ssh $server "journalctl -u aladdin-backend -n 100 --no-pager 2>&1 | grep -A 10 -B 10 -i 'error\\|exception\\|traceback\\|failed'"

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
puts "📋 Попытка импорта вручную..."
spawn ssh $server "cd /opt/aladdin-backend && python3 -c 'from main import app' 2>&1"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait
