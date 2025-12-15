#!/usr/bin/expect -f
# Проверка конфликта портов

set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА ПРОБЛЕМЫ С ПОРТОМ"
puts "============================="
puts ""

# Проверка что занимает порт 8000
puts "📋 Что использует порт 8000..."
spawn ssh $server "netstat -tlnp | grep :8000 || ss -tlnp | grep :8000"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

# Проверка процесса который занимает порт
puts ""
puts "📋 Детали процесса на порту 8000..."
spawn ssh $server "lsof -i :8000 2>/dev/null || echo 'lsof не доступен'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

# Проверка systemd - почему он не может запустить
puts ""
puts "📋 Последняя ошибка systemd (stderr)..."
spawn ssh $server "systemctl status aladdin-backend --no-pager -l | tail -20"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

# Проверка - может backend уже работает?
puts ""
puts "🌐 Проверка доступности порта 8000..."
spawn ssh $server "curl -s http://localhost:8000/ 2>&1 | head -10"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait
