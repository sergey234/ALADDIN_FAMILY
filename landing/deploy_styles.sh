#!/usr/bin/expect -f

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"
set local_styles "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/styles.css"
set remote_base "/var/www"

puts "📤 Загружаем обновленный styles.css на сервер..."
puts ""

# Найти директорию сайта
spawn ssh $server "find $remote_base -name 'index.html' -path '*aladdin*' 2>/dev/null | head -1 | xargs dirname 2>/dev/null || echo '/var/www/html'"
expect "password:" { send "$password\r" }
expect eof

set site_dir [string trim $expect_out(buffer)]
if {[string length $site_dir] < 5} {
    set site_dir "/var/www/html"
}

puts "✅ Найдена директория: $site_dir"
puts ""

# Создать бэкап
spawn ssh $server "cp ${site_dir}/styles.css ${site_dir}/styles.css.backup_\$(date +%Y%m%d_%H%M%S) 2>/dev/null && echo 'BACKUP_OK' || echo 'BACKUP_SKIPPED'"
expect "password:" { send "$password\r" }
expect eof

# Загрузить файл
puts "📤 Загружаем styles.css..."
spawn scp $local_styles $server:${site_dir}/styles.css
expect "password:" { send "$password\r" }
expect eof

# Установить права
spawn ssh $server "chmod 644 ${site_dir}/styles.css && chown www-data:www-data ${site_dir}/styles.css 2>/dev/null || chown nginx:nginx ${site_dir}/styles.css 2>/dev/null || true && echo 'PERMS_OK'"
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ Готово! styles.css обновлен на сервере."
puts ""

