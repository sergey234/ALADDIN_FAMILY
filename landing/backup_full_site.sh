#!/usr/bin/expect -f

# Полный бэкап сайта (лендинг + админка)

set timeout 300
set password "Sergio675"
set server "root@149.154.65.180"

set timestamp [clock format [clock seconds] -format "%Y%m%d_%H%M%S"]
set backup_dir "/root/backups/site_backup_$timestamp"

puts "💾 СОЗДАНИЕ ПОЛНОГО БЭКАПА САЙТА"
puts "=========================================="
puts "Дата: $timestamp"
puts ""

# 1. Создать директорию для бэкапа
puts "1️⃣ Создаю директорию для бэкапа..."
spawn ssh $server "mkdir -p $backup_dir && echo 'DIRECTORY_CREATED'"
expect "password:" { send "$password\r" }
expect eof

puts "✅ Директория создана: $backup_dir"
puts ""

# 2. Бэкап лендинга
puts "2️⃣ Копирую лендинг..."
spawn ssh $server "mkdir -p $backup_dir/landing && cp -r /var/www/aladdin-ai.ru/* $backup_dir/landing/ 2>&1 && echo 'LANDING_BACKED_UP'"
expect "password:" { send "$password\r" }
expect eof

set landing_result [string trim $expect_out(buffer)]
puts "$landing_result"
puts ""

# 3. Бэкап админки
puts "3️⃣ Копирую админку..."
spawn ssh $server "mkdir -p $backup_dir/admin && cp -r /var/www/aladdin-ai.ru/admin $backup_dir/admin/ 2>&1 && echo 'ADMIN_BACKED_UP'"
expect "password:" { send "$password\r" }
expect eof

set admin_result [string trim $expect_out(buffer)]
puts "$admin_result"
puts ""

# 4. Бэкап dashboard
puts "4️⃣ Копирую dashboard..."
spawn ssh $server "test -d /var/www/aladdin-ai.ru/dashboard && mkdir -p $backup_dir/dashboard && cp -r /var/www/aladdin-ai.ru/dashboard $backup_dir/dashboard/ 2>&1 && echo 'DASHBOARD_BACKED_UP' || echo 'DASHBOARD_NOT_FOUND'"
expect "password:" { send "$password\r" }
expect eof

set dashboard_result [string trim $expect_out(buffer)]
puts "$dashboard_result"
puts ""

# 5. Бэкап Nginx конфигурации
puts "5️⃣ Копирую Nginx конфигурацию..."
spawn ssh $server "mkdir -p $backup_dir/nginx && cp /etc/nginx/sites-enabled/aladdin-ai.ru $backup_dir/nginx/ 2>&1 && cp /etc/nginx/nginx.conf $backup_dir/nginx/nginx.conf.backup 2>&1 && echo 'NGINX_BACKED_UP'"
expect "password:" { send "$password\r" }
expect eof

set nginx_result [string trim $expect_out(buffer)]
puts "$nginx_result"
puts ""

# 6. Бэкап payment_service (только конфигурация и код)
puts "6️⃣ Копирую payment_service..."
spawn ssh $server "mkdir -p $backup_dir/payment_service && cp -r /opt/aladdin-backend/app $backup_dir/payment_service/ 2>&1 && cp /opt/aladdin-backend/main.py $backup_dir/payment_service/ 2>&1 && cp /opt/aladdin-backend/requirements.txt $backup_dir/payment_service/ 2>&1 && echo 'PAYMENT_SERVICE_BACKED_UP'"
expect "password:" { send "$password\r" }
expect eof

set payment_result [string trim $expect_out(buffer)]
puts "$payment_result"
puts ""

# 7. Создать архив
puts "7️⃣ Создаю архив..."
spawn ssh $server "cd /root/backups && tar -czf site_backup_$timestamp.tar.gz site_backup_$timestamp/ 2>&1 && echo 'ARCHIVE_CREATED'"
expect "password:" { send "$password\r" }
expect eof

set archive_result [string trim $expect_out(buffer)]
puts "$archive_result"
puts ""

# 8. Проверить размер архива
puts "8️⃣ Проверяю размер архива..."
spawn ssh $server "ls -lh /root/backups/site_backup_$timestamp.tar.gz 2>&1"
expect "password:" { send "$password\r" }
expect eof

set size_result [string trim $expect_out(buffer)]
puts "$size_result"
puts ""

# 9. Создать список файлов
puts "9️⃣ Создаю список файлов..."
spawn ssh $server "cd $backup_dir && find . -type f > /root/backups/site_backup_$timestamp.files.txt 2>&1 && wc -l /root/backups/site_backup_$timestamp.files.txt"
expect "password:" { send "$password\r" }
expect eof

set files_result [string trim $expect_out(buffer)]
puts "$files_result"
puts ""

# 10. Показать структуру бэкапа
puts "🔟 Структура бэкапа:"
spawn ssh $server "tree -L 2 $backup_dir 2>&1 || find $backup_dir -maxdepth 2 -type d | sort"
expect "password:" { send "$password\r" }
expect eof

set structure_result [string trim $expect_out(buffer)]
puts "$structure_result"
puts ""

puts "=========================================="
puts "✅ БЭКАП СОЗДАН УСПЕШНО!"
puts ""
puts "📁 Расположение:"
puts "   Директория: $backup_dir"
puts "   Архив: /root/backups/site_backup_$timestamp.tar.gz"
puts "   Список файлов: /root/backups/site_backup_$timestamp.files.txt"
puts ""
puts "💡 Для восстановления:"
puts "   tar -xzf /root/backups/site_backup_$timestamp.tar.gz"
puts ""

