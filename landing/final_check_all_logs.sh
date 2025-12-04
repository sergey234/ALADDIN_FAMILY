#!/usr/bin/expect -f

# Финальная проверка всех логов

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"
set admin_key "ADMIN_SECRET_KEY_CHANGE_IN_PRODUCTION"

puts "🔍 ФИНАЛЬНАЯ ПРОВЕРКА ВСЕХ ЛОГОВ"
puts "=========================================="
puts ""

set services [list "payment_service" "nginx" "system" "security" "mysql" "postgresql" "auth"]

foreach service $services {
    puts "🔍 Проверяю: $service"
    spawn ssh $server "curl -s -H 'X-Admin-Key: $admin_key' 'http://localhost:8000/api/admin/logs?service=$service&limit=5' | python3 -c 'import sys, json; data=json.load(sys.stdin); service_name=data.get(\"service\", \"unknown\"); total=data.get(\"total\", 0); error=data.get(\"error\", None); note=data.get(\"note\", \"\"); print(f\"✅ {service_name}: Логов={total}\"); if error: print(f\"   ⚠️ {error}\"); if note and \"пуст\" in note.lower(): print(f\"   ℹ️ {note}\")' 2>&1"
    expect "password:" { send "$password\r" }
    expect eof
    
    set result [string trim $expect_out(buffer)]
    puts "$result"
    puts ""
}

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

