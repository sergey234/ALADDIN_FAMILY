#!/usr/bin/expect -f
# Проверка регистрации router
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== ПРОВЕРКА РЕГИСТРАЦИИ ROUTER ==="
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

# Проверка структуры регистрации
puts "1. Проверка регистрации router..."
send "grep -A 4 'Location Bubble Router' main.py\r"
expect "# "

# Проверка что router в try/except
send "sed -n '905,915p' main.py\r"
expect "# "

# Проверка импорта агента
puts "2. Проверка импорта агента..."
send "cd /opt/aladdin-backend && source venv/bin/activate && python3 -c 'from security.ai_agents.location_bubble_agent import LocationBubbleAgent; print(\"✅ Агент импортируется\")' 2>&1\r"
expect "# "

# Проверка импорта router
puts "3. Проверка импорта router..."
send "python3 -c 'from security.api.routers.location_bubble_router import router; print(\"✅ Router импортируется\")' 2>&1\r"
expect "# "

# Проверка логов на ошибки
puts "4. Проверка логов..."
send "journalctl -u aladdin-backend -n 50 --no-pager | tail -20\r"
expect "# "

# Проверка всех зарегистрированных routers
puts "5. Все routers..."
send "grep 'app.include_router' main.py | tail -5\r"
expect "# "

puts ""
puts "Проверка завершена"
puts ""

send "exit\r"
expect eof
