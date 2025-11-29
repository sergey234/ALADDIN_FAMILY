#!/usr/bin/expect -f
# 🔍 Поиск backend на сервере

set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 Ищу backend на сервере..."
puts ""

# 1. Проверяем запущенные процессы Python
puts "1️⃣ Проверяю процессы Python:"
spawn ssh $server "ps aux | grep -E '(python|uvicorn|gunicorn|fastapi)' | grep -v grep"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {}
    timeout { exit 1 }
}
wait

# 2. Проверяем открытые порты
puts "\n2️⃣ Проверяю открытые порты:"
spawn ssh $server "netstat -tlnp 2>/dev/null | grep -E ':(8000|8001|8080|5000|3000)' || ss -tlnp 2>/dev/null | grep -E ':(8000|8001|8080|5000|3000)'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {}
    timeout { exit 1 }
}
wait

# 3. Проверяем systemd сервисы
puts "\n3️⃣ Проверяю systemd сервисы:"
spawn ssh $server "systemctl list-units --type=service --state=running | grep -E '(payment|backend|api|aladdin|python)'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {}
    timeout { exit 1 }
}
wait

# 4. Проверяем конфигурацию Nginx для /api/
puts "\n4️⃣ Проверяю конфигурацию Nginx:"
spawn ssh $server "cat /etc/nginx/sites-available/aladdin-ai.ru"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {}
    timeout { exit 1 }
}
wait

# 5. Проверяем директорию backend
puts "\n5️⃣ Проверяю директорию /opt/aladdin-backend:"
spawn ssh $server "ls -la /opt/aladdin-backend/ 2>/dev/null || echo 'Директория не существует'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {}
    timeout { exit 1 }
}
wait

puts "\n✅ Проверка завершена"


