#!/usr/bin/expect -f
# Финальное исправление logger

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ LOGGER"
puts "=============================="
puts ""

# Скачать main.py для проверки
puts "📋 Скачивание main.py для анализа..."
spawn ssh $server "grep -n 'logger' /opt/aladdin-backend/main.py | head -5"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

puts ""
puts "📋 Исправление: замена logger на print в блоке dark_web..."
spawn ssh $server "sed -i 's/logger\\.info(\"✅ Dark Web Monitoring Router зарегистрирован\")/print(\"✅ Dark Web Monitoring Router зарегистрирован\")/g' /opt/aladdin-backend/main.py && sed -i 's/logger\\.warning(f\"⚠️ Не удалось зарегистрировать Dark Web Monitoring Router: {e}\")/print(f\"⚠️ Не удалось зарегистрировать Dark Web Monitoring Router: {e}\")/g' /opt/aladdin-backend/main.py && echo '✅ Заменено на print'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

puts ""
puts "🧪 Проверка импорта..."
spawn ssh $server "cd /opt/aladdin-backend && /opt/aladdin-backend/venv/bin/python3 -c 'from main import app; print(\"✅✅✅ ИМПОРТ УСПЕШЕН!\")' 2>&1"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅✅✅ ИМПОРТ УСПЕШЕН" {
        puts ""
        puts "🎉🎉🎉 ВСЕ РАБОТАЕТ!"
        exp_continue
    }
    eof {
    }
}

wait

puts ""
puts "🔄 Перезапуск backend..."
spawn ssh $server "systemctl restart aladdin-backend && sleep 5 && systemctl status aladdin-backend --no-pager | head -15"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "Active: active" {
        puts "   ✅✅✅ BACKEND РАБОТАЕТ!"
        exp_continue
    }
    eof {
    }
}

wait
