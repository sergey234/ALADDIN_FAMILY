#!/usr/bin/expect -f

# Скрипт для загрузки обновлений сайта на сервер
# Обновления: убраны "шифрования", "экономия батареи", обновлены банки

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"
set remote_base "/var/www"
set site_dir "/var/www/aladdin-ai.ru"

puts "🚀 Загрузка обновлений сайта на сервер..."
puts ""

# Шаг 1: Создать бэкап
puts "📦 Создаем бэкап..."
set timestamp [clock format [clock seconds] -format "%Y%m%d_%H%M%S"]
spawn ssh $server "mkdir -p /root/backups/site_updates_$timestamp && cp $site_dir/index.html /root/backups/site_updates_$timestamp/index.html.backup 2>/dev/null && cp -r $site_dir/cms /root/backups/site_updates_$timestamp/cms_backup 2>/dev/null || true && echo '✅ Бэкап создан'"
expect "password:" { send "$password\r" }
expect eof

# Шаг 2: Загрузить index.html
puts "📤 Загружаем index.html..."
spawn scp /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/index.html $server:$site_dir/
expect "password:" { send "$password\r" }
expect eof

# Шаг 3: Загрузить banks.json
puts "📤 Загружаем banks.json..."
spawn scp /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/cms/banks.json $server:$site_dir/cms/
expect "password:" { send "$password\r" }
expect eof

# Шаг 4: Установить права доступа
puts "🔐 Устанавливаем права доступа..."
spawn ssh $server "chmod 644 $site_dir/index.html $site_dir/cms/banks.json && chown www-data:www-data $site_dir/index.html $site_dir/cms/banks.json 2>/dev/null || chown nginx:nginx $site_dir/index.html $site_dir/cms/banks.json 2>/dev/null || true && echo '✅ Права установлены'"
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ Обновления загружены на сервер!"
puts "📋 Обновлено:"
puts "   - index.html (убраны 'шифрования', 'экономия батареи', обновлены банки)"
puts "   - cms/banks.json (обновлены способы оплаты для всех банков)"
puts ""
puts "🌐 Проверьте сайт: https://aladdin-ai.ru/"

