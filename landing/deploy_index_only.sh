#!/usr/bin/expect -f

# Скрипт для загрузки только index.html на сервер
# Использует expect для автоматического ввода пароля

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"
set remote_base "/var/www"
set backup_dir "/var/www/backups"

puts "🚀 Загружаем обновленный index.html на сервер..."
puts ""

# Шаг 1: Найти директорию сайта
puts "🔍 Ищем директорию сайта на сервере..."
spawn ssh $server "find $remote_base -name 'index.html' -path '*aladdin*' 2>/dev/null | head -1 | xargs dirname 2>/dev/null || echo '/var/www/html'"
expect "password:" { send "$password\r" }
expect eof

set site_dir [string trim $expect_out(buffer)]
set site_dir [regsub -all {\r|\n|^\s+|\s+$} $site_dir ""]

if {[string length $site_dir] < 5} {
    set site_dir "/var/www/html"
}

puts "✅ Найдена директория: $site_dir"
puts ""

# Шаг 2: Создать бэкап текущего index.html
puts "📦 Создаем бэкап текущего index.html..."
spawn ssh $server "mkdir -p $backup_dir && cp $site_dir/index.html $backup_dir/index.html.backup_before_remove_debug_\$(date +%Y%m%d_%H%M%S) 2>/dev/null && echo '✅ Бэкап создан' || echo '⚠️ Бэкап не создан'"
expect "password:" { send "$password\r" }
expect eof

# Шаг 3: Загрузить обновленный index.html
puts "📤 Загружаем обновленный index.html..."
spawn scp /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/index.html $server:$site_dir/
expect "password:" { send "$password\r" }
expect eof

# Шаг 4: Установить права доступа
puts "🔐 Устанавливаем права доступа..."
spawn ssh $server "chmod 644 $site_dir/index.html && chown www-data:www-data $site_dir/index.html 2>/dev/null || chown nginx:nginx $site_dir/index.html 2>/dev/null || chown apache:apache $site_dir/index.html 2>/dev/null || true"
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ Готово! index.html обновлен на сервере."
puts ""
puts "📋 Проверьте сайт: https://aladdin-ai.ru/"
puts "   Отладочные элементы должны быть удалены:"
puts "   ❌ Индикатор 'JS работает!' (верхний правый угол)"
puts "   ❌ Кнопка 'Диагностика' (нижний правый угол)"
puts "   ❌ Окно с логами"
puts ""
puts "💾 Бэкап сохранен в: $backup_dir"

