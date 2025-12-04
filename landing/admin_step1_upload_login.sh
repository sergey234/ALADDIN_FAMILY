#!/usr/bin/expect -f

# ШАГ 1: Создать директорию и загрузить login.html

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "📤 ШАГ 1: Создаю директорию и загружаю login.html..."
puts ""

# Создать директории
spawn ssh $server "mkdir -p /var/www/aladdin-ai.ru/admin/css /var/www/aladdin-ai.ru/admin/js && echo 'DIRECTORIES_CREATED'"
expect "password:" { send "$password\r" }
expect eof

set dir_result [string trim $expect_out(buffer)]
puts "Результат: $dir_result"
puts ""

# Загрузить login.html
spawn scp admin/login.html $server:/var/www/aladdin-ai.ru/admin/login.html
expect "password:" { send "$password\r" }
expect eof

puts ""
puts "✅ login.html загружен!"
puts ""

