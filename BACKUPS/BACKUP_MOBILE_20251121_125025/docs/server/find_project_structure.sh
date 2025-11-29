#!/usr/bin/expect -f
set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== 🔍 ПОИСК СТРУКТУРЫ ПРОЕКТА И ПАРАМЕТРОВ БД ==="
puts ""

# 1. Найти все Python проекты
spawn ssh $server "find /opt /var/www /home -type d -name '*aladdin*' -o -name '*backend*' 2>/dev/null | head -10"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 2. Найти main.py
spawn ssh $server "find /opt /var/www /home -name 'main.py' -type f 2>/dev/null | head -5"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 3. Найти все файлы в /opt/aladdin-backend
spawn ssh $server "find /opt/aladdin-backend -type f 2>/dev/null | head -20"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 4. Проверить systemd сервисы
spawn ssh $server "systemctl list-units --type=service --state=running | grep -iE 'aladdin|python|api|backend'"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 5. Найти процессы Python
spawn ssh $server "ps aux | grep -E 'python|uvicorn|gunicorn|fastapi' | grep -v grep"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 6. Проверить сетевые порты
spawn ssh $server "ss -tuln | grep -E '8000|8080|5000|5432'"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 7. Найти упоминания БД в коде
spawn ssh $server "grep -r 'DATABASE\|database\|postgres\|mysql\|sqlite' /opt/aladdin-backend --include='*.py' 2>/dev/null | head -10"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

puts "\n=== ✅ ПОИСК ЗАВЕРШЕН ==="

