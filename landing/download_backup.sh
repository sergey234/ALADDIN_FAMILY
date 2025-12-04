#!/usr/bin/expect -f

# Скачивание бэкапа с сервера

set timeout 300
set password "Sergio675"
set server "root@149.154.65.180"
set backup_file "site_backup_20251204_111443.tar.gz"
set backup_path "/root/backups/$backup_file"
set local_dir "./backups"

puts "📥 СКАЧИВАНИЕ БЭКАПА С СЕРВЕРА"
puts "=========================================="
puts ""

# 1. Создать локальную директорию
puts "1️⃣ Создаю локальную директорию..."
exec mkdir -p $local_dir

puts "✅ Директория создана: $local_dir"
puts ""

# 2. Скачать архив
puts "2️⃣ Скачиваю архив..."
spawn scp $server:$backup_path $local_dir/$backup_file
expect "password:" { send "$password\r" }
expect eof

puts "✅ Архив скачан: $local_dir/$backup_file"
puts ""

# 3. Скачать список файлов
puts "3️⃣ Скачиваю список файлов..."
spawn scp $server:/root/backups/site_backup_20251204_111443.files.txt $local_dir/
expect "password:" { send "$password\r" }
expect eof

puts "✅ Список файлов скачан"
puts ""

# 4. Проверить размер
puts "4️⃣ Проверяю размер файла..."
exec ls -lh $local_dir/$backup_file

puts ""
puts "=========================================="
puts "✅ БЭКАП СКАЧАН УСПЕШНО!"
puts ""
puts "📁 Расположение:"
puts "   $local_dir/$backup_file"
puts ""
puts "💡 Для распаковки:"
puts "   cd $local_dir && tar -xzf $backup_file"
puts ""

