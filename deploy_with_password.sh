#!/usr/bin/expect -f
# 🚀 Автоматическая загрузка лендинга на сервер с паролем

set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"
set local_path "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/"
set remote_path "/var/www/aladdin-ai.ru/"

puts "🚀 Начинаю загрузку лендинга на сервер..."
puts "📦 Локальная директория: $local_path"
puts "🌐 Сервер: $server"
puts "📁 Путь на сервере: $remote_path"
puts ""

spawn rsync -avz --progress $local_path $server:$remote_path

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "Are you sure you want to continue connecting" {
        send "yes\r"
        exp_continue
    }
    eof {
        puts "\n✅ Загрузка завершена!"
    }
    timeout {
        puts "\n❌ Таймаут при загрузке"
        exit 1
    }
}

wait

puts "\n🔧 Теперь выполните на сервере:"
puts "   ssh $server"
puts "   chown -R www-data:www-data $remote_path"
puts "   find $remote_path -type d -exec chmod 755 {} \\;"
puts "   find $remote_path -type f -exec chmod 644 {} \\;"
puts "   systemctl reload nginx"


