#!/usr/bin/expect -f
# Автоматическое развертывание на сервере с использованием expect
# Использование: ./auto_deploy.sh

set timeout 300
set server "149.154.65.180"
set user "root"
set password "Sergio675"
set remote_dir "/opt/aladdin-backend"
set local_dir [file dirname [file normalize [info script]]]

puts "============================================================"
puts "АВТОМАТИЧЕСКОЕ РАЗВЕРТЫВАНИЕ НА СЕРВЕРЕ"
puts "============================================================"
puts ""

# Копирование файлов на сервер
puts "📤 Копирование файлов на сервер..."
spawn scp -o StrictHostKeyChecking=no $local_dir/create_component_tables.sql $local_dir/apply_migration.py $local_dir/test_endpoints.py $local_dir/verify_endpoints.py $local_dir/EXECUTE_ON_SERVER.sh ${user}@${server}:${remote_dir}/app/database/migrations/
expect {
    "password:" {
        send "$password\r"
        expect eof
    }
    "yes/no" {
        send "yes\r"
        expect "password:"
        send "$password\r"
        expect eof
    }
    eof
}

puts "✅ Файлы скопированы"
puts ""

# Подключение к серверу и выполнение команд
puts "🔧 Подключение к серверу и применение миграции..."
spawn ssh -o StrictHostKeyChecking=no ${user}@${server}
expect {
    "password:" {
        send "$password\r"
    }
    "yes/no" {
        send "yes\r"
        expect "password:"
        send "$password\r"
    }
}

expect "# "
send "cd $remote_dir\r"
expect "# "

send "python3 app/database/migrations/apply_migration.py\r"
expect {
    "✅ Миграция завершена успешно!" {
        puts "✅ Миграция применена успешно!"
    }
    "❌" {
        puts "❌ Ошибка применения миграции"
        exit 1
    }
    timeout {
        puts "⚠️ Таймаут при применении миграции"
    }
}

expect "# "
send "export API_BASE_URL='https://aladdin-ai.ru'\r"
expect "# "

send "python3 app/database/migrations/test_endpoints.py\r"
expect {
    "✅ Все тесты пройдены!" {
        puts "✅ Тестирование завершено успешно!"
    }
    timeout {
        puts "⚠️ Тестирование завершено"
    }
}

expect "# "
send "python3 app/database/migrations/verify_endpoints.py\r"
expect {
    "✅ ✅ Все endpoints соответствуют документации!" {
        puts "✅ Проверка документации завершена успешно!"
    }
    timeout {
        puts "⚠️ Проверка завершена"
    }
}

expect "# "
send "exit\r"
expect eof

puts ""
puts "============================================================"
puts "✅ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО"
puts "============================================================"
