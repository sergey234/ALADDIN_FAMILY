#!/usr/bin/expect -f
# Проверка и исправление
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== ПРОВЕРКА И ИСПРАВЛЕНИЕ ==="
puts ""

spawn ssh $server
expect {
    "password:" {
        send "$password\r"
        expect "# "
    }
}

send "cd /opt/aladdin-backend\r"
expect "# "

# Проверка импорта
puts "1. Проверка импорта router..."
send "grep 'location_bubble_router' main.py | head -2\r"
expect "# "

# Проверка регистрации
puts "2. Проверка регистрации router..."
send "grep 'app.include_router(location_bubble_router)' main.py\r"
expect "# "

# Проверка логов
puts "3. Проверка логов сервиса..."
send "journalctl -u aladdin-backend -n 30 | grep -i 'location_bubble\\|error\\|exception' | tail -10\r"
expect "# "

# Проверка что файл router существует
puts "4. Проверка файла router..."
send "ls -la /opt/aladdin-backend/security/api/routers/location_bubble_router.py\r"
expect "# "

# Попытка импорта
puts "5. Проверка импорта Python..."
send "cd /opt/aladdin-backend && source venv/bin/activate && python3 -c 'from security.api.routers.location_bubble_router import router; print(\"✅ Импорт успешен\")' 2>&1\r"
expect "# "

# Проверка всех зарегистрированных routers
puts "6. Проверка всех routers..."
send "grep 'app.include_router' main.py | tail -5\r"
expect "# "

puts ""
puts "Проверка завершена"
puts ""

send "exit\r"
expect eof
