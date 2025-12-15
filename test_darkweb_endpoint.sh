#!/usr/bin/expect -f
# Тест нашего endpoint

set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"

puts "🧪 ТЕСТ ENDPOINT DARK WEB"
puts "========================"
puts ""

# Проверка health check
puts "📋 Проверка /api/darkweb/health..."
spawn ssh $server "curl -s http://localhost:8000/api/darkweb/health 2>&1"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "healthy" {
        puts "   ✅ Health check работает!"
        exp_continue
    }
    "Not Found" {
        puts "   ⚠️  Endpoint не найден (может быть старый backend без нашего router)"
        exp_continue
    }
    eof {
    }
}

wait

# Проверка что это за backend
puts ""
puts "📋 Проверка какой backend работает..."
spawn ssh $server "curl -s http://localhost:8000/ 2>&1"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

# Информация о процессе
puts ""
puts "📋 Информация о работающем процессе..."
spawn ssh $server "ps aux | grep 1494117 | grep -v grep"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait
