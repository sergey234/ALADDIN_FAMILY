#!/usr/bin/expect -f
# 🛡️ Автоматическое создание backup'ов на сервере

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

puts "🛡️ СОЗДАНИЕ BACKUP'ОВ НА СЕРВЕРЕ"
puts "=========================================="
puts "Сервер: $server"
puts ""

# Создать директорию для backup'ов
set backup_dir "/tmp/referral_backup_$(date +%Y%m%d_%H%M%S)"
set timestamp [clock format [clock seconds] -format "%Y%m%d_%H%M%S"]

puts "▶ 1. Создание backup директории на сервере..."
spawn ssh $server "mkdir -p /tmp/referral_backup_$timestamp && echo '/tmp/referral_backup_$timestamp'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "Are you sure you want to continue connecting" {
        send "yes\r"
        exp_continue
    }
    "/tmp/referral_backup_" {
        set backup_dir $expect_out(buffer)
        puts "   ✅ Директория создана: $backup_dir"
        exp_continue
    }
    eof {
        puts "   ✅ Директория создана"
    }
    timeout {
        puts "   ⚠ Таймаут"
    }
}

wait

puts ""
puts "▶ 2. Backup базы данных..."

# Backup базы данных (нужно указать параметры)
set db_user "postgres"
set db_name "aladdin"

spawn ssh $server "pg_dump -h localhost -U $db_user -d $db_name > /tmp/referral_backup_$timestamp/database_full_backup.sql 2>&1 || echo 'ERROR: Не удалось создать backup БД'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "ERROR:" {
        puts "   ⚠ Не удалось создать backup БД автоматически"
        puts "   Выполните вручную: pg_dump -h localhost -U user -d database > backup.sql"
        exp_continue
    }
    eof {
        puts "   ✅ Backup БД создан"
    }
    timeout {
        puts "   ⚠ Таймаут"
    }
}

wait

puts ""
puts "▶ 3. Backup Nginx конфигурации..."

spawn ssh $server "cp /etc/nginx/sites-available/aladdin-ai.ru /tmp/referral_backup_$timestamp/nginx_aladdin-ai.ru.backup 2>&1 && echo 'OK' || echo 'ERROR'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "OK" {
        puts "   ✅ Backup Nginx создан"
        exp_continue
    }
    "ERROR" {
        puts "   ⚠ Не удалось создать backup Nginx"
        exp_continue
    }
    eof {
        puts "   ✅ Backup Nginx создан"
    }
}

wait

puts ""
puts "▶ 4. Backup Python проекта..."

# Ищем проект в типичных местах
set project_paths [list "/opt/aladdin-backend" "/var/www/aladdin" "/root/aladdin" "/app"]

foreach path $project_paths {
    spawn ssh $server "test -d $path && echo 'FOUND:$path' || echo 'NOT_FOUND'"
    
    expect {
        "password:" {
            send "$password\r"
            exp_continue
        }
        "FOUND:" {
            set found_path $expect_out(buffer)
            puts "   Найден проект: $found_path"
            
            # Создать Git tag если есть Git
            spawn ssh $server "cd $found_path && test -d .git && (git add . && git commit -m 'Backup before referral' && git tag backup-referral-$timestamp && echo 'GIT_OK') || echo 'NO_GIT'"
            
            expect {
                "password:" {
                    send "$password\r"
                    exp_continue
                }
                "GIT_OK" {
                    puts "   ✅ Git tag создан"
                    exp_continue
                }
                "NO_GIT" {
                    puts "   ⚠ Git не используется"
                    exp_continue
                }
                eof {
                    break
                }
            }
            wait
            break
        }
        "NOT_FOUND" {
            continue
        }
        eof {
            continue
        }
    }
    wait
}

puts ""
puts "▶ 5. Создание информационного файла..."

spawn ssh $server "cat > /tmp/referral_backup_$timestamp/BACKUP_INFO.txt << 'EOF'
===========================================
BACKUP ИНФОРМАЦИЯ
===========================================
Дата: $(date)
Backup директория: /tmp/referral_backup_$timestamp

СОЗДАННЫЕ BACKUP'Ы:
- База данных: database_full_backup.sql
- Nginx: nginx_aladdin-ai.ru.backup
- Python проект: Git tag backup-referral-$timestamp

ВОССТАНОВЛЕНИЕ:
1. База данных:
   psql -h localhost -U user -d database < database_full_backup.sql

2. Nginx:
   cp nginx_aladdin-ai.ru.backup /etc/nginx/sites-available/aladdin-ai.ru
   nginx -t && systemctl reload nginx

3. Проект (Git):
   cd /path/to/project
   git checkout backup-referral-$timestamp

===========================================
EOF
echo 'OK'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "OK" {
        puts "   ✅ Информационный файл создан"
        exp_continue
    }
    eof {
        puts "   ✅ Информационный файл создан"
    }
}

wait

puts ""
puts "▶ 6. Создание архива..."

spawn ssh $server "cd /tmp && tar -czf referral_backup_$timestamp.tar.gz referral_backup_$timestamp/ 2>&1 && echo 'ARCHIVE_OK' || echo 'ARCHIVE_ERROR'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "ARCHIVE_OK" {
        puts "   ✅ Архив создан: /tmp/referral_backup_$timestamp.tar.gz"
        exp_continue
    }
    "ARCHIVE_ERROR" {
        puts "   ⚠ Не удалось создать архив"
        exp_continue
    }
    eof {
        puts "   ✅ Архив создан"
    }
}

wait

puts ""
puts "=========================================="
puts "✅ BACKUP ЗАВЕРШЕН!"
puts ""
puts "Backup директория на сервере: /tmp/referral_backup_$timestamp"
puts "Архив: /tmp/referral_backup_$timestamp.tar.gz"
puts ""
puts "📋 Для просмотра backup'ов выполните:"
puts "   ssh $server 'ls -lh /tmp/referral_backup_$timestamp'"
puts ""


