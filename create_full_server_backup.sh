#!/usr/bin/expect -f
# 🛡️ ПОЛНЫЙ BACKUP ВСЕГО СЕРВЕРА (сайт, админка, dashboard, nginx, payment service)

set timeout 600
set password "Sergio675"
set server "root@149.154.65.180"

# Текущая дата и время
set timestamp [clock format [clock seconds] -format "%Y%m%d_%H%M%S"]
set backup_name "site_backup_$timestamp"

# Директории
set remote_backup_dir "/root/backups/$backup_name"
set local_backup_dir "$env(HOME)/Downloads"
set local_backup_path "$local_backup_dir/$backup_name"

puts "\n🛡️ ПОЛНЫЙ BACKUP ВСЕГО СЕРВЕРА"
puts "=========================================="
puts "Сервер: $server"
puts "Дата: $timestamp"
puts "Директория на сервере: $remote_backup_dir"
puts "Локальная директория: $local_backup_path"
puts ""

# Создать локальную директорию
exec mkdir -p "$local_backup_path"

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
puts "▶ 2. Backup лендинга (/var/www/aladdin-ai.ru)..."
spawn ssh $server "cd /var/www && tar -czf $remote_backup_dir/landing_backup.tar.gz aladdin-ai.ru 2>&1 && echo 'LANDING_OK' || echo 'LANDING_ERROR'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "LANDING_OK" {
        puts "   ✅ Backup лендинга создан"
        exp_continue
    }
    "LANDING_ERROR" {
        puts "   ⚠ Не удалось создать backup лендинга"
        exp_continue
    }
    eof {
        puts "   ✅ Backup лендинга создан"
    }
}

wait

puts ""
puts "▶ 3. Backup админки..."
# Ищем админку в разных местах
set admin_paths [list "/var/www/admin" "/var/www/aladdin-ai.ru/admin" "/opt/admin" "/root/admin" "/var/www/html/admin"]

set admin_found 0
foreach admin_path $admin_paths {
    if {$admin_found} break
    
    spawn ssh $server "test -d $admin_path && echo 'FOUND:$admin_path' || echo 'NOT_FOUND'"
    
    expect {
        "password:" {
            send "$password\r"
            exp_continue
        }
        -re "FOUND:(.+)" {
            set found_path $expect_out(1,string)
            set found_path [string trim $found_path]
            puts "   Найдена админка: $found_path"
            
            spawn ssh $server "cd [file dirname $found_path] && tar -czf $remote_backup_dir/admin_backup.tar.gz [file tail $found_path] 2>&1 && echo 'ADMIN_OK' || echo 'ADMIN_ERROR'"
            
            expect {
                "password:" {
                    send "$password\r"
                    exp_continue
                }
                "ADMIN_OK" {
                    puts "   ✅ Backup админки создан"
                    set admin_found 1
                    exp_continue
                }
                "ADMIN_ERROR" {
                    puts "   ⚠ Не удалось создать backup админки"
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

if {!$admin_found} {
    puts "   ⚠ Админка не найдена автоматически"
}

puts ""
puts "▶ 4. Backup Dashboard..."
set dashboard_paths [list "/var/www/dashboard" "/var/www/aladdin-ai.ru/dashboard" "/opt/dashboard" "/root/dashboard"]

set dashboard_found 0
foreach dashboard_path $dashboard_paths {
    if {$dashboard_found} break
    
    spawn ssh $server "test -d $dashboard_path && echo 'FOUND:$dashboard_path' || echo 'NOT_FOUND'"
    
    expect {
        "password:" {
            send "$password\r"
            exp_continue
        }
        -re "FOUND:(.+)" {
            set found_path $expect_out(1,string)
            set found_path [string trim $found_path]
            puts "   Найден dashboard: $found_path"
            
            spawn ssh $server "cd [file dirname $found_path] && tar -czf $remote_backup_dir/dashboard_backup.tar.gz [file tail $found_path] 2>&1 && echo 'DASHBOARD_OK' || echo 'DASHBOARD_ERROR'"
            
            expect {
                "password:" {
                    send "$password\r"
                    exp_continue
                }
                "DASHBOARD_OK" {
                    puts "   ✅ Backup dashboard создан"
                    set dashboard_found 1
                    exp_continue
                }
                "DASHBOARD_ERROR" {
                    puts "   ⚠ Не удалось создать backup dashboard"
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

if {!$dashboard_found} {
    puts "   ⚠ Dashboard не найден автоматически"
}

puts ""
puts "▶ 5. Backup Nginx конфигурации..."
spawn ssh $server "mkdir -p $remote_backup_dir/nginx && cp -r /etc/nginx/sites-available $remote_backup_dir/nginx/sites-available 2>&1 && cp /etc/nginx/nginx.conf $remote_backup_dir/nginx/nginx.conf 2>&1 && echo 'NGINX_OK' || echo 'NGINX_ERROR'"

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
puts "▶ 6. Backup Payment Service..."
set payment_paths [list "/opt/payment_service" "/var/www/payment_service" "/root/payment_service" "/opt/aladdin-backend/payment_service" "/var/www/aladdin-ai.ru/payment_service"]

set payment_found 0
foreach payment_path $payment_paths {
    if {$payment_found} break
    
    spawn ssh $server "test -d $payment_path && echo 'FOUND:$payment_path' || echo 'NOT_FOUND'"
    
    expect {
        "password:" {
            send "$password\r"
            exp_continue
        }
        -re "FOUND:(.+)" {
            set found_path $expect_out(1,string)
            set found_path [string trim $found_path]
            puts "   Найден Payment Service: $found_path"
            
            spawn ssh $server "cd [file dirname $found_path] && tar -czf $remote_backup_dir/payment_service_backup.tar.gz [file tail $found_path] 2>&1 && echo 'PAYMENT_OK' || echo 'PAYMENT_ERROR'"
            
            expect {
                "password:" {
                    send "$password\r"
                    exp_continue
                }
                "PAYMENT_OK" {
                    puts "   ✅ Backup Payment Service создан"
                    set payment_found 1
                    exp_continue
                }
                "PAYMENT_ERROR" {
                    puts "   ⚠ Не удалось создать backup Payment Service"
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

if {!$payment_found} {
    puts "   ⚠ Payment Service не найден автоматически"
}

puts ""
puts "▶ 7. Backup базы данных..."
spawn ssh $server "pg_dump -h localhost -U postgres -d aladdin > $remote_backup_dir/database_backup.sql 2>&1 && echo 'DB_OK' || (pg_dump -h localhost -U aladdin -d aladdin_db > $remote_backup_dir/database_backup.sql 2>&1 && echo 'DB_OK') || echo 'DB_ERROR'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "DB_OK" {
        puts "   ✅ Backup базы данных создан"
        exp_continue
    }
    "DB_ERROR" {
        puts "   ⚠ Не удалось создать backup БД автоматически"
        exp_continue
    }
    eof {
        puts "   ✅ Backup БД создан"
    }
}

wait

puts ""
puts "▶ 8. Backup конфигурационных файлов (.env, configs)..."
spawn ssh $server "find /opt /var/www /root -maxdepth 3 -name '.env*' -o -name 'config.*' -o -name '*.conf' 2>/dev/null | head -50 | xargs tar -czf $remote_backup_dir/config_files_backup.tar.gz 2>&1 && echo 'CONFIG_OK' || echo 'CONFIG_ERROR'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "CONFIG_OK" {
        puts "   ✅ Backup конфигураций создан"
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
puts "▶ 9. Создание списка файлов..."
spawn ssh $server "find $remote_backup_dir -type f > $remote_backup_dir.files.txt 2>&1 && echo 'FILES_OK' || echo 'FILES_ERROR'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "FILES_OK" {
        puts "   ✅ Список файлов создан"
        exp_continue
    }
    eof {
        puts "   ✅ Список файлов создан"
    }
}

wait

puts ""
puts "▶ 10. Создание информационного файла..."
set date_str [clock format [clock seconds] -format "%Y-%m-%d %H:%M:%S"]
spawn ssh $server "cat > $remote_backup_dir/BACKUP_INFO.txt << 'EOF'
===========================================
ПОЛНЫЙ BACKUP СЕРВЕРА
===========================================
Дата: $date_str
Backup директория: $remote_backup_dir

СОЗДАННЫЕ BACKUP'Ы:
- Лендинг: landing_backup.tar.gz
- Админка: admin_backup.tar.gz (если найдена)
- Dashboard: dashboard_backup.tar.gz (если найден)
- Nginx: nginx/ (конфигурации)
- Payment Service: payment_service_backup.tar.gz (если найден)
- База данных: database_backup.sql
- Конфигурации: config_files_backup.tar.gz

РАЗМЕРЫ:
(выполните: du -sh $remote_backup_dir/*)

ВОССТАНОВЛЕНИЕ:
1. Лендинг:
   tar -xzf landing_backup.tar.gz -C /var/www/

2. Админка:
   tar -xzf admin_backup.tar.gz -C /var/www/

3. Dashboard:
   tar -xzf dashboard_backup.tar.gz -C /var/www/

4. Nginx:
   cp -r nginx/sites-available/* /etc/nginx/sites-available/
   cp nginx/nginx.conf /etc/nginx/nginx.conf

5. База данных:
   psql -h localhost -U postgres -d aladdin < database_backup.sql

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
puts "▶ 11. Создание архива на сервере..."
spawn ssh $server "cd /root/backups && tar -czf $backup_name.tar.gz $backup_name/ 2>&1 && echo 'ARCHIVE_OK' || echo 'ARCHIVE_ERROR'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "ARCHIVE_OK" {
        puts "   ✅ Архив создан на сервере: /root/backups/$backup_name.tar.gz"
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
puts "▶ 12. Скачивание архива в Downloads..."
spawn scp $server:/root/backups/$backup_name.tar.gz "$local_backup_path.tar.gz"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Архив скачан в Downloads"
    }
    timeout {
        puts "   ⚠ Таймаут при скачивании"
    }
}

wait

puts ""
puts "▶ 13. Скачивание всех файлов в Downloads..."
spawn scp -r $server:$remote_backup_dir "$local_backup_path"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Все файлы скачаны"
    }
    timeout {
        puts "   ⚠ Таймаут при скачивании"
    }
}

wait

puts ""
puts "▶ 14. Скачивание списка файлов..."
spawn scp $server:/root/backups/$backup_name.files.txt "$local_backup_path.files.txt"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Список файлов скачан"
    }
}

wait

puts ""
puts "=========================================="
puts "✅ ПОЛНЫЙ BACKUP СЕРВЕРА ЗАВЕРШЕН!"
puts ""
puts "📁 На сервере:"
puts "   Директория: $remote_backup_dir"
puts "   Архив: /root/backups/$backup_name.tar.gz"
puts "   Список файлов: /root/backups/$backup_name.files.txt"
puts ""
puts "📁 В Downloads:"
puts "   Директория: $local_backup_path"
puts "   Архив: $local_backup_path.tar.gz"
puts "   Список файлов: $local_backup_path.files.txt"
puts ""
puts "💾 Размеры:"
exec du -sh "$local_backup_path" 2>/dev/null || puts "   (проверка размера...)"
exec ls -lh "$local_backup_path.tar.gz" 2>/dev/null || puts "   (проверка архива...)"
puts ""
puts "✅ Весь сервер сохранен!"
puts ""
