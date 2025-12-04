#!/usr/bin/expect -f

# Установка админ-ключа на сервере

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔑 УСТАНОВКА АДМИН-КЛЮЧА"
puts "=========================================="
puts ""
puts "Текущий ключ: ADMIN_SECRET_KEY_CHANGE_IN_PRODUCTION"
puts ""
puts "Введите новый админ-ключ (или нажмите Enter для использования текущего):"
puts ""

# Получить ключ от пользователя
set new_key "ADMIN_SECRET_KEY_CHANGE_IN_PRODUCTION"
# В expect нельзя легко получить ввод от пользователя, поэтому используем аргумент
if {[llength $argv] > 0} {
    set new_key [lindex $argv 0]
}

puts "Используемый ключ: $new_key"
puts ""

# 1. Создать/обновить .env файл
puts "1️⃣ Создаю/обновляю .env файл..."
spawn ssh $server "cd /opt/aladdin-backend && if [ -f .env ]; then grep -v '^PAYMENT_ADMIN_KEY=' .env > .env.tmp && mv .env.tmp .env; fi && echo 'PAYMENT_ADMIN_KEY=$new_key' >> .env && echo 'ENV_UPDATED'"
expect "password:" { send "$password\r" }
expect eof

set env_result [string trim $expect_out(buffer)]
puts "Результат: $env_result"
puts ""

# 2. Показать содержимое .env
puts "2️⃣ Проверяю содержимое .env..."
spawn ssh $server "cat /opt/aladdin-backend/.env 2>&1 | grep ADMIN_KEY || echo 'NOT_FOUND'"
expect "password:" { send "$password\r" }
expect eof

set env_content [string trim $expect_out(buffer)]
puts "Результат:"
puts "$env_content"
puts ""

# 3. Перезапустить payment_service
puts "3️⃣ Перезапускаю payment_service..."
spawn ssh $server "lsof -ti :8000 | xargs kill 2>&1; sleep 2; cd /opt/aladdin-backend && source venv/bin/activate && nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /dev/null 2>&1 & sleep 3 && echo 'SERVICE_RESTARTED'"
expect "password:" { send "$password\r" }
expect eof

set restart_result [string trim $expect_out(buffer)]
puts "Результат: $restart_result"
puts ""

puts "=========================================="
puts "✅ Ключ установлен!"
puts ""
puts "📝 Ваш админ-ключ: $new_key"
puts "💾 Сохраните его в безопасном месте!"
puts ""

