#!/usr/bin/expect -f

# Скрипт для загрузки обновленного privacy.html с разделом Face ID на сервер
# Использует expect для автоматического ввода пароля

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"
set site_dir "/var/www/aladdin-ai.ru"

puts "🚀 Загрузка обновленного privacy.html на сервер..."
puts ""

# Шаг 1: Создать бэкап
puts "📦 Создаем бэкап..."
set timestamp [clock format [clock seconds] -format "%Y%m%d_%H%M%S"]
spawn ssh $server "mkdir -p /root/backups && cp $site_dir/privacy.html /root/backups/privacy.html.backup_$timestamp 2>/dev/null || true && echo '✅ Бэкап создан'"
expect "password:" { send "$password\r" }
expect eof

# Шаг 2: Загрузить privacy.html
puts "📤 Загружаем privacy.html..."
spawn scp /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/privacy.html $server:$site_dir/privacy.html
expect "password:" { send "$password\r" }
expect eof

# Шаг 3: Установить права доступа
puts "🔐 Устанавливаем права доступа..."
spawn ssh $server "chmod 644 $site_dir/privacy.html && chown www-data:www-data $site_dir/privacy.html 2>/dev/null || chown nginx:nginx $site_dir/privacy.html 2>/dev/null || true && echo '✅ Права установлены'"
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ Обновления загружены на сервер!"
puts "📋 Обновлено:"
puts "   - privacy.html (добавлен раздел 7 'Face ID (Распознавание лица)')"
puts ""
puts "🌐 Проверьте сайт: https://aladdin-ai.ru/privacy.html"
puts "   Должен быть раздел 7 'Face ID (Распознавание лица)'"
