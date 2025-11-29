#!/usr/bin/expect -f
# 🔍 Проверка конфигурации Nginx на сервере

set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 Проверяю конфигурацию Nginx на сервере..."
puts ""

# Проверяем конфигурацию Nginx для /api/
spawn ssh $server "cat /etc/nginx/sites-available/aladdin-ai.ru | grep -A 20 'location /api'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "Are you sure you want to continue connecting" {
        send "yes\r"
        exp_continue
    }
    eof {
        puts "\n✅ Конфигурация получена"
    }
    timeout {
        puts "\n❌ Таймаут"
        exit 1
    }
}

wait

puts "\n🔍 Проверяю, работает ли backend на порту 8000..."
spawn ssh $server "curl -v http://localhost:8000/api/payment-methods 2>&1 | head -20"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "\n✅ Проверка завершена"
    }
    timeout {
        puts "\n❌ Таймаут"
        exit 1
    }
}

wait


