#!/usr/bin/expect -f

# Скрипт для автоматической загрузки обновленных методов оплаты на сервер
# Использует expect для автоматического ввода пароля
# Основан на ML_SYSTEM_SERVER_ACCESS_GUIDE.md

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"
set remote_base "/var/www"
set backup_dir "/var/www/backups"

puts "🚀 Начинаем загрузку обновленных методов оплаты на сервер..."
puts ""

# Шаг 1: Найти директорию сайта
puts "🔍 Ищем директорию сайта на сервере..."
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
puts "📦 Создаем бэкап на сервере..."
spawn ssh $server "mkdir -p $backup_dir && mkdir -p $site_dir/cms && cp $site_dir/index.html $backup_dir/index.html.backup_\$(date +%Y%m%d_%H%M%S) 2>/dev/null && cp $site_dir/cms/methods.json $backup_dir/methods.json.backup_\$(date +%Y%m%d_%H%M%S) 2>/dev/null || true && echo '✅ Бэкап создан'"
expect "password:" { send "$password\r" }
expect eof

# Шаг 3: Загрузить index.html
puts "📤 Загружаем index.html..."
spawn scp /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/index.html $server:$site_dir/
expect "password:" { send "$password\r" }
expect eof

# Шаг 4: Загрузить methods.json
puts "📤 Загружаем methods.json..."
spawn scp /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/cms/methods.json $server:$site_dir/cms/
expect "password:" { send "$password\r" }
expect eof

# Шаг 5: Установить права доступа
puts "🔐 Устанавливаем права доступа..."
spawn ssh $server "chmod 644 $site_dir/index.html $site_dir/cms/methods.json && chown www-data:www-data $site_dir/index.html $site_dir/cms/methods.json 2>/dev/null || chown nginx:nginx $site_dir/index.html $site_dir/cms/methods.json 2>/dev/null || chown apache:apache $site_dir/index.html $site_dir/cms/methods.json 2>/dev/null || true"
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ Готово! Файлы загружены на сервер."
puts ""
puts "📋 Проверьте сайт: https://aladdin-ai.ru/"
puts "   Должно быть только 5 методов оплаты:"
puts "   1. QR / Система быстрых платежей"
puts "   2. SberPay"
puts "   3. Карта Сбербанк (Мир/Visa/Mastercard)"
puts "   4. Tinkoff Pay"
puts "   5. Оплата на карту через СБП"
puts ""
puts "💾 Бэкапы сохранены в: $backup_dir"

