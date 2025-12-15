#!/usr/bin/expect -f
# Проверка systemd service и Python окружения

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА BACKEND SERVICE"
puts "==========================="
puts ""

# Шаг 1: Проверить systemd service файл
puts "📋 Шаг 1: Проверка systemd service..."
spawn ssh $server "cat /etc/systemd/system/aladdin-backend.service"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

# Шаг 2: Проверить виртуальное окружение
puts ""
puts "📋 Шаг 2: Проверка виртуального окружения..."
spawn ssh $server "ls -la /opt/aladdin-backend/venv/bin/python* 2>/dev/null || ls -la /opt/aladdin-backend/venvs/*/bin/python* 2>/dev/null | head -3"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait

# Шаг 3: Проверить где установлен FastAPI
puts ""
puts "📋 Шаг 3: Проверка установки FastAPI..."
spawn ssh $server "/opt/aladdin-backend/venv/bin/python3 -c 'import fastapi; print(f\"FastAPI version: {fastapi.__version__}\")' 2>&1 || /opt/aladdin-backend/venvs/*/bin/python3 -c 'import fastapi; print(f\"FastAPI version: {fastapi.__version__}\")' 2>&1 | head -1"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait
