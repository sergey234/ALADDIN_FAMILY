#!/usr/bin/expect -f
# Исправление uvicorn и проверка

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ИСПРАВЛЕНИЕ И ПРОВЕРКА"
puts "========================"
puts ""

# Исправить uvicorn import
puts "📋 Исправление import uvicorn..."
spawn ssh $server "sed -i 's/uvicorn\\.run(app, host=\"127.0.0.1\", port=8000)/import uvicorn\\n    uvicorn.run(app, host=\"127.0.0.1\", port=8000)/g' /opt/aladdin-backend/main.py || sed -i '/if __name__ == \"__main__\":/a\\    import uvicorn' /opt/aladdin-backend/main.py && echo '✅ Исправлено'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

# Проверка регистрации router
puts ""
puts "📋 Проверка зарегистрированных роутеров..."
spawn ssh $server "grep -n 'app.include_router' /opt/aladdin-backend/main.py"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

# Проверка через uvicorn
puts ""
puts "📋 Тест через uvicorn (как systemd)..."
spawn ssh $server "cd /opt/aladdin-backend && timeout 5 /opt/aladdin-backend/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8002 > /tmp/test.log 2>&1 & PID=\$!; sleep 3; curl -s http://127.0.0.1:8002/api/darkweb/health; kill \$PID 2>/dev/null; echo ''"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "healthy" {
        puts "   ✅✅✅ HEALTH CHECK РАБОТАЕТ!"
        exp_continue
    }
    eof {
    }
}

wait
