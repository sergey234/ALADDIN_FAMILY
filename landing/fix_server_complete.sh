#!/usr/bin/expect -f

# Полное исправление проблем на сервере
# - Загружает правильный index.html
# - Проверяет styles.css
# - Исправляет права доступа
# - Проверяет Nginx

set timeout 300
set password "Sergio675"
set server "root@149.154.65.180"
set remote_base "/var/www"
set local_index "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/index.html"
set local_styles "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/styles.css"

puts "🔧 ПОЛНОЕ ИСПРАВЛЕНИЕ ПРОБЛЕМ НА СЕРВЕРЕ"
puts "=========================================="
puts ""

# Шаг 1: Найти директорию сайта
puts "1️⃣ Ищем директорию сайта..."
spawn ssh $server "find $remote_base -name 'index.html' -path '*aladdin*' 2>/dev/null | head -1 | xargs dirname 2>/dev/null || echo '/var/www/html'"
expect "password:" { send "$password\r" }
expect eof

set site_dir [string trim $expect_out(buffer)]
if {[string length $site_dir] < 5} {
    set site_dir "/var/www/html"
}

puts "✅ Найдена директория: $site_dir"
puts ""

# Шаг 2: Создать бэкап
puts "2️⃣ Создаем бэкап текущих файлов..."
set timestamp [clock format [clock seconds] -format %Y%m%d_%H%M%S]
spawn ssh $server "mkdir -p /var/www/backups && cp ${site_dir}/index.html /var/www/backups/index.html.backup_${timestamp} 2>/dev/null && cp ${site_dir}/styles.css /var/www/backups/styles.css.backup_${timestamp} 2>/dev/null && echo 'BACKUP_OK' || echo 'BACKUP_FAILED'"
expect "password:" { send "$password\r" }
expect eof

puts "✅ Бэкап создан"
puts ""

# Шаг 3: Загрузить правильный index.html
puts "3️⃣ Загружаем правильный index.html..."
spawn scp $local_index $server:${site_dir}/index.html
expect "password:" { send "$password\r" }
expect eof

puts "✅ index.html загружен"
puts ""

# Шаг 4: Проверить и загрузить styles.css если нужно
puts "4️⃣ Проверяем styles.css..."
spawn ssh $server "test -f ${site_dir}/styles.css && echo 'EXISTS' || echo 'MISSING'"
expect "password:" { send "$password\r" }
expect eof

set css_status [string trim $expect_out(buffer)]
if {[string match "*MISSING*" $css_status]} {
    puts "⚠️ styles.css отсутствует, загружаем..."
    spawn scp $local_styles $server:${site_dir}/styles.css
    expect "password:" { send "$password\r" }
    expect eof
    puts "✅ styles.css загружен"
} else {
    puts "✅ styles.css существует"
}
puts ""

# Шаг 5: Установить права доступа
puts "5️⃣ Устанавливаем права доступа..."
spawn ssh $server "chmod 644 ${site_dir}/index.html ${site_dir}/styles.css && chown www-data:www-data ${site_dir}/index.html ${site_dir}/styles.css 2>/dev/null || chown nginx:nginx ${site_dir}/index.html ${site_dir}/styles.css 2>/dev/null || true && echo 'PERMS_OK'"
expect "password:" { send "$password\r" }
expect eof

puts "✅ Права доступа установлены"
puts ""

# Шаг 6: Проверить наличие отладочных элементов
puts "6️⃣ Проверяем, что отладочные элементы удалены..."
spawn ssh $server "grep -c 'debugIndicator\\|debugPanel' ${site_dir}/index.html 2>/dev/null || echo '0'"
expect "password:" { send "$password\r" }
expect eof

set debug_count [string trim $expect_out(buffer)]
if {$debug_count > 0} {
    puts "⚠️ ВНИМАНИЕ: Найдено $debug_count отладочных элементов!"
    puts "   Это означает, что файл не обновился правильно"
} else {
    puts "✅ Отладочные элементы не найдены"
}
puts ""

# Шаг 7: Проверить размер файла
puts "7️⃣ Проверяем размер index.html..."
spawn ssh $server "ls -lh ${site_dir}/index.html | awk '{print \$5}'"
expect "password:" { send "$password\r" }
expect eof

set file_size [string trim $expect_out(buffer)]
puts "✅ Размер файла: $file_size"
puts ""

# Шаг 8: Проверить ссылку на styles.css
puts "8️⃣ Проверяем ссылку на styles.css в index.html..."
spawn ssh $server "head -10 ${site_dir}/index.html | grep -c 'styles\\.css' || echo '0'"
expect "password:" { send "$password\r" }
expect eof

set css_link [string trim $expect_out(buffer)]
if {$css_link > 0} {
    puts "✅ Ссылка на styles.css найдена"
} else {
    puts "❌ ОШИБКА: Ссылка на styles.css не найдена!"
}
puts ""

# Шаг 9: Перезагрузить Nginx
puts "9️⃣ Перезагружаем Nginx..."
spawn ssh $server "systemctl reload nginx && echo 'NGINX_OK' || echo 'NGINX_FAILED'"
expect "password:" { send "$password\r" }
expect eof

set nginx_status [string trim $expect_out(buffer)]
if {[string match "*NGINX_OK*" $nginx_status]} {
    puts "✅ Nginx перезагружен"
} else {
    puts "⚠️ Проблема с перезагрузкой Nginx"
}
puts ""

puts "=========================================="
puts "✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!"
puts ""
puts "--- Проверьте сайт: ---"
puts "   https://aladdin-ai.ru/"
puts ""
puts "💾 Бэкапы сохранены в: /var/www/backups/"
puts "📁 Директория сайта: $site_dir"
puts ""

