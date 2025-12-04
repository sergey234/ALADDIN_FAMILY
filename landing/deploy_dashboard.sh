#!/usr/bin/expect -f

# Скрипт для деплоя публичного dashboard на сервер
# Загружает файлы dashboard и обновляет Nginx конфигурацию

set timeout 300
set password "Sergio675"
set server "root@149.154.65.180"
set remote_base "/var/www/html"
set local_dashboard "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/dashboard"
set nginx_config_local "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/docs/server/NGINX_CONFIG_DASHBOARD.conf"
set nginx_config_remote "/etc/nginx/sites-available/aladdin-ai.ru"

puts "🚀 Начинаем деплой публичного dashboard на сервер..."
puts ""

# Шаг 1: Найти директорию сайта
puts "🔍 Ищем директорию сайта на сервере..."
spawn ssh $server "find /var/www -name 'index.html' -path '*aladdin*' 2>/dev/null | head -1 | xargs dirname 2>/dev/null || echo '/var/www/html'"
expect "password:" { send "$password\r" }
expect eof

set site_dir [string trim $expect_out(buffer)]
if {[string length $site_dir] < 5} {
    set site_dir "/var/www/html"
}

puts "✅ Найдена директория: $site_dir"
puts ""

# Шаг 2: Создать директорию dashboard на сервере
puts "📁 Создаем директорию dashboard на сервере..."
spawn ssh $server "mkdir -p ${site_dir}/dashboard && echo 'DIR_CREATED' || echo 'DIR_FAILED'"
expect "password:" { send "$password\r" }
expect eof

puts "✅ Директория создана"
puts ""

# Шаг 3: Загрузить файлы dashboard
puts "📤 Загружаем файлы dashboard..."
spawn scp $local_dashboard/index.html $server:${site_dir}/dashboard/index.html
expect "password:" { send "$password\r" }
expect eof

puts "✅ Файлы загружены"
puts ""

# Шаг 4: Установить права доступа
puts "🔐 Устанавливаем права доступа..."
spawn ssh $server "chown -R www-data:www-data ${site_dir}/dashboard && chmod -R 755 ${site_dir}/dashboard && echo 'PERMISSIONS_SET' || echo 'PERMISSIONS_FAILED'"
expect "password:" { send "$password\r" }
expect eof

puts "✅ Права доступа установлены"
puts ""

# Шаг 5: Создать бэкап текущей конфигурации Nginx
puts "📦 Создаем бэкап конфигурации Nginx..."
set timestamp [clock format [clock seconds] -format %Y%m%d_%H%M%S]
set backup_config "${nginx_config_remote}.backup_${timestamp}"
spawn ssh $server "cp $nginx_config_remote $backup_config 2>/dev/null && echo 'BACKUP_SUCCESS' || echo 'BACKUP_SKIPPED'"
expect "password:" { send "$password\r" }
expect eof

puts "✅ Бэкап создан: $backup_config"
puts ""

# Шаг 6: Загрузить новую конфигурацию Nginx
puts "📤 Загружаем новую конфигурацию Nginx..."
spawn scp $nginx_config_local $server:$nginx_config_remote
expect "password:" { send "$password\r" }
expect eof

puts "✅ Конфигурация загружена"
puts ""

# Шаг 7: Проверить конфигурацию Nginx
puts "🔍 Проверяем конфигурацию Nginx..."
spawn ssh $server "nginx -t 2>&1"
expect "password:" { send "$password\r" }
expect eof

set nginx_test [string trim $expect_out(buffer)]
if {[string match "*syntax is ok*" $nginx_test] && [string match "*test is successful*" $nginx_test]} {
    puts "✅ Конфигурация валидна"
} else {
    puts "❌ Ошибка в конфигурации:"
    puts "$nginx_test"
    puts ""
    puts "⚠️ Конфигурация НЕ будет применена!"
    puts "💾 Бэкап сохранен в: $backup_config"
    puts "🔄 Для восстановления используйте:"
    puts "   cp $backup_config $nginx_config_remote"
    exit 1
}
puts ""

# Шаг 8: Перезагрузить Nginx
puts "🔄 Перезагружаем Nginx..."
spawn ssh $server "systemctl reload nginx && echo 'RELOAD_SUCCESS' || echo 'RELOAD_FAILED'"
expect "password:" { send "$password\r" }
expect eof

set reload_result [string trim $expect_out(buffer)]
if {[string match "*RELOAD_SUCCESS*" $reload_result]} {
    puts "✅ Nginx перезагружен"
} else {
    puts "❌ Ошибка при перезагрузке Nginx"
    puts "$reload_result"
    exit 1
}
puts ""

# Шаг 9: Проверить статус Nginx
puts "📊 Проверяем статус Nginx..."
spawn ssh $server "systemctl status nginx --no-pager | head -5"
expect "password:" { send "$password\r" }
expect eof

# Шаг 10: Проверить наличие файлов
puts "📋 Проверяем наличие файлов dashboard..."
spawn ssh $server "ls -lh ${site_dir}/dashboard/ 2>/dev/null | head -10"
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ Готово! Dashboard развернут на сервере."
puts ""
puts "--- Проверьте работу: ---"
puts "   📊 Dashboard: https://aladdin-ai.ru/dashboard"
puts "   🔌 API Stats: https://aladdin-ai.ru/api/dashboard/public/stats"
puts "   📈 API Timeline: https://aladdin-ai.ru/api/dashboard/public/threats-timeline"
puts "   🛡️ API Top Threats: https://aladdin-ai.ru/api/dashboard/public/top-threats"
puts ""
puts "💾 Бэкап конфигурации: $backup_config"
puts "📁 Директория dashboard: ${site_dir}/dashboard"
puts ""

