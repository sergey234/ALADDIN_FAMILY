#!/usr/bin/expect -f
# Простое финальное исправление

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ"
puts "======================"
puts ""

spawn scp fix_main_simple_final.py "$server:/tmp/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

spawn ssh $server "python3 /tmp/fix_main_simple_final.py"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅ Синтаксис правильный" {
        puts "   🎉 ИСПРАВЛЕНО!"
        exp_continue
    }
    eof {
    }
}

wait

puts ""
puts "🧪 Тест..."
spawn ssh $server "cd /opt/aladdin-backend && /opt/aladdin-backend/venv/bin/python3 -c 'from main import app; print(\"✅✅✅ РАБОТАЕТ!\")' 2>&1 | head -3"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅✅✅ РАБОТАЕТ" {
        puts ""
        puts "🎉🎉🎉 ВСЕ РАБОТАЕТ!"
        exp_continue
    }
    eof {
    }
}

wait

puts ""
puts "🔄 Перезапуск..."
spawn ssh $server "systemctl restart aladdin-backend && sleep 8 && systemctl status aladdin-backend --no-pager | head -15"

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

puts ""
puts "🌐 Health check..."
spawn ssh $server "sleep 2 && curl -s http://localhost:8000/api/darkweb/health 2>&1"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "healthy" {
        puts "   ✅✅✅ ENDPOINT РАБОТАЕТ!"
        exp_continue
    }
    eof {
    }
}

wait
