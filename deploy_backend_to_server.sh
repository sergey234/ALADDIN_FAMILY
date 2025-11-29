#!/usr/bin/expect -f
# 🚀 Полный деплой backend на сервер

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"
set local_path "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/payment_service/"
set remote_path "/opt/aladdin-backend"

puts "=========================================="
puts "🚀 ДЕПЛОЙ BACKEND НА СЕРВЕР"
puts "=========================================="
puts ""
puts "📦 Локальный путь: $local_path"
puts "🌐 Сервер: $server"
puts "📁 Путь на сервере: $remote_path"
puts ""

# ШАГ 1: Загрузка файлов
puts "📦 ШАГ 1: Загружаю backend код на сервер..."
spawn rsync -avz --progress --exclude '.venv' --exclude '__pycache__' --exclude '*.pyc' --exclude 'payments.db' $local_path $server:$remote_path/

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "Are you sure you want to continue connecting" {
        send "yes\r"
        exp_continue
    }
    eof {
        puts "\n✅ Файлы загружены!"
    }
    timeout {
        puts "\n❌ Таймаут при загрузке"
        exit 1
    }
}
wait

# ШАГ 2: Установка зависимостей
puts "\n📦 ШАГ 2: Устанавливаю зависимости на сервере..."
spawn ssh $server "cd $remote_path && python3 -m venv .venv && source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && echo '✅ Зависимости установлены'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "\n✅ Зависимости установлены!"
    }
    timeout {
        puts "\n❌ Таймаут при установке"
        exit 1
    }
}
wait

# ШАГ 3: Проверка .env файла
puts "\n🔧 ШАГ 3: Проверяю .env файл..."
spawn ssh $server "cd $remote_path && if [ ! -f .env ]; then echo '⚠️ .env файл не найден, создаю из .env.example...' && cp .env.example .env 2>/dev/null || echo 'PAYMENT_API_KEY_PUBLIC=PUBLIC_CLIENT_KEY' > .env; fi && echo '✅ .env файл готов'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {}
    timeout { exit 1 }
}
wait

puts "\n=========================================="
puts "✅ ДЕПЛОЙ ЗАВЕРШЕН!"
puts "=========================================="
puts ""
puts "📋 СЛЕДУЮЩИЕ ШАГИ (выполните вручную на сервере):"
puts ""
puts "1️⃣ Подключитесь к серверу:"
puts "   ssh root@149.154.65.180"
puts ""
puts "2️⃣ Настройте .env файл:"
puts "   cd /opt/aladdin-backend"
puts "   nano .env"
puts "   # Добавьте PAYMENT_CARD_NUMBER и другие настройки"
puts ""
puts "3️⃣ Протестируйте запуск backend:"
puts "   cd /opt/aladdin-backend"
puts "   source .venv/bin/activate"
puts "   uvicorn main:app --host 127.0.0.1 --port 8000"
puts ""
puts "4️⃣ Создайте systemd сервис (см. docs/BACKEND_SETUP_COMPLETE.md)"
puts ""
puts "5️⃣ Настройте Nginx для /api/ (см. docs/BACKEND_SETUP_COMPLETE.md)"
puts ""


