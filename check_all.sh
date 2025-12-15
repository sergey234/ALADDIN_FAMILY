#!/usr/bin/expect -f
# Полная проверка регистрации и backend

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПОЛНАЯ ПРОВЕРКА"
puts "=================="
puts ""

# Проверка registry
puts "📋 Проверка регистрации..."
spawn scp check_registry.py "$server:/tmp/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

spawn ssh $server "python3 /tmp/check_registry.py"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

# Проверка backend через venv
puts ""
puts "📋 Проверка импорта через venv..."
spawn ssh $server "cd /opt/aladdin-backend && /opt/aladdin-backend/venv/bin/python3 -c 'from main import app; print(\"✅ Импорт успешен\")' 2>&1"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

# Проверка systemd
puts ""
puts "📋 Статус systemd service..."
spawn ssh $server "systemctl status aladdin-backend --no-pager | head -20"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait
