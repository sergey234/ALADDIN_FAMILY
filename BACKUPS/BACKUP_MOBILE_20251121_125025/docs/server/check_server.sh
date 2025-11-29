#!/usr/bin/expect -f
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== 🔍 ПОЛНАЯ ПРОВЕРКА СЕРВЕРА ==="
puts ""

# Выполнить все команды в одной SSH сессии
spawn ssh $server bash -c {
    echo "=== 1. Поиск проектов ==="
    find /opt /var/www /home -type d -name '*aladdin*' -o -name '*backend*' 2>/dev/null | head -10
    echo ""
    
    echo "=== 2. Поиск main.py ==="
    find /opt /var/www /home -name 'main.py' -type f 2>/dev/null | head -5
    echo ""
    
    echo "=== 3. Файлы в /opt/aladdin-backend ==="
    find /opt/aladdin-backend -type f 2>/dev/null | head -20
    echo ""
    
    echo "=== 4. Systemd сервисы ==="
    systemctl list-units --type=service --state=running | grep -iE 'aladdin|python|api|backend' || echo "Не найдено"
    echo ""
    
    echo "=== 5. Python процессы ==="
    ps aux | grep -E 'python|uvicorn|gunicorn|fastapi' | grep -v grep || echo "Не найдено"
    echo ""
    
    echo "=== 6. Сетевые порты ==="
    ss -tuln 2>/dev/null | grep -E '8000|8080|5000|5432' || echo "Не найдено"
    echo ""
    
    echo "=== 7. Упоминания БД в коде ==="
    grep -r 'DATABASE\|database\|postgres\|mysql\|sqlite' /opt/aladdin-backend --include='*.py' 2>/dev/null | head -10 || echo "Не найдено"
    echo ""
    
    echo "=== 8. Проверка PostgreSQL ==="
    ps aux | grep postgres | grep -v grep || echo "PostgreSQL не запущен локально"
    echo ""
    
    echo "=== 9. Конфигурационные файлы ==="
    find /opt/aladdin-backend -name '*.env' -o -name '*.conf' -o -name 'config.py' -o -name 'settings.py' 2>/dev/null | head -10
}

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}

