#!/usr/bin/expect -f
set timeout 60
# SECURITY: Never store passwords in the repository.
# Prefer SSH keys. If password auth is absolutely required, pass it via env var:
#   export ALADDIN_SSH_PASSWORD='...'
if {![info exists env(ALADDIN_SSH_PASSWORD)]} {
    puts "❌ SECURITY: ALADDIN_SSH_PASSWORD не задана. Настройте SSH-ключи (рекомендуется) и повторите."
    exit 1
}
set password $env(ALADDIN_SSH_PASSWORD)
set server "root@149.154.65.180"

# Параметры БД
set db_name "aladdin_db"
set db_user "aladdin_user"
set db_password "AladdinSecure2024!"

puts "=== 🗄️  НАСТРОЙКА БАЗЫ ДАННЫХ ALADDIN ==="
puts ""

# 1. Создание базы данных
puts "📦 Шаг 1: Создание базы данных '$db_name'..."
spawn ssh $server "sudo -u postgres psql -c \"CREATE DATABASE $db_name;\""
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 2. Создание пользователя
puts ""
puts "👤 Шаг 2: Создание пользователя '$db_user'..."
spawn ssh $server "sudo -u postgres psql -c \"CREATE USER $db_user WITH PASSWORD '$db_password';\""
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 3. Выдача прав
puts ""
puts "🔐 Шаг 3: Выдача прав пользователю..."
spawn ssh $server "sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE $db_name TO $db_user;\""
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 4. Выдача прав на схему public
puts ""
puts "🔐 Шаг 4: Выдача прав на схему public..."
spawn ssh $server "sudo -u postgres psql -d $db_name -c \"GRANT ALL ON SCHEMA public TO $db_user;\""
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

# 5. Проверка подключения
puts ""
puts "✅ Шаг 5: Проверка подключения..."
spawn ssh $server "PGPASSWORD='$db_password' psql -h localhost -U $db_user -d $db_name -c \"SELECT version();\" | head -3"
expect {
    "password:" { send "$password\r"; exp_continue }
    eof
}

puts ""
puts "✅ База данных настроена!"
puts ""
puts "📝 Параметры подключения:"
puts "   Host: localhost"
puts "   Port: 5432"
puts "   Database: $db_name"
puts "   User: $db_user"
puts "   Password: $db_password"
puts ""
puts "🔗 Строка подключения:"
puts "   postgresql://$db_user:$db_password@localhost:5432/$db_name"


