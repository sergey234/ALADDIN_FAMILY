#!/usr/bin/expect -f
# Полная проверка работы Location Bubble Agent
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== ПОЛНАЯ ПРОВЕРКА LOCATION BUBBLE AGENT ==="
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

# 1. Проверка health endpoint
puts "1. Health endpoint..."
send "curl -s http://localhost:8000/api/location/bubble/health | python3 -m json.tool\r"
expect "# "

# 2. Тест генерации пузыря
puts "2. Тест генерации пузыря..."
send "curl -s -X POST http://localhost:8000/api/location/bubble -H 'Content-Type: application/json' -d '{\"user_id\":\"test123\",\"person_id\":\"person456\",\"exact_latitude\":55.7558,\"exact_longitude\":37.6173,\"radius\":500}' | python3 -m json.tool\r"
expect "# "

# 3. Проверка настроек
puts "3. Тест настроек..."
send "curl -s -X POST http://localhost:8000/api/location/bubble/settings -H 'Content-Type: application/json' -d '{\"user_id\":\"test123\",\"person_id\":\"person456\",\"default_radius\":1000,\"enabled\":true}' | python3 -m json.tool\r"
expect "# "

# 4. Проверка получения настроек
puts "4. Получение настроек..."
send "curl -s 'http://localhost:8000/api/location/bubble/settings?user_id=test123&person_id=person456' | python3 -m json.tool\r"
expect "# "

# 5. Проверка истории
puts "5. История генераций..."
send "curl -s 'http://localhost:8000/api/location/bubble/history?user_id=test123&limit=5' | python3 -m json.tool\r"
expect "# "

# 6. Проверка логов регистрации
puts "6. Логи регистрации..."
send "journalctl -u aladdin-backend --since '5 minutes ago' --no-pager | grep -i 'location.*bubble\\|router.*registered' | tail -5\r"
expect "# "

puts ""
puts "✅ Все проверки завершены!"
puts ""

send "exit\r"
expect eof
