#!/usr/bin/expect -f

set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 Проверяем banks.json на сервере..."
puts ""

spawn ssh $server "cat /var/www/aladdin-ai.ru/cms/banks.json | wc -l && echo '---' && cat /var/www/aladdin-ai.ru/cms/banks.json"
expect "password:" { send "$password\r" }
expect eof

