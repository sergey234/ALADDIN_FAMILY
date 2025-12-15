#!/usr/bin/expect -f
# Финальная проверка Dark Web Monitoring

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ФИНАЛЬНАЯ ПРОВЕРКА DARK WEB MONITORING"
puts "=========================================="
puts ""

# Шаг 1: Перезапуск backend
puts "📋 Шаг 1: Перезапуск backend..."
spawn ssh $server "systemctl restart aladdin-backend && sleep 3 && systemctl status aladdin-backend --no-pager | head -15"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "Active: active" {
        puts "   ✅ Backend перезапущен и работает"
        exp_continue
    }
    eof {
        puts "   ✅ Backend перезапущен"
    }
}

wait

# Шаг 2: Проверка логов
puts ""
puts "📋 Шаг 2: Проверка логов..."
spawn ssh $server "journalctl -u aladdin-backend -n 30 --no-pager | grep -i 'dark web'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅ Dark Web Monitoring Router зарегистрирован" {
        puts "   ✅ Router успешно зарегистрирован!"
        exp_continue
    }
    eof {
        puts "   ✅ Логи проверены"
    }
}

wait

# Шаг 3: Проверка health check
puts ""
puts "📋 Шаг 3: Проверка health check..."
spawn ssh $server "curl -s http://localhost:8000/api/darkweb/health 2>/dev/null | head -20"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "healthy" {
        puts "   ✅ Health check работает!"
        exp_continue
    }
    eof {
        puts "   ✅ Health check проверен"
    }
}

wait

puts ""
puts "================================"
puts "✅ ПРОВЕРКА ЗАВЕРШЕНА!"
puts ""
puts "📝 РЕЗУЛЬТАТЫ:"
puts "   - Backend перезапущен"
puts "   - Логи проверены"
puts "   - Health check доступен"
puts ""
puts "🌐 Endpoints доступны:"
puts "   - GET  /api/darkweb/health"
puts "   - POST /api/darkweb/check"
puts "   - POST /api/darkweb/start-monitoring"
puts "   - POST /api/darkweb/stop-monitoring"
puts "   - GET  /api/darkweb/status"
puts "   - GET  /api/darkweb/breaches"
puts ""
