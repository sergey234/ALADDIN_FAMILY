#!/usr/bin/expect -f
# Проверка работы backend

set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА РАБОТЫ BACKEND"
puts "=========================="
puts ""

# Проверка через uvicorn напрямую (как systemd)
puts "📋 Тест импорта app через uvicorn..."
spawn ssh $server "cd /opt/aladdin-backend && /opt/aladdin-backend/venv/bin/python3 -c 'import sys; sys.path.insert(0, \".\"); from main import app; print(\"✅ App импортирован успешно\")' 2>&1 | head -30"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅ App импортирован" {
        puts "   ✅ Импорт работает!"
        exp_continue
    }
    "✅ Dark Web Monitoring Router зарегистрирован" {
        puts "   ✅ Router зарегистрирован!"
        exp_continue
    }
    eof {
    }
}

wait

puts ""
puts "📋 Проверка endpoints через uvicorn..."
spawn ssh $server "cd /opt/aladdin-backend && timeout 3 /opt/aladdin-backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8001 > /tmp/uvicorn_test.log 2>&1 & sleep 2 && curl -s http://127.0.0.1:8001/api/darkweb/health && pkill -f 'uvicorn.*8001'"

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
    }
}

wait

puts ""
puts "📋 Проверка логов systemd..."
spawn ssh $server "journalctl -u aladdin-backend -n 20 --no-pager | tail -10"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait
