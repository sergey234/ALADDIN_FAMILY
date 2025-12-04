#!/usr/bin/expect -f

# Применение исправленной конфигурации Nginx

set timeout 300
set password "Sergio675"
set server "root@149.154.65.180"
set nginx_config_local "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/docs/server/NGINX_CONFIG_DASHBOARD.conf"
set nginx_config_remote "/etc/nginx/sites-available/aladdin-ai.ru"

puts "🔧 Применяем исправленную конфигурацию Nginx..."
puts ""

# Создать бэкап
puts "📦 Создаем бэкап..."
spawn ssh $server "cp $nginx_config_remote ${nginx_config_remote}.backup_fix && echo 'BACKUP_OK'"
expect "password:" { send "$password\r" }
expect eof

# Загрузить конфигурацию
puts "📤 Загружаем конфигурацию..."
spawn scp $nginx_config_local $server:$nginx_config_remote
expect "password:" { send "$password\r" }
expect eof

# Проверить конфигурацию
puts "🔍 Проверяем конфигурацию..."
spawn ssh $server "nginx -t 2>&1"
expect "password:" { send "$password\r" }
expect eof

set nginx_test [string trim $expect_out(buffer)]
if {[string match "*syntax is ok*" $nginx_test]} {
    puts "✅ Конфигурация валидна"
    
    # Перезагрузить
    puts "🔄 Перезагружаем Nginx..."
    spawn ssh $server "systemctl reload nginx && echo 'RELOAD_OK'"
    expect "password:" { send "$password\r" }
    expect eof
    
    puts "✅ Nginx перезагружен"
} else {
    puts "❌ Ошибка в конфигурации:"
    puts "$nginx_test"
    exit 1
}

puts ""
puts "✅ Готово! Конфигурация применена."

