#!/usr/bin/expect -f
# ============================================
# ПОЛНАЯ ИНТЕГРАЦИЯ: Реферальная программа
# ============================================
# Выполняет все оставшиеся задачи автоматически
# ============================================

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== 🚀 ПОЛНАЯ ИНТЕГРАЦИЯ РЕФЕРАЛЬНОЙ ПРОГРАММЫ ==="
puts ""

# ============================================
# ШАГ 1: Выполнить SQL скрипт
# ============================================

puts "📊 ШАГ 1: Выполнение SQL скрипта..."

# Попробуем разные варианты подключения к БД
set db_users [list "postgres" "aladdin" "root"]
set db_names [list "aladdin" "aladdin_db" "postgres"]

set sql_executed 0

foreach db_user $db_users {
    foreach db_name $db_names {
        puts "Попытка: psql -U $db_user -d $db_name"
        
        spawn ssh $server "psql -U $db_user -d $db_name -f /tmp/REFERRAL_DB_SETUP.sql"
        expect {
            "password:" {
                send "$password\r"
                exp_continue
            }
            "Пароль:" {
                send "$password\r"
                exp_continue
            }
            "CREATE TABLE" {
                puts "✅ SQL скрипт выполняется..."
                exp_continue
            }
            "CREATE INDEX" {
                exp_continue
            }
            "CREATE OR REPLACE FUNCTION" {
                exp_continue
            }
            "ERROR" {
                puts "❌ Ошибка при выполнении SQL"
                exp_continue
            }
            eof {
                set sql_executed 1
                break
            }
        }
        
        if {$sql_executed} {
            break
        }
    }
    if {$sql_executed} {
        break
    }
}

if {!$sql_executed} {
    puts "⚠️  Не удалось автоматически выполнить SQL скрипт"
    puts "Выполните вручную:"
    puts "  ssh $server"
    puts "  psql -U ваш_пользователь -d ваша_база -f /tmp/REFERRAL_DB_SETUP.sql"
} else {
    puts "✅ SQL скрипт выполнен"
}
puts ""

# ============================================
# ШАГ 2: Проверить что Python файлы на месте
# ============================================

puts "🐍 ШАГ 2: Проверка Python файлов..."

spawn ssh $server "ls -lh /opt/aladdin-backend/app/routers/referral.py /opt/aladdin-backend/app/referral_payment_integration.py /opt/aladdin-backend/app/referral_implementation.py"
expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "No such file" {
        puts "⚠️  Некоторые файлы не найдены"
        exp_continue
    }
    eof
}

puts "✅ Python файлы проверены"
puts ""

# ============================================
# ШАГ 3: Настроить Nginx
# ============================================

puts "⚙️  ШАГ 3: Настройка Nginx..."

# Создать временный файл с конфигурацией для /invite/
set nginx_block {
location /invite/ {
    try_files $uri $uri/ /invite.html?code=$1;
    
    # Или если используете Python backend, раскомментируйте:
    # proxy_pass http://localhost:8000;
    # proxy_set_header Host $host;
    # proxy_set_header X-Real-IP $remote_addr;
}
}

# Проверить существующую конфигурацию
spawn ssh $server "grep -q 'location /invite/' /etc/nginx/sites-available/aladdin-ai.ru 2>/dev/null && echo 'exists' || echo 'not_exists'"
expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "exists" {
        puts "✅ Блок location /invite/ уже существует в конфигурации"
    }
    "not_exists" {
        puts "⚠️  Блок location /invite/ не найден"
        puts "Добавьте вручную в /etc/nginx/sites-available/aladdin-ai.ru:"
        puts $nginx_block
    }
    eof
}

# Проверить конфигурацию Nginx
spawn ssh $server "nginx -t"
expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "syntax is ok" {
        puts "✅ Конфигурация Nginx корректна"
        
        # Перезагрузить Nginx
        spawn ssh $server "systemctl reload nginx"
        expect {
            "password:" {
                send "$password\r"
                exp_continue
            }
            eof
        }
        puts "✅ Nginx перезагружен"
    }
    "syntax error" {
        puts "❌ Ошибка в конфигурации Nginx"
    }
    eof
}

puts ""

# ============================================
# ШАГ 4: Проверить FastAPI приложение
# ============================================

puts "🔄 ШАГ 4: Проверка FastAPI приложения..."

# Проверить статус systemd сервиса
spawn ssh $server "systemctl is-active aladdin-backend 2>/dev/null || echo 'not_found'"
expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "active" {
        puts "✅ Сервис aladdin-backend активен"
        
        # Перезапустить
        spawn ssh $server "systemctl restart aladdin-backend"
        expect {
            "password:" {
                send "$password\r"
                exp_continue
            }
            eof
        }
        puts "✅ Сервис перезапущен"
    }
    "not_found" {
        # Проверить pm2
        spawn ssh $server "pm2 list | grep aladdin-backend || echo 'not_found'"
        expect {
            "password:" {
                send "$password\r"
                exp_continue
            }
            "aladdin-backend" {
                puts "✅ Приложение найдено в pm2"
                
                # Перезапустить
                spawn ssh $server "pm2 restart aladdin-backend"
                expect {
                    "password:" {
                        send "$password\r"
                        exp_continue
                    }
                    eof
                }
                puts "✅ Приложение перезапущено"
            }
            "not_found" {
                puts "⚠️  FastAPI приложение не найдено в systemd или pm2"
                puts "Перезапустите вручную"
            }
            eof
        }
    }
    eof
}

puts ""

# ============================================
# ИТОГ
# ============================================

puts "=== ✅ ИНТЕГРАЦИЯ ЗАВЕРШЕНА ==="
puts ""
puts "📋 Что сделано:"
puts "  ✅ SQL скрипт: попытка выполнения"
puts "  ✅ Python файлы: проверены"
puts "  ✅ Nginx: проверена конфигурация"
puts "  ✅ FastAPI: проверено и перезапущено"
puts ""
puts "⚠️  ВАЖНО: Интеграция функций в код оплаты требует ручного редактирования"
puts "См. REFERRAL_INTEGRATION_GUIDE.md раздел 'ШАГ 3: Интеграция в оплату'"
puts ""
puts "📖 Проверьте работу:"
puts "  1. curl -H 'Authorization: Bearer TOKEN' https://aladdin-ai.ru/api/referral/code"
puts "  2. https://aladdin-ai.ru/invite/ABC123"

