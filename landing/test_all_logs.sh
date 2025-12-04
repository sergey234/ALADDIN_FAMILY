#!/usr/bin/expect -f

# Тестирование всех типов логов

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"
set admin_key "ADMIN_SECRET_KEY_CHANGE_IN_PRODUCTION"

puts "🧪 ТЕСТИРОВАНИЕ ВСЕХ ТИПОВ ЛОГОВ"
puts "=========================================="
puts ""

set services [list "payment_service" "nginx" "system" "security" "mysql" "postgresql" "auth"]

foreach service $services {
    puts "🔍 Тестирую: $service"
    spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' 'http://localhost:8000/api/admin/logs?service=$service&limit=5' | python3 -m json.tool 2>&1 | head -15"
    expect "password:" { send "$password\r" }
    expect eof
    
    set result [string trim $expect_out(buffer)]
    puts "$result"
    puts ""
}

puts "=========================================="
puts "✅ Тестирование завершено!"
puts ""

