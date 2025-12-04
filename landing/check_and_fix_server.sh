#!/usr/bin/expect -f

# Скрипт для проверки и исправления проблем на сервере

set timeout 300
set password "Sergio675"
set server "root@149.154.65.180"
set site_dir "/var/www/aladdin-ai.ru"

puts "🔍 Проверяем состояние сайта на сервере..."
puts ""

# Шаг 1: Проверить наличие отладочных элементов
puts "1️⃣ Проверяем наличие отладочных элементов в index.html..."
spawn ssh $server "grep -n 'debugIndicator\\|debugPanel\\|Диагностика\\|JS работает' ${site_dir}/index.html 2>/dev/null | head -10 || echo 'НЕ_НАЙДЕНО'"
expect "password:" { send "$password\r" }
expect eof

set debug_check [string trim $expect_out(buffer)]
puts "Результат: $debug_check"
puts ""

# Шаг 2: Проверить наличие styles.css
puts "2️⃣ Проверяем наличие styles.css..."
spawn ssh $server "ls -lh ${site_dir}/styles.css 2>&1"
expect "password:" { send "$password\r" }
expect eof

set css_check [string trim $expect_out(buffer)]
puts "Результат: $css_check"
puts ""

# Шаг 3: Проверить размер index.html
puts "3️⃣ Проверяем размер index.html..."
spawn ssh $server "ls -lh ${site_dir}/index.html | awk '{print \$5, \$9}'"
expect "password:" { send "$password\r" }
expect eof

set size_check [string trim $expect_out(buffer)]
puts "Результат: $size_check"
puts ""

# Шаг 4: Проверить ссылку на styles.css в index.html
puts "4️⃣ Проверяем ссылку на styles.css в index.html..."
spawn ssh $server "head -20 ${site_dir}/index.html | grep -E 'styles\\.css|link.*stylesheet'"
expect "password:" { send "$password\r" }
expect eof

set link_check [string trim $expect_out(buffer)]
puts "Результат: $link_check"
puts ""

# Шаг 5: Проверить права доступа
puts "5️⃣ Проверяем права доступа..."
spawn ssh $server "ls -la ${site_dir}/index.html ${site_dir}/styles.css 2>&1 | head -5"
expect "password:" { send "$password\r" }
expect eof

set perms_check [string trim $expect_out(buffer)]
puts "Результат: $perms_check"
puts ""

puts "✅ Проверка завершена!"
puts ""

