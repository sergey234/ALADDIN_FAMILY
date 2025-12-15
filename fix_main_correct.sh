#!/usr/bin/expect -f
# Правильное исправление

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ПРАВИЛЬНОЕ ИСПРАВЛЕНИЕ"
puts "========================"
puts ""

spawn scp fix_main_correctly.py "$server:/tmp/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

spawn ssh $server "python3 /tmp/fix_main_correctly.py"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅ Синтаксис правильный" {
        puts "   ✅ Исправлено!"
        exp_continue
    }
    eof {
    }
}

wait

puts ""
puts "🧪 Тест импорта..."
spawn ssh $server "cd /opt/aladdin-backend && /opt/aladdin-backend/venv/bin/python3 -c 'from main import app; print(\"✅✅✅ ИМПОРТ УСПЕШЕН!\")' 2>&1 | head -5"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅✅✅ ИМПОРТ УСПЕШЕН" {
        puts "   🎉🎉🎉 ВСЕ РАБОТАЕТ!"
        exp_continue
    }
    eof {
    }
}

wait

puts ""
puts "🔄 Перезапуск backend..."
spawn ssh $server "systemctl restart aladdin-backend && sleep 8 && systemctl status aladdin-backend --no-pager | head -15"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "Active: active" {
        puts "   ✅✅✅ BACKEND ЗАПУЩЕН!"
        exp_continue
    }
    eof {
    }
}

wait
