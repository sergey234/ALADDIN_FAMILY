#!/usr/bin/expect -f
# Детальная проверка логов

set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ДЕТАЛЬНАЯ ПРОВЕРКА ПРОБЛЕМЫ"
puts "=============================="
puts ""

# Попробовать запустить uvicorn напрямую и увидеть ошибку
puts "📋 Тестовый запуск uvicorn (посмотрим ошибку)..."
spawn ssh $server "cd /opt/aladdin-backend && timeout 5 /opt/aladdin-backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8003 2>&1 | head -50"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

# Проверить что именно происходит при импорте
puts ""
puts "📋 Проверка ошибок при импорте..."
spawn ssh $server "cd /opt/aladdin-backend && /opt/aladdin-backend/venv/bin/python3 -c 'import sys; sys.stderr = sys.stdout; from main import app; print(\"✅ OK\")' 2>&1"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

# Проверить процессы
puts ""
puts "📋 Проверка процессов Python..."
spawn ssh $server "ps aux | grep -E '(uvicorn|python.*main)' | grep -v grep"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait
