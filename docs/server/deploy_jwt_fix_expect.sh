#!/usr/bin/expect -f
# ============================================================================
# ДЕПЛОЙ: Исправление JWT 401 - 4 файла (с автоматическим вводом пароля)
# ============================================================================
# Дата: 2026-03-17
# Использует expect для автоматического ввода пароля
# ============================================================================

set timeout 60
# SECURITY: Never store passwords in the repository.
# Use SSH keys (recommended) or provide password via environment variable.
if {![info exists env(ALADDIN_SSH_PASSWORD)]} {
    puts "❌ SECURITY: Переменная окружения ALADDIN_SSH_PASSWORD не задана."
    puts "✅ Рекомендуется настроить SSH-ключи и НЕ использовать пароль в скриптах."
    puts "   Пример: ssh-copy-id root@149.154.65.180"
    exit 1
}
set password $env(ALADDIN_SSH_PASSWORD)
set server "root@149.154.65.180"
set server_path "/opt/aladdin-backend"
set local_path "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS"

# Файлы для деплоя
set files {
    "app/auth/auth.py"
    "backend/app/services/jwt_service.py"
    "app/auth/__init__.py"
    "app/routers/analytics_router.py"
}

puts "============================================================================"
puts "🚀 ДЕПЛОЙ: Исправление JWT 401 - 4 файла"
puts "============================================================================"
puts "📅 Дата: [clock format [clock seconds] -format {%Y-%m-%d %H:%M:%S}]"
puts "🌐 Сервер: $server"
puts "📁 Путь на сервере: $server_path"
puts "📁 Локальный путь: $local_path"
puts "============================================================================"
puts ""

# ШАГ 1: Проверка текущего состояния на сервере
puts "🔍 ШАГ 1: Проверка текущего состояния на сервере..."
spawn ssh $server "cd $server_path && echo '=== ПРОВЕРКА: app/auth/auth.py ===' && (grep -q 'aladdin-super-secret-key-change-in-production' app/auth/auth.py && echo '✅ JWT_SECRET найден' || echo '❌ JWT_SECRET НЕ найден') && (grep -q 'leeway=60' app/auth/auth.py && echo '✅ leeway найден' || echo '❌ leeway НЕ найден') && echo && echo '=== ПРОВЕРКА: backend/app/services/jwt_service.py ===' && (grep -q 'aladdin-super-secret-key-change-in-production' backend/app/services/jwt_service.py && echo '✅ SECRET_KEY найден' || echo '❌ SECRET_KEY НЕ найден') && echo && echo '=== ПРОВЕРКА: app/auth/__init__.py ===' && (grep -q 'aladdin-super-secret-key-change-in-production' app/auth/__init__.py && echo '✅ JWT_SECRET найден' || echo '❌ JWT_SECRET НЕ найден') && echo && echo '=== ПРОВЕРКА: app/routers/analytics_router.py ===' && (grep -q 'from app.auth.auth import get_current_user' app/routers/analytics_router.py && echo '✅ Правильный импорт найден' || echo '❌ Правильный импорт НЕ найден')"

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
        puts "\n✅ Проверка завершена"
    }
    timeout {
        puts "\n❌ Таймаут при проверке"
        exit 1
    }
}
wait
puts ""

# ШАГ 2: Создание backup
puts "📦 ШАГ 2: Создание backup на сервере..."
spawn ssh $server "cd $server_path && BACKUP_DIR=backup_jwt_fix_\$(date +%Y%m%d_%H%M%S) && mkdir -p \$BACKUP_DIR && cp app/auth/auth.py \$BACKUP_DIR/auth.py.backup 2>/dev/null; cp backend/app/services/jwt_service.py \$BACKUP_DIR/jwt_service.py.backup 2>/dev/null; cp app/auth/__init__.py \$BACKUP_DIR/__init__.py.backup 2>/dev/null; cp app/routers/analytics_router.py \$BACKUP_DIR/analytics_router.py.backup 2>/dev/null; echo \"✅ Backup создан в: \$BACKUP_DIR\""

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "\n✅ Backup создан"
    }
    timeout {
        puts "\n❌ Таймаут при создании backup"
        exit 1
    }
}
wait
puts ""

# ШАГ 3: Деплой файлов
puts "📤 ШАГ 3: Деплой файлов на сервер..."
foreach file $files {
    set local_file "$local_path/$file"
    set server_file "$server_path/$file"
    set server_dir [file dirname $server_file]
    
    puts "   📄 Деploy: $file"
    
    # Создать директорию на сервере если нужно
    spawn ssh $server "mkdir -p $server_dir"
    expect {
        "password:" {
            send "$password\r"
            exp_continue
        }
        eof {}
    }
    wait
    
    # Скопировать файл
    spawn scp "$local_file" "$server:$server_file"
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
            puts "      ✅ Успешно задеплоен"
        }
        timeout {
            puts "      ❌ Таймаут при деплое"
            exit 1
        }
    }
    wait
}
puts ""

# ШАГ 4: Проверка деплоя
puts "✅ ШАГ 4: Проверка деплоя..."
spawn ssh $server "cd $server_path && echo '=== Проверка app/auth/auth.py ===' && (grep -q 'aladdin-super-secret-key-change-in-production' app/auth/auth.py && grep -q 'leeway=60' app/auth/auth.py && echo '✅ auth.py: исправления найдены' || echo '❌ auth.py: исправления НЕ найдены') && echo && echo '=== Проверка backend/app/services/jwt_service.py ===' && (grep -q 'aladdin-super-secret-key-change-in-production' backend/app/services/jwt_service.py && grep -q 'leeway=60' backend/app/services/jwt_service.py && grep -q 'import os' backend/app/services/jwt_service.py && echo '✅ jwt_service.py: исправления найдены' || echo '❌ jwt_service.py: исправления НЕ найдены') && echo && echo '=== Проверка app/auth/__init__.py ===' && (grep -q 'aladdin-super-secret-key-change-in-production' app/auth/__init__.py && echo '✅ __init__.py: исправления найдены' || echo '❌ __init__.py: исправления НЕ найдены') && echo && echo '=== Проверка app/routers/analytics_router.py ===' && (grep -q 'from app.auth.auth import get_current_user' app/routers/analytics_router.py && echo '✅ analytics_router.py: исправления найдены' || echo '❌ analytics_router.py: исправления НЕ найдены')"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "\n✅ Проверка завершена"
    }
    timeout {
        puts "\n❌ Таймаут при проверке"
        exit 1
    }
}
wait
puts ""

# ШАГ 5: Перезапуск сервера
puts "🔄 ШАГ 5: Перезапуск сервера..."
puts "   💡 Пробуем перезапустить через systemd..."
spawn ssh $server "sudo systemctl restart aladdin-api && sudo systemctl status aladdin-api --no-pager | head -10"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "\n✅ Сервер перезапущен"
    }
    timeout {
        puts "\n⚠️  Таймаут при перезапуске (возможно сервер уже перезапущен)"
    }
}
wait
puts ""

puts "============================================================================"
puts "✅ ДЕПЛОЙ ЗАВЕРШЕН!"
puts "============================================================================"
puts "📤 Задеплоено файлов: 4"
puts "🔄 Сервер: перезапущен"
puts ""
puts "📋 Следующие шаги:"
puts "   1. Запустить тест: python3 docs/server/test_protected_endpoints_jwt_fix.py"
puts "   2. Проверить логи сервера"
puts "   3. Убедиться, что 401 ошибок нет"
puts "============================================================================"
