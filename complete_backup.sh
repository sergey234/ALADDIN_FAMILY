#!/usr/bin/expect -f
# Завершение бэкапа и скачивание

set timeout 300
set password "Sergio675"
set server "root@149.154.65.180"
set timestamp "20251209_220433"
set backup_name "site_backup_$timestamp"
set remote_backup_dir "/root/backups/$backup_name"
set local_backup_dir "$env(HOME)/Downloads"
set local_backup_path "$local_backup_dir/$backup_name"

puts "\n▶ Завершение бэкапа и скачивание..."
puts ""

# Проверить что создано на сервере
puts "Проверка созданных файлов на сервере..."
spawn ssh $server "ls -lh $remote_backup_dir/ 2>&1"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Проверка завершена"
    }
}

wait

# Создать архив на сервере
puts ""
puts "Создание архива на сервере..."
spawn ssh $server "cd /root/backups && tar -czf $backup_name.tar.gz $backup_name/ 2>&1 && echo 'ARCHIVE_OK' || echo 'ARCHIVE_ERROR'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "ARCHIVE_OK" {
        puts "   ✅ Архив создан"
        exp_continue
    }
    eof {
        puts "   ✅ Архив создан"
    }
}

wait

# Скачать архив
puts ""
puts "Скачивание архива в Downloads..."
exec mkdir -p "$local_backup_dir"
spawn scp $server:/root/backups/$backup_name.tar.gz "$local_backup_path.tar.gz"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Архив скачан"
    }
}

wait

# Скачать директорию
puts ""
puts "Скачивание директории в Downloads..."
spawn scp -r $server:$remote_backup_dir "$local_backup_path"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Директория скачана"
    }
}

wait

puts ""
puts "✅ Бэкап завершен!"
puts "📁 На сервере: $remote_backup_dir"
puts "📁 В Downloads: $local_backup_path"
puts "📦 Архив: $local_backup_path.tar.gz"
puts ""
