#!/usr/bin/expect -f

# Проверка всех доступных логов

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА ВСЕХ ДОСТУПНЫХ ЛОГОВ"
puts "=========================================="
puts ""

# 1. Payment Service логи
puts "1️⃣ Payment Service логи:"
spawn ssh $server "ls -lh /tmp/payment_service.log 2>&1 && tail -5 /tmp/payment_service.log 2>&1 | head -5"
expect "password:" { send "$password\r" }
expect eof

set payment_logs [string trim $expect_out(buffer)]
puts "$payment_logs"
puts ""

# 2. Nginx логи
puts "2️⃣ Nginx логи:"
spawn ssh $server "ls -lh /var/log/nginx/*.log 2>&1 | head -5"
expect "password:" { send "$password\r" }
expect eof

set nginx_logs [string trim $expect_out(buffer)]
puts "$nginx_logs"
puts ""

# 3. System логи
puts "3️⃣ System логи:"
spawn ssh $server "ls -lh /var/log/syslog 2>&1 && tail -5 /var/log/syslog 2>&1 | head -5"
expect "password:" { send "$password\r" }
expect eof

set system_logs [string trim $expect_out(buffer)]
puts "$system_logs"
puts ""

# 4. API Gateway логи
puts "4️⃣ API Gateway логи:"
spawn ssh $server "find /opt/aladdin-backend -name '*.log' -type f 2>&1 | head -10"
expect "password:" { send "$password\r" }
expect eof

set api_gateway_logs [string trim $expect_out(buffer)]
puts "$api_gateway_logs"
puts ""

# 5. База данных логи
puts "5️⃣ MySQL логи:"
spawn ssh $server "ls -lh /var/log/mysql/*.log 2>&1 | head -5 || echo 'MySQL logs not found in standard location'"
expect "password:" { send "$password\r" }
expect eof

set mysql_logs [string trim $expect_out(buffer)]
puts "$mysql_logs"
puts ""

# 6. PostgreSQL логи
puts "6️⃣ PostgreSQL логи:"
spawn ssh $server "ls -lh /var/log/postgresql/*.log 2>&1 | head -5 || echo 'PostgreSQL logs not found in standard location'"
expect "password:" { send "$password\r" }
expect eof

set postgres_logs [string trim $expect_out(buffer)]
puts "$postgres_logs"
puts ""

# 7. Auth логи (безопасность)
puts "7️⃣ Auth логи (безопасность):"
spawn ssh $server "ls -lh /var/log/auth.log 2>&1 && tail -5 /var/log/auth.log 2>&1 | head -5"
expect "password:" { send "$password\r" }
expect eof

set auth_logs [string trim $expect_out(buffer)]
puts "$auth_logs"
puts ""

# 8. Kernel логи
puts "8️⃣ Kernel логи:"
spawn ssh $server "ls -lh /var/log/kern.log 2>&1 && tail -5 /var/log/kern.log 2>&1 | head -5"
expect "password:" { send "$password\r" }
expect eof

set kernel_logs [string trim $expect_out(buffer)]
puts "$kernel_logs"
puts ""

# 9. Проверить journalctl (systemd логи)
puts "9️⃣ Systemd логи (journalctl):"
spawn ssh $server "journalctl --list-boots | head -3 2>&1"
expect "password:" { send "$password\r" }
expect eof

set journalctl_logs [string trim $expect_out(buffer)]
puts "$journalctl_logs"
puts ""

# 10. Проверить что доступно через API
puts "🔟 Что доступно через API админки:"
spawn ssh $server "echo 'Payment Service: /api/admin/logs?service=payment_service' && echo 'Nginx: /api/admin/logs?service=nginx' && echo 'System: /api/admin/logs?service=system'"
expect "password:" { send "$password\r" }
expect eof

set api_logs [string trim $expect_out(buffer)]
puts "$api_logs"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

