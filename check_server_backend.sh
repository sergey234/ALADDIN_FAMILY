#!/usr/bin/expect -f
# 🔍 Проверка: Где находится backend и где он должен быть запущен

set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"

puts "=========================================="
puts "🔍 ПРОВЕРКА: Backend на сервере"
puts "=========================================="
puts ""

# 1. Проверяем, есть ли backend код на сервере
puts "1️⃣ Проверяю наличие backend кода на сервере:"
spawn ssh $server "ls -la /opt/aladdin-backend/ 2>/dev/null && echo '---' && find /opt/aladdin-backend -name '*.py' -type f 2>/dev/null | head -5 || echo '❌ Backend код не найден'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {}
    timeout { exit 1 }
}
wait

# 2. Проверяем, запущен ли backend процесс
puts "\n2️⃣ Проверяю запущенные процессы backend:"
spawn ssh $server "ps aux | grep -E '(uvicorn|fastapi|main:app)' | grep -v grep || echo '❌ Backend процесс не найден'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {}
    timeout { exit 1 }
}
wait

# 3. Проверяем порт 8000
puts "\n3️⃣ Проверяю порт 8000:"
spawn ssh $server "netstat -tlnp 2>/dev/null | grep ':8000' || ss -tlnp 2>/dev/null | grep ':8000' || echo '❌ Порт 8000 не слушается'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {}
    timeout { exit 1 }
}
wait

# 4. Проверяем systemd сервис
puts "\n4️⃣ Проверяю systemd сервис:"
spawn ssh $server "systemctl status aladdin-backend 2>&1 | head -10 || echo '❌ Сервис aladdin-backend не найден'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {}
    timeout { exit 1 }
}
wait

# 5. Проверяем Nginx конфигурацию
puts "\n5️⃣ Проверяю Nginx конфигурацию для /api/:"
spawn ssh $server "grep -A 10 'location /api' /etc/nginx/sites-available/aladdin-ai.ru 2>/dev/null || echo '❌ location /api/ не настроен в Nginx'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {}
    timeout { exit 1 }
}
wait

puts "\n=========================================="
puts "✅ Проверка завершена"
puts "=========================================="
puts ""
puts "📋 РЕЗЮМЕ:"
puts "   - Backend код должен быть на СЕРВЕРЕ: /opt/aladdin-backend/"
puts "   - Backend должен быть ЗАПУЩЕН на СЕРВЕРЕ на порту 8000"
puts "   - Nginx на СЕРВЕРЕ должен проксировать /api/ на localhost:8000"
puts ""


