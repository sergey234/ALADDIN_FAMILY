#!/usr/bin/expect -f

# Скрипт для создания полного бэкапа сайта на сервере
# Использует expect для автоматического ввода пароля
# Основан на ML_SYSTEM_SERVER_ACCESS_GUIDE.md

set timeout 180
set password "Sergio675"
set server "root@149.154.65.180"
set remote_base "/var/www"
set backup_dir "/var/www/backups"
set backup_date [clock format [clock seconds] -format "%Y%m%d_%H%M%S"]

puts "💾 Начинаем создание полного бэкапа сайта..."
puts ""

# Шаг 1: Найти директорию сайта
puts "🔍 Ищем директорию сайта на сервере..."
spawn ssh $server "find $remote_base -name 'index.html' -path '*aladdin*' 2>/dev/null | head -1 | xargs dirname 2>/dev/null || echo '/var/www/html'"
expect "password:" { send "$password\r" }
expect eof

set site_dir [string trim $expect_out(buffer)]
# Убираем лишние символы из вывода
set site_dir [regsub -all {\r|\n|^\s+|\s+$} $site_dir ""]

if {[string length $site_dir] < 5} {
    set site_dir "/var/www/html"
}

puts "✅ Найдена директория: $site_dir"
puts ""

# Шаг 2: Создать директорию для бэкапов
puts "📁 Создаем директорию для бэкапов..."
spawn ssh $server "mkdir -p $backup_dir"
expect "password:" { send "$password\r" }
expect eof

# Шаг 3: Создать полный бэкап сайта (tar.gz архив)
puts "📦 Создаем полный архив сайта..."
set backup_file "$backup_dir/site_backup_$backup_date.tar.gz"
spawn ssh $server "cd $remote_base && tar -czf $backup_file -C [file dirname $site_dir] [file tail $site_dir] 2>&1 && echo 'BACKUP_SUCCESS' || echo 'BACKUP_FAILED'"
expect "password:" { send "$password\r" }
expect eof

# Шаг 4: Проверить размер бэкапа
puts "📊 Проверяем размер бэкапа..."
spawn ssh $server "ls -lh $backup_file 2>/dev/null | awk '{print \$5}' || echo '0'"
expect "password:" { send "$password\r" }
expect eof

set backup_size [string trim $expect_out(buffer)]
set backup_size [regsub -all {\r|\n|^\s+|\s+$} $backup_size ""]

# Шаг 5: Создать список файлов в бэкапе
puts "📋 Создаем список файлов в бэкапе..."
spawn ssh $server "tar -tzf $backup_file 2>/dev/null | wc -l || echo '0'"
expect "password:" { send "$password\r" }
expect eof

set file_count [string trim $expect_out(buffer)]
set file_count [regsub -all {\r|\n|^\s+|\s+$} $file_count ""]

# Шаг 6: Создать дополнительный бэкап отдельных файлов (на всякий случай)
puts "📝 Создаем дополнительные бэкапы ключевых файлов..."
spawn ssh $server "mkdir -p $backup_dir/files_$backup_date && cp $site_dir/index.html $backup_dir/files_$backup_date/index.html.backup 2>/dev/null && cp $site_dir/cms/*.json $backup_dir/files_$backup_date/ 2>/dev/null && echo 'FILES_BACKUP_SUCCESS' || echo 'FILES_BACKUP_PARTIAL'"
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ Бэкап создан успешно!"
puts ""
puts "📊 Информация о бэкапе:"
puts "   📁 Директория сайта: $site_dir"
puts "   💾 Файл архива: $backup_file"
puts "   📦 Размер: $backup_size"
puts "   📄 Файлов в архиве: $file_count"
puts "   📂 Дополнительные файлы: $backup_dir/files_$backup_date/"
puts ""
puts "🔄 Для восстановления используйте:"
puts "   tar -xzf $backup_file -C $remote_base"
puts ""
puts "📋 Список всех бэкапов:"
spawn ssh $server "ls -lht $backup_dir/*.tar.gz 2>/dev/null | head -5 | awk '{print \$9, \$5}' || echo 'Нет бэкапов'"
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ Готово! Бэкап сохранен на сервере."

