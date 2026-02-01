#!/usr/bin/expect -f

# Автоматизированное развертывание Группы 3 с вводом пароля
set SERVER "149.154.65.180"
set USER "root"
set PASSWORD "Sergio675"
set LOCAL_SCRIPT "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/migrate_group3.py"
set REMOTE_PATH "/opt/aladdin-backend/"

puts "🚀 АВТОМАТИЗИРОВАННОЕ РАЗВЕРТЫВАНИЕ ГРУППЫ 3"
puts "==============================================="

# Загружаем скрипт на сервер
puts "📤 Загружаем скрипт на сервер..."
spawn scp "$LOCAL_SCRIPT" "$USER@$SERVER:$REMOTE_PATH"
expect {
    "password:" {
        send "$PASSWORD\r"
        expect eof
    }
    eof {
        puts "✅ Скрипт загружен успешно"
    }
}

# Выполняем миграцию на сервере
puts "🔧 Выполняем миграцию на сервере..."
spawn ssh "$USER@$SERVER"
expect {
    "password:" {
        send "$PASSWORD\r"
        expect {
            "$ " {
                send "cd /opt/aladdin-backend\r"
                expect "$ "
                send "echo '📍 Текущая директория: '\$(pwd)\r"
                expect "$ "
                send "echo '📄 Проверяем наличие скрипта...'\r"
                expect "$ "
                send "ls -la migrate_group3.py\r"
                expect "$ "
                send "echo ''\r"
                expect "$ "
                send "echo '🚀 Запускаем миграцию...'\r"
                expect "$ "
                send "python3 migrate_group3.py --apply\r"
                expect "$ "
                send "echo ''\r"
                expect "$ "
                send "echo '✅ МИГРАЦИЯ ГРУППЫ 3 ЗАВЕРШЕНА!'\r"
                expect "$ "
                send "exit\r"
            }
        }
    }
}

puts ""
puts "🎉 АВТОМАТИЗИРОВАННОЕ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО!"
puts "==============================================="


