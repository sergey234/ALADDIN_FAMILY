#!/usr/bin/expect -f

# Тестирование кнопок обновления логов

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"
set admin_key "ADMIN_SECRET_KEY_CHANGE_IN_PRODUCTION"

puts "🧪 ТЕСТИРОВАНИЕ КНОПОК ОБНОВЛЕНИЯ ЛОГОВ"
puts "=========================================="
puts ""

set services [list "payment_service" "nginx" "system" "security" "mysql" "postgresql" "auth"]

foreach service $services {
    puts "🔍 Тестирую: $service"
    spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' 'http://localhost:8000/api/admin/logs?service=$service&limit=3' | python3 -c 'import sys, json; data=json.load(sys.stdin); print(\"✅ Работает:\", data.get(\"service\", \"unknown\"), \"- Логов:\", data.get(\"total\", 0))' 2>&1"
    expect "password:" { send "$password\r" }
    expect eof
    
    set result [string trim $expect_out(buffer)]
    puts "$result"
    puts ""
}

puts "=========================================="
puts "✅ Тестирование завершено!"
puts ""
puts "💡 Проверьте в браузере:"
puts "   1. Кнопка '🔄 Обновить' должна работать для всех типов логов"
puts "   2. Кнопка '⏸️ Автообновление' должна работать для всех типов логов"
puts "   3. При переключении между типами логов автообновление должно продолжать работать"
puts ""

