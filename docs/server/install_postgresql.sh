#!/usr/bin/expect -f
set timeout 120
# SECURITY: Never store passwords in the repository.
# Prefer SSH keys. If password auth is absolutely required, pass it via env var:
#   export ALADDIN_SSH_PASSWORD='...'
if {![info exists env(ALADDIN_SSH_PASSWORD)]} {
    puts "❌ SECURITY: ALADDIN_SSH_PASSWORD не задана. Настройте SSH-ключи (рекомендуется) и повторите."
    exit 1
}
set password $env(ALADDIN_SSH_PASSWORD)
set server "root@149.154.65.180"

puts "=== 🚀 УСТАНОВКА POSTGRESQL НА 149.154.65.180 ==="
puts ""

# 1. Обновление пакетов
puts "📦 Шаг 1: Обновление списка пакетов..."
spawn ssh $server "apt update"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 2. Установка PostgreSQL сервера
puts ""
puts "📦 Шаг 2: Установка PostgreSQL сервера..."
spawn ssh $server "DEBIAN_FRONTEND=noninteractive apt install -y postgresql postgresql-contrib"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 3. Запуск службы
puts ""
puts "▶️  Шаг 3: Запуск PostgreSQL..."
spawn ssh $server "systemctl start postgresql && systemctl enable postgresql"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 4. Проверка статуса
puts ""
puts "✅ Шаг 4: Проверка статуса..."
spawn ssh $server "systemctl status postgresql | head -10"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 5. Проверка версии
puts ""
puts "📊 Шаг 5: Проверка версии PostgreSQL..."
spawn ssh $server "sudo -u postgres psql --version"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

puts ""
puts "✅ PostgreSQL установлен и запущен!"
puts ""
puts "📝 Следующие шаги:"
puts "   1. Создать базу данных для ALADDIN"
puts "   2. Создать пользователя БД"
puts "   3. Выполнить SQL скрипт для реферальной программы"


