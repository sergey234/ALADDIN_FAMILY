#!/usr/bin/expect -f
# Детальная проверка логов backend

set timeout 30
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ДЕТАЛЬНЫЕ ЛОГИ BACKEND"
puts "========================="
puts ""

spawn ssh $server "journalctl -u aladdin-backend -n 50 --no-pager"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
    }
}

wait
