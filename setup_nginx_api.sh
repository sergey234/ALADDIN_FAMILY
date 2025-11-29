#!/usr/bin/expect -f
# 🔧 Настройка Nginx для проксирования /api/ на backend

set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"
set config_file "/etc/nginx/sites-available/aladdin-ai.ru"

puts "🔧 Настраиваю Nginx для проксирования API..."
puts ""

# Создаем backup конфигурации
spawn ssh $server "cp $config_file ${config_file}.backup_$(date +%Y%m%d_%H%M%S) && echo '✅ Backup создан'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {}
    timeout { exit 1 }
}
wait

# Проверяем текущую конфигурацию
puts "\n📋 Текущая конфигурация:"
spawn ssh $server "grep -A 5 'location /api' $config_file || echo '❌ location /api не найден'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {}
    timeout { exit 1 }
}
wait

puts "\n✅ Скрипт готов. Теперь нужно:"
puts "   1. Добавить location /api/ в конфигурацию Nginx"
puts "   2. Перезагрузить Nginx"
puts ""
puts "📝 См. инструкцию в: docs/BACKEND_ARCHITECTURE_EXPLANATION.md"


