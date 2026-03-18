#!/usr/bin/expect -f
# 🛡️ ПОЛНЫЙ BACKUP ВСЕГО САЙТА С СЕРВЕРА

set timeout 300
# SECURITY: Never store passwords in the repository.
# Prefer SSH keys. If password auth is absolutely required, pass it via env var:
#   export ALADDIN_SSH_PASSWORD='...'
if {![info exists env(ALADDIN_SSH_PASSWORD)]} {
    puts "❌ SECURITY: ALADDIN_SSH_PASSWORD не задана. Настройте SSH-ключи (рекомендуется) и повторите."
    exit 1
}
set password $env(ALADDIN_SSH_PASSWORD)
set server "root@149.154.65.180"

# Локальная директория для backup'ов
set local_backup_dir "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/BACKUPS"
set timestamp [clock format [clock seconds] -format "%Y%m%d_%H%M%S"]
set backup_name "FULL_SITE_BACKUP_$timestamp"
set local_backup_path "$local_backup_dir/$backup_name"
set remote_backup_dir "/tmp/full_site_backup_$timestamp"

puts "🛡️ ПОЛНЫЙ BACKUP ВСЕГО САЙТА"
puts "=========================================="
puts "Сервер: $server"
puts "Локальная директория: $local_backup_path"
puts ""

# Создать локальную директорию
exec mkdir -p "$local_backup_path"
exec mkdir -p "$local_backup_path/database"
exec mkdir -p "$local_backup_path/nginx"
exec mkdir -p "$local_backup_path/website"
exec mkdir -p "$local_backup_path/project"
exec mkdir -p "$local_backup_path/system"

puts "▶ 1. Создание backup директории на сервере..."
spawn ssh $server "mkdir -p $remote_backup_dir && echo 'OK'"

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

puts ""
puts "▶ 2. Backup базы данных..."

# Пробуем разные варианты пользователя и базы данных
set db_users [list "postgres" "aladdin" "root"]
set db_names [list "aladdin" "aladdin_db" "postgres"]

set db_backup_created 0

foreach db_user $db_users {
    foreach db_name $db_names {
        if {$db_backup_created} break
        
        puts "   Пробую: user=$db_user, database=$db_name"
        
        spawn ssh $server "pg_dump -h localhost -U $db_user -d $db_name > $remote_backup_dir/database_full_backup.sql 2>&1 && echo 'DB_OK' || echo 'DB_ERROR'"
        
        expect {
            "password:" {
                send "$password\r"
                exp_continue
            }
            "DB_OK" {
                puts "   ✅ Backup БД создан (user=$db_user, database=$db_name)"
                set db_backup_created 1
                exp_continue
            }
            "DB_ERROR" {
                # Пробуем следующий вариант
                exp_continue
            }
            eof {
                if {$db_backup_created} break
            }
        }
        wait
    }
    if {$db_backup_created} break
}

if {!$db_backup_created} {
    puts "   ⚠ Не удалось создать backup БД автоматически"
    puts "   Выполните вручную: pg_dump -h localhost -U user -d database > backup.sql"
}

puts ""
puts "▶ 3. Backup Nginx конфигурации..."

# Backup всех Nginx конфигураций
spawn ssh $server "cp -r /etc/nginx/sites-available $remote_backup_dir/nginx_sites_available 2>&1 && cp /etc/nginx/nginx.conf $remote_backup_dir/nginx_main.conf 2>&1 && echo 'NGINX_OK' || echo 'NGINX_ERROR'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "NGINX_OK" {
        puts "   ✅ Backup Nginx создан"
        exp_continue
    }
    "NGINX_ERROR" {
        puts "   ⚠ Не удалось создать backup Nginx"
        exp_continue
    }
    eof {
        puts "   ✅ Backup Nginx создан"
    }
}

wait

puts ""
puts "▶ 4. Backup всего сайта (/var/www/aladdin-ai.ru)..."

spawn ssh $server "tar -czf $remote_backup_dir/website_full_backup.tar.gz -C /var/www aladdin-ai.ru 2>&1 && echo 'WEBSITE_OK' || echo 'WEBSITE_ERROR'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "WEBSITE_OK" {
        puts "   ✅ Backup сайта создан"
        exp_continue
    }
    "WEBSITE_ERROR" {
        puts "   ⚠ Не удалось создать backup сайта"
        exp_continue
    }
    eof {
        puts "   ✅ Backup сайта создан"
    }
}

wait

puts ""
puts "▶ 5. Backup Python/FastAPI проекта..."

# Ищем проект в разных местах
set project_paths [list "/opt/aladdin-backend" "/var/www/aladdin" "/root/aladdin" "/app" "/srv/aladdin" "/home/*/aladdin"]

set project_found 0

foreach path_pattern $project_paths {
    if {$project_found} break
    
    spawn ssh $server "test -d $path_pattern && echo 'FOUND:$path_pattern' || echo 'NOT_FOUND'"
    
    expect {
        "password:" {
            send "$password\r"
            exp_continue
        }
        -re "FOUND:(.+)" {
            set found_path $expect_out(1,string)
            set found_path [string trim $found_path]
            puts "   Найден проект: $found_path"
            
            # Создать архив проекта
            set project_name [file tail $found_path]
            set project_parent [file dirname $found_path]
            spawn ssh $server "cd $project_parent && tar -czf $remote_backup_dir/project_backup.tar.gz $project_name 2>&1 && echo 'PROJECT_OK' || echo 'PROJECT_ERROR'"
            
            expect {
                "password:" {
                    send "$password\r"
                    exp_continue
                }
                "PROJECT_OK" {
                    puts "   ✅ Backup проекта создан"
                    set project_found 1
                    exp_continue
                }
                "PROJECT_ERROR" {
                    puts "   ⚠ Не удалось создать backup проекта"
                    exp_continue
                }
                eof {
                    break
                }
            }
            wait
            
            # Создать Git tag если есть Git
            spawn ssh $server "cd $found_path && test -d .git && (git add . && git commit -m 'Full site backup $timestamp' && git tag full-backup-$timestamp && echo 'GIT_OK') || echo 'NO_GIT'"
            
            expect {
                "password:" {
                    send "$password\r"
                    exp_continue
                }
                "GIT_OK" {
                    puts "   ✅ Git tag создан: full-backup-$timestamp"
                    exp_continue
                }
                "NO_GIT" {
                    puts "   ℹ Git не используется"
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

if {!$project_found} {
    puts "   ⚠ Проект не найден автоматически"
}

puts ""
puts "▶ 6. Backup системных файлов..."

# Backup .env файлов, конфигураций и т.д.
spawn ssh $server "find /opt /var/www /root -name '.env*' -o -name '*.conf' -o -name 'config.*' 2>/dev/null | head -20 | xargs tar -czf $remote_backup_dir/config_files_backup.tar.gz 2>&1 && echo 'CONFIG_OK' || echo 'CONFIG_ERROR'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "CONFIG_OK" {
        puts "   ✅ Backup конфигурационных файлов создан"
        exp_continue
    }
    "CONFIG_ERROR" {
        puts "   ⚠ Не удалось создать backup конфигураций"
        exp_continue
    }
    eof {
        puts "   ✅ Backup конфигураций создан"
    }
}

wait

puts ""
puts "▶ 7. Создание информационного файла на сервере..."

set date_str [clock format [clock seconds] -format "%Y-%m-%d %H:%M:%S"]
spawn ssh $server "cat > $remote_backup_dir/BACKUP_INFO.txt << 'EOF'
===========================================
ПОЛНЫЙ BACKUP САЙТА
===========================================
Дата: $date_str
Backup директория: $remote_backup_dir

СОЗДАННЫЕ BACKUP'Ы:
- База данных: database_full_backup.sql
- Nginx: nginx_sites_available/, nginx_main.conf
- Сайт: website_full_backup.tar.gz
- Проект: project_backup.tar.gz
- Конфигурации: config_files_backup.tar.gz

РАЗМЕРЫ:
(выполните: du -sh $remote_backup_dir/*)

ВОССТАНОВЛЕНИЕ:
1. База данных:
   psql -h localhost -U user -d database < database_full_backup.sql

2. Nginx:
   cp -r nginx_sites_available/* /etc/nginx/sites-available/
   cp nginx_main.conf /etc/nginx/nginx.conf

3. Сайт:
   tar -xzf website_full_backup.tar.gz -C /var/www/

4. Проект:
   tar -xzf project_backup.tar.gz -C /path/to/

===========================================
EOF
echo 'INFO_OK'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "INFO_OK" {
        puts "   ✅ Информационный файл создан"
        exp_continue
    }
    eof {
        puts "   ✅ Информационный файл создан"
    }
}

wait

puts ""
puts "▶ 8. Создание архива на сервере..."

spawn ssh $server "cd /tmp && tar -czf full_site_backup_$timestamp.tar.gz full_site_backup_$timestamp/ 2>&1 && echo 'ARCHIVE_OK' || echo 'ARCHIVE_ERROR'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "ARCHIVE_OK" {
        puts "   ✅ Архив создан на сервере"
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
puts "▶ 9. Скачивание всех backup'ов на локальный компьютер..."

# Скачать архив с сервера
puts "   Скачивание полного архива..."
spawn rsync -avz --progress $server:/tmp/full_site_backup_$timestamp.tar.gz "$local_backup_path/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Архив скачан"
    }
    timeout {
        puts "   ⚠ Таймаут при скачивании"
    }
}

wait

# Также скачать отдельные файлы для удобства
puts "   Скачивание отдельных файлов..."
spawn rsync -avz --progress $server:$remote_backup_dir/ "$local_backup_path/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Все файлы скачаны"
    }
}

wait

puts ""
puts "▶ 10. Распаковка архива локально..."

exec cd "$local_backup_path" && tar -xzf full_site_backup_$timestamp.tar.gz 2>/dev/null || puts "   ⚠ Не удалось распаковать (возможно, уже распакован)"

puts ""
puts "=========================================="
puts "✅ ПОЛНЫЙ BACKUP ЗАВЕРШЕН!"
puts ""
puts "📁 Локальная директория: $local_backup_path"
puts "📁 На сервере: $remote_backup_dir"
puts "📦 Архив: $local_backup_path/full_site_backup_$timestamp.tar.gz"
puts ""
puts "📋 СОДЕРЖИМОЕ BACKUP'А:"
exec ls -lh "$local_backup_path" | head -20
puts ""
puts "💾 РАЗМЕР BACKUP'А:"
exec du -sh "$local_backup_path"
puts ""
puts "✅ Весь сайт сохранен!"
puts ""

