#!/usr/bin/expect -f

# Скрипт для обновления конфигурации Nginx с поддержкой dashboard
# Автоматизирует процесс обновления конфигурации на сервере

set timeout 300
# SECURITY: Never store passwords in the repository.
# Prefer SSH keys. If password auth is absolutely required, pass it via env var:
#   export ALADDIN_SSH_PASSWORD='...'
if {![info exists env(ALADDIN_SSH_PASSWORD)]} {
    puts "❌ SECURITY: ALADDIN_SSH_PASSWORD не задана. Настройте SSH-ключи (рекомендуется) и повторите."
    exit 1
}
set password $env(ALADDIN_SSH_PASSWORD)
set server "root@149.154.65.180"
set local_config "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/docs/server/NGINX_CONFIG_DASHBOARD.conf"
set remote_config "/etc/nginx/sites-available/aladdin-ai.ru"
set backup_config "/etc/nginx/sites-available/aladdin-ai.ru.backup_$(date +%Y%m%d_%H%M%S)"

puts "🚀 Начинаем обновление конфигурации Nginx для dashboard..."
puts ""

# Шаг 1: Создать бэкап текущей конфигурации
puts "📦 Создаем бэкап текущей конфигурации..."
spawn ssh $server "cp $remote_config $backup_config && echo 'BACKUP_SUCCESS' || echo 'BACKUP_FAILED'"
expect "password:" { send "$password\r" }
expect eof

set backup_result [string trim $expect_out(buffer)]
if {[string match "*BACKUP_SUCCESS*" $backup_result]} {
    puts "✅ Бэкап создан: $backup_config"
} else {
    puts "⚠️ Бэкап не создан (возможно, файл не существует - это нормально для первого раза)"
}
puts ""

# Шаг 2: Загрузить новую конфигурацию
puts "📤 Загружаем новую конфигурацию..."
spawn scp $local_config $server:$remote_config
expect "password:" { send "$password\r" }
expect eof

puts "✅ Конфигурация загружена"
puts ""

# Шаг 3: Проверить конфигурацию
puts "🔍 Проверяем конфигурацию Nginx..."
spawn ssh $server "nginx -t 2>&1"
expect "password:" { send "$password\r" }
expect eof

set nginx_test [string trim $expect_out(buffer)]
if {[string match "*syntax is ok*" $nginx_test] && [string match "*test is successful*" $nginx_test]} {
    puts "✅ Конфигурация валидна"
} else {
    puts "❌ Ошибка в конфигурации:"
    puts "$nginx_test"
    puts ""
    puts "⚠️ Конфигурация НЕ будет применена!"
    puts "💾 Бэкап сохранен в: $backup_config"
    puts "🔄 Для восстановления используйте:"
    puts "   cp $backup_config $remote_config"
    exit 1
}
puts ""

# Шаг 4: Перезагрузить Nginx
puts "🔄 Перезагружаем Nginx..."
spawn ssh $server "systemctl reload nginx && echo 'RELOAD_SUCCESS' || echo 'RELOAD_FAILED'"
expect "password:" { send "$password\r" }
expect eof

set reload_result [string trim $expect_out(buffer)]
if {[string match "*RELOAD_SUCCESS*" $reload_result]} {
    puts "✅ Nginx перезагружен"
} else {
    puts "❌ Ошибка при перезагрузке Nginx"
    puts "$reload_result"
    exit 1
}
puts ""

# Шаг 5: Проверить статус Nginx
puts "📊 Проверяем статус Nginx..."
spawn ssh $server "systemctl status nginx --no-pager | head -5"
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ Готово! Конфигурация Nginx обновлена."
puts ""
puts "--- Проверьте работу: ---"
puts "   https://aladdin-ai.ru/dashboard"
puts "   https://aladdin-ai.ru/api/dashboard/public/stats"
puts ""
puts "💾 Бэкап сохранен в: $backup_config"
puts ""

