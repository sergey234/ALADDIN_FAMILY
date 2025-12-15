#!/usr/bin/expect -f

# Скрипт для автоматической загрузки обновленного privacy.html с разделом Face ID на сервер
# Использует expect для автоматического ввода пароля

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"
set remote_base "/var/www"
set backup_dir "/var/www/backups"
set project_path "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS"

puts "🚀 Начинаем загрузку обновленного privacy.html на сервер..."
puts ""

# Шаг 1: Найти директорию сайта
puts "🔍 Ищем директорию сайта на сервере..."
spawn ssh $server "find $remote_base -name 'privacy.html' -path '*aladdin*' 2>/dev/null | head -1 | xargs dirname 2>/dev/null || find $remote_base -name 'index.html' -path '*aladdin*' 2>/dev/null | head -1 | xargs dirname 2>/dev/null || echo '/var/www/html'"
expect {
    "password:" { 
        send "$password\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}

set site_dir [string trim $expect_out(buffer)]
# Убрать лишние символы из вывода
regsub -all {\r|\n|password:|yes/no} $site_dir "" site_dir
set site_dir [string trim $site_dir]

if {[string length $site_dir] < 5} {
    set site_dir "/var/www/html"
}

puts "✅ Найдена директория: $site_dir"
puts ""

# Шаг 2: Создать бэкап
puts "📦 Создаем бэкап на сервере..."
spawn ssh $server "mkdir -p $backup_dir && cp $site_dir/privacy.html $backup_dir/privacy.html.backup_\$(date +%Y%m%d_%H%M%S) 2>/dev/null && echo '✅ Бэкап создан'"
expect {
    "password:" { 
        send "$password\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}

# Шаг 3: Загрузить privacy.html
puts "📤 Загружаем privacy.html..."
spawn scp $project_path/landing/privacy.html $server:$site_dir/privacy.html
expect {
    "password:" { 
        send "$password\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}

# Шаг 4: Установить права доступа
puts "🔐 Устанавливаем права доступа..."
spawn ssh $server "chmod 644 $site_dir/privacy.html && chown www-data:www-data $site_dir/privacy.html 2>/dev/null || chown nginx:nginx $site_dir/privacy.html 2>/dev/null || chown apache:apache $site_dir/privacy.html 2>/dev/null || true"
expect {
    "password:" { 
        send "$password\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}

puts ""
puts "✅ Готово! Файл privacy.html загружен на сервер."
puts ""
puts "📋 Проверьте сайт: https://aladdin-ai.ru/privacy.html"
puts "   Должен быть раздел 7 'Face ID (Распознавание лица)'"
puts ""
puts "💾 Бэкап сохранен в: $backup_dir"

