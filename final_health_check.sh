#!/usr/bin/expect -f
# Финальная проверка health endpoint
set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== ФИНАЛЬНАЯ ПРОВЕРКА HEALTH ENDPOINT ==="
puts ""

spawn ssh $server
expect {
    "password:" {
        send "$password\r"
        expect "# "
    }
}

send "curl -s http://localhost:8000/api/location/bubble/health | python3 -m json.tool\r"
expect "# "

send "echo ''\r"
expect "# "

# Проверка других endpoints
send "curl -s -X POST http://localhost:8000/api/location/bubble -H 'Content-Type: application/json' -d '{\"user_id\":\"test\",\"person_id\":\"test\",\"exact_latitude\":55.7558,\"exact_longitude\":37.6173,\"radius\":500}' | python3 -m json.tool | head -10\r"
expect "# "

# Проверка логов регистрации
send "journalctl -u aladdin-backend --since '2 minutes ago' --no-pager | grep 'Location Bubble' | tail -3\r"
expect "# "

puts ""
puts "✅ Проверка завершена!"
puts ""

send "exit\r"
expect eof
