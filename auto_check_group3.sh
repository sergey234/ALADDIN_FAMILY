#!/usr/bin/expect -f

# 🔍 АВТОМАТИЧЕСКАЯ ПРОВЕРКА МИГРАЦИИ ГРУППЫ 3
# Использует expect для автоматизации SSH

set SERVER "149.154.65.180"
set USER "root"
set PASSWORD "Sergio675"
set TIMEOUT 30

puts "🔍 АВТОМАТИЧЕСКАЯ ПРОВЕРКА МИГРАЦИИ ГРУППЫ 3"
puts "=========================================="
puts "Сервер: $SERVER"
puts ""

# Подключаемся к серверу
spawn ssh "$USER@$SERVER"
expect {
    "password:" {
        send "$PASSWORD\r"
        expect {
            "$ " {
                puts "✅ Подключение установлено"
            }
            "# " {
                puts "✅ Подключение установлено"
            }
        }
    }
    "yes/no" {
        send "yes\r"
        expect "password:" {
            send "$PASSWORD\r"
        }
    }
}

# 1. Проверка файла миграции
puts "\n📁 1. ПРОВЕРКА ФАЙЛА МИГРАЦИИ:"
send "ls -la /opt/aladdin-backend/migrate_group3.py\r"
expect {
    "No such file" {
        puts "❌ Файл migrate_group3.py отсутствует"
    }
    -re ".*migrate_group3.py.*" {
        puts "✅ Файл migrate_group3.py присутствует"
    }
}
expect "$ "
expect "# "

# 2. Проверка кода Группы 3
puts "\n🔍 2. ПРОВЕРКА КОДА ГРУППЫ 3:"
send "grep -n 'Группа 3' /opt/aladdin-backend/api_gateway.py | head -3\r"
expect {
    -re ".*Группа 3.*" {
        puts "✅ Код Группы 3 найден в api_gateway.py"
    }
    -re ".*No such file.*" {
        puts "❌ Файл api_gateway.py не найден"
    }
    default {
        puts "❌ Код Группы 3 НЕ найден"
    }
}
expect "$ "
expect "# "

# 3. Статус API Gateway
puts "\n🔧 3. СТАТУС API GATEWAY:"
send "systemctl status aladdin-api-gateway --no-pager | head -5\r"
expect {
    -re ".*active.*running.*" {
        puts "✅ API Gateway работает"
    }
    -re ".*inactive.*" {
        puts "❌ API Gateway не работает"
    }
    default {
        puts "⚠️ Статус не определен"
    }
}
expect "$ "
expect "# "

# 4. Health endpoint
puts "\n🏥 4. HEALTH ENDPOINT:"
send "curl -s http://127.0.0.1:8002/api/health\r"
expect {
    -re ".*status.*ok.*" {
        puts "✅ Health endpoint отвечает"
    }
    -re ".*Connection refused.*" {
        puts "❌ Health endpoint не отвечает"
    }
    default {
        puts "⚠️ Ответ получен"
    }
}
expect "$ "
expect "# "

# 5. Тестирование endpoints Группы 3
puts "\n🎯 5. ТЕСТИРОВАНИЕ ENDPOINTS ГРУППЫ 3:"

set endpoints {
    "/api/ai/categories/stats"
    "/api/data/cleanup/stats"
    "/api/location/stats"
    "/api/darkweb/stats"
    "/api/identity/stats"
}

foreach endpoint $endpoints {
    send "curl -s -w 'HTTP %{http_code}' http://127.0.0.1:8002$endpoint -o /dev/null\r"
    expect {
        -re ".*HTTP 200.*" {
            puts "✅ $endpoint: HTTP 200"
        }
        -re ".*HTTP [0-9]+.*" {
            puts "⚠️ $endpoint: ответ получен"
        }
        default {
            puts "❌ $endpoint: не отвечает"
        }
    }
    expect "$ "
    expect "# "
}

# 6. Подсчет endpoints
puts "\n📊 6. СТАТИСТИКА ENDPOINTS:"
send "grep -c 'app\\.' /opt/aladdin-backend/api_gateway.py\r"
expect {
    -re "([0-9]+)" {
        set total $expect_out(1,string)
        puts "Общее количество endpoints: $total"
    }
}
expect "$ "
expect "# "

# 7. Финальный вердикт
puts "\n📋 7. ФИНАЛЬНЫЙ РЕЗУЛЬТАТ:"
puts "=========================="

send "echo 'Проверка завершена'\r"
expect "$ "
expect "# "

puts "\n🎉 ПРОВЕРКА ЗАВЕРШЕНА!"
puts "======================"

send "exit\r"
expect eof


