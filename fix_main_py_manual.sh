#!/usr/bin/expect -f
# Ручное исправление main.py
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== РУЧНОЕ ИСПРАВЛЕНИЕ MAIN.PY ==="
puts ""

spawn ssh $server
expect {
    "password:" {
        send "$password\r"
        expect "# "
    }
}

# Восстановление из backup
send "cd /opt/aladdin-backend\r"
expect "# "
send "cp main.py.backup_20251213_160926 main.py\r"
expect "# "

# Показываем структуру вокруг router регистраций
puts "Поиск места для вставки router..."
send "grep -n 'app.include_router' main.py | tail -5\r"
expect "# "

# Показываем контекст последней регистрации
send "tail -20 main.py | head -15\r"
expect "# "

puts ""
puts "Теперь нужно вручную добавить:"
puts "1. Импорт: from security.api.routers.location_bubble_router import router as location_bubble_router"
puts "2. Регистрацию: app.include_router(location_bubble_router)"
puts ""
puts "После последнего app.include_router, но ВНЕ try/except блоков"
puts ""

send "exit\r"
expect eof
