#!/usr/bin/expect -f

# Проверка и исправление пустых логов

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔍 ПРОВЕРКА И ИСПРАВЛЕНИЕ ПУСТЫХ ЛОГОВ"
puts "=========================================="
puts ""

# 1. Проверить MySQL логи
puts "1️⃣ Проверяю MySQL логи..."
spawn ssh $server "ls -lh /var/log/mysql/error.log 2>&1 && tail -5 /var/log/mysql/error.log 2>&1"
expect "password:" { send "$password\r" }
expect eof

set mysql_check [string trim $expect_out(buffer)]
puts "$mysql_check"
puts ""

# 2. Проверить PostgreSQL логи
puts "2️⃣ Проверяю PostgreSQL логи..."
spawn ssh $server "ls -lh /var/log/postgresql/postgresql-16-main.log 2>&1 && tail -5 /var/log/postgresql/postgresql-16-main.log 2>&1"
expect "password:" { send "$password\r" }
expect eof

set postgres_check [string trim $expect_out(buffer)]
puts "$postgres_check"
puts ""

# 3. Проверить auth.log
puts "3️⃣ Проверяю auth.log..."
spawn ssh $server "ls -lh /var/log/auth.log 2>&1 || echo 'FILE_NOT_FOUND'"
expect "password:" { send "$password\r" }
expect eof

set auth_check [string trim $expect_out(buffer)]
puts "$auth_check"
puts ""

# 4. Проверить journalctl для MySQL
puts "4️⃣ Проверяю journalctl для MySQL..."
spawn ssh $server "journalctl -u mysql -n 5 --no-pager 2>&1 | head -10"
expect "password:" { send "$password\r" }
expect eof

set mysql_journal [string trim $expect_out(buffer)]
puts "$mysql_journal"
puts ""

# 5. Проверить journalctl для PostgreSQL
puts "5️⃣ Проверяю journalctl для PostgreSQL..."
spawn ssh $server "journalctl -u postgresql -n 5 --no-pager 2>&1 | head -10"
expect "password:" { send "$password\r" }
expect eof

set postgres_journal [string trim $expect_out(buffer)]
puts "$postgres_journal"
puts ""

# 6. Проверить journalctl для SSH
puts "6️⃣ Проверяю journalctl для SSH..."
spawn ssh $server "journalctl _COMM=sshd -n 5 --no-pager 2>&1 | head -10"
expect "password:" { send "$password\r" }
expect eof

set ssh_journal [string trim $expect_out(buffer)]
puts "$ssh_journal"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

