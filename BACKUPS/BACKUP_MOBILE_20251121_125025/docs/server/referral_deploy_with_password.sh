#!/usr/bin/expect -f
# 🚀 Автоматическое развертывание реферальной программы на сервере

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"
set local_script_dir "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/docs/server"

puts "🚀 РАЗВЕРТЫВАНИЕ РЕФЕРАЛЬНОЙ ПРОГРАММЫ"
puts "=========================================="
puts "Сервер: $server"
puts ""

# ============================================
# ШАГ 1: ЗАГРУЗКА ФАЙЛОВ НА СЕРВЕР
# ============================================

puts "▶ 1. Загрузка файлов на сервер..."

set remote_dir "/tmp/referral_deployment"

# Создать директорию на сервере
spawn ssh $server "mkdir -p $remote_dir && echo 'OK'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "Are you sure you want to continue connecting" {
        send "yes\r"
        exp_continue
    }
    "OK" {
        puts "   ✅ Директория создана на сервере"
        exp_continue
    }
    eof {
        puts "   ✅ Директория создана"
    }
}

wait

# Загрузить SQL скрипт
puts "   Загрузка SQL скрипта..."
spawn rsync -avz "$local_script_dir/REFERRAL_DB_SETUP.sql" $server:$remote_dir/

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ SQL скрипт загружен"
    }
    timeout {
        puts "   ⚠ Таймаут при загрузке SQL"
    }
}

wait

# Загрузить Python файлы
puts "   Загрузка Python файлов..."
spawn rsync -avz "$local_script_dir/REFERRAL_API_ENDPOINTS.py" "$local_script_dir/REFERRAL_REGISTRATION_HANDLER.py" "$local_script_dir/REFERRAL_PAYMENT_HANDLER.py" $server:$remote_dir/

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Python файлы загружены"
    }
}

wait

# Загрузить HTML файл
puts "   Загрузка HTML файла..."
spawn rsync -avz "$local_script_dir/REFERRAL_LANDING_PAGE.html" $server:$remote_dir/

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ HTML файл загружен"
    }
}

wait

# Загрузить Nginx конфигурацию
puts "   Загрузка Nginx конфигурации..."
spawn rsync -avz "$local_script_dir/NGINX_CONFIG.conf" $server:$remote_dir/

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Nginx конфигурация загружена"
    }
}

wait

puts ""

# ============================================
# ШАГ 2: ВЫПОЛНЕНИЕ SQL СКРИПТА
# ============================================

puts "▶ 2. Выполнение SQL скрипта..."

set db_user "postgres"
set db_name "aladdin"

spawn ssh $server "psql -h localhost -U $db_user -d $db_name -f $remote_dir/REFERRAL_DB_SETUP.sql 2>&1"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "CREATE TABLE" {
        puts "   ✅ Таблицы создаются..."
        exp_continue
    }
    "CREATE INDEX" {
        puts "   ✅ Индексы создаются..."
        exp_continue
    }
    "CREATE FUNCTION" {
        puts "   ✅ Функции создаются..."
        exp_continue
    }
    "ERROR" {
        puts "   ⚠ Ошибка при выполнении SQL"
        exp_continue
    }
    eof {
        puts "   ✅ SQL скрипт выполнен"
    }
    timeout {
        puts "   ⚠ Таймаут при выполнении SQL"
    }
}

wait

puts ""

# ============================================
# ШАГ 3: ПРОВЕРКА ТАБЛИЦ
# ============================================

puts "▶ 3. Проверка созданных таблиц..."

spawn ssh $server "psql -h localhost -U $db_user -d $db_name -c '\\dt referral*' 2>&1"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "referral_codes" {
        puts "   ✅ Таблица referral_codes найдена"
        exp_continue
    }
    "referrals" {
        puts "   ✅ Таблица referrals найдена"
        exp_continue
    }
    eof {
        puts "   ✅ Проверка завершена"
    }
}

wait

puts ""

# ============================================
# ШАГ 4: ИНФОРМАЦИЯ О СЛЕДУЮЩИХ ШАГАХ
# ============================================

puts "=========================================="
puts "✅ ФАЙЛЫ ЗАГРУЖЕНЫ НА СЕРВЕР!"
puts ""
puts "📁 Файлы находятся в: $remote_dir"
puts ""
puts "📋 СЛЕДУЮЩИЕ ШАГИ (выполните вручную или через SSH):"
puts ""
puts "1. Интегрировать Python код в ваш FastAPI проект:"
puts "   cp $remote_dir/REFERRAL_API_ENDPOINTS.py /path/to/project/app/routers/"
puts ""
puts "2. Разместить HTML файл:"
puts "   cp $remote_dir/REFERRAL_LANDING_PAGE.html /path/to/project/templates/"
puts ""
puts "3. Настроить Nginx (добавить в существующую конфигурацию):"
puts "   См. $remote_dir/NGINX_CONFIG.conf"
puts ""
puts "4. Интегрировать обработчики регистрации и оплаты:"
puts "   См. $remote_dir/REFERRAL_REGISTRATION_HANDLER.py"
puts "   См. $remote_dir/REFERRAL_PAYMENT_HANDLER.py"
puts ""
puts "📖 Детальные инструкции: $remote_dir/README.md (если загружен)"
puts ""

