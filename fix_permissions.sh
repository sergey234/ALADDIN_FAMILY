#!/usr/bin/expect -f
# 🔧 Настройка прав доступа на сервере

set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"
set remote_path "/var/www/aladdin-ai.ru"

puts "🔧 Настраиваю права доступа на сервере..."
puts ""

spawn ssh $server "chown -R www-data:www-data $remote_path && find $remote_path -type d -exec chmod 755 {} \\; && find $remote_path -type f -exec chmod 644 {} \\; && systemctl reload nginx && echo '✅ Права доступа настроены, Nginx перезагружен'"

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
        puts "\n✅ Готово!"
    }
    timeout {
        puts "\n❌ Таймаут"
        exit 1
    }
}

wait


