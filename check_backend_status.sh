#!/usr/bin/expect -f
# Проверка текущего статуса backend

set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА ТЕКУЩЕГО СТАТУСА BACKEND"
puts "===================================="
puts ""

# Статус service
puts "📋 Статус systemd service..."
spawn ssh $server "systemctl status aladdin-backend --no-pager | head -20"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "Active: active" {
        puts "   ✅ Backend работает!"
        exp_continue
    }
    "Active: failed" {
        puts "   ❌ Backend упал"
        exp_continue
    }
    eof {
    }
}

wait

# Последние логи
puts ""
puts "📋 Последние логи (последние 30 строк)..."
spawn ssh $server "journalctl -u aladdin-backend -n 30 --no-pager"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

# Проверка health check
puts ""
puts "🌐 Проверка health check..."
spawn ssh $server "curl -s http://localhost:8000/api/darkweb/health 2>&1 || echo 'Backend не отвечает'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "healthy" {
        puts "   ✅ Health check работает!"
        exp_continue
    }
    eof {
    }
}

wait

# Проверка импорта
puts ""
puts "🧪 Проверка импорта app..."
spawn ssh $server "cd /opt/aladdin-backend && /opt/aladdin-backend/venv/bin/python3 -c 'from main import app; print(\"✅ Импорт работает\")' 2>&1 | head -5"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅ Импорт работает" {
        puts "   ✅ Импорт работает!"
        exp_continue
    }
    eof {
    }
}

wait
