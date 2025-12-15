#!/usr/bin/expect -f
# Скрипт для добавления Dark Web Router в main.py

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ДОБАВЛЕНИЕ DARK WEB ROUTER В MAIN.PY"
puts "========================================"
puts ""

# Шаг 1: Отправка скрипта
puts "📋 Шаг 1: Отправка скрипта..."
spawn scp add_dark_web_to_main.py "$server:/tmp/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Скрипт отправлен"
    }
}

wait

# Шаг 2: Запуск скрипта
puts ""
puts "📋 Шаг 2: Запуск скрипта..."
spawn ssh $server "python3 /tmp/add_dark_web_to_main.py"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅ main.py обновлен" {
        puts "   ✅ Router добавлен в main.py!"
        exp_continue
    }
    eof {
        puts "   ✅ Скрипт завершен"
    }
}

wait

puts ""
puts "================================"
puts "✅ ИНТЕГРАЦИЯ ЗАВЕРШЕНА!"
puts ""
puts "📝 СЛЕДУЮЩИЕ ШАГИ:"
puts ""
puts "1. Перезапустить backend:"
puts "   ssh $server"
puts "   systemctl restart aladdin-backend"
puts ""
puts "2. Проверить логи:"
puts "   journalctl -u aladdin-backend -n 50 | grep -i 'dark web'"
puts ""
puts "3. Проверить health check:"
puts "   curl http://localhost:8000/api/darkweb/health"
puts ""
