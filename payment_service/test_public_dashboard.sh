#!/usr/bin/expect -f

# Тестирование публичного dashboard /dashboard

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🧪 ТЕСТИРОВАНИЕ ПУБЛИЧНОГО DASHBOARD /dashboard"
puts "=========================================="
puts ""

# 1. Проверить доступность страницы /dashboard
puts "1️⃣ Проверяю доступность страницы /dashboard..."
spawn ssh $server "curl -s -o /dev/null -w 'HTTP %{http_code}' https://aladdin-ai.ru/dashboard/ 2>&1"
expect "password:" { send "$password\r" }
expect eof

set page_status [string trim $expect_out(buffer)]
puts "Результат: $page_status"
if {[string match "*200*" $page_status]} {
    puts "✅ Страница /dashboard доступна!"
} else {
    puts "❌ Страница /dashboard НЕ доступна!"
}
puts ""

# 2. Проверить наличие dashboard/index.html
puts "2️⃣ Проверяю наличие dashboard/index.html..."
spawn ssh $server "ls -lh /var/www/aladdin-ai.ru/dashboard/index.html 2>&1 || echo 'NOT_FOUND'"
expect "password:" { send "$password\r" }
expect eof

set dashboard_file [string trim $expect_out(buffer)]
puts "Результат:"
puts "$dashboard_file"
if {[string match "*NOT_FOUND*" $dashboard_file]} {
    puts "❌ Файл dashboard/index.html не найден!"
} else {
    puts "✅ Файл dashboard/index.html найден!"
}
puts ""

# 3. Проверить наличие вызова API в dashboard/index.html
puts "3️⃣ Проверяю наличие вызова API в dashboard/index.html..."
spawn ssh $server "grep -c 'api/dashboard/public/stats' /var/www/aladdin-ai.ru/dashboard/index.html 2>&1 || echo '0'"
expect "password:" { send "$password\r" }
expect eof

set api_call [string trim $expect_out(buffer)]
puts "Результат (API вызов): $api_call"
if {[string match "0" $api_call]} {
    puts "❌ Вызов API не найден!"
} else {
    puts "✅ Вызов API найден!"
}
puts ""

# 4. Проверить наличие Chart.js
puts "4️⃣ Проверяю наличие Chart.js в dashboard/index.html..."
spawn ssh $server "grep -c 'chart.js' /var/www/aladdin-ai.ru/dashboard/index.html 2>&1 || echo '0'"
expect "password:" { send "$password\r" }
expect eof

set chartjs [string trim $expect_out(buffer)]
puts "Результат (Chart.js): $chartjs"
if {[string match "0" $chartjs]} {
    puts "❌ Chart.js не найден!"
} else {
    puts "✅ Chart.js найден!"
}
puts ""

# 5. Проверить все dashboard endpoints
puts "5️⃣ Проверяю все dashboard endpoints..."
spawn ssh $server "curl -s -o /dev/null -w 'stats: %{http_code}, ' http://localhost:8000/api/dashboard/public/stats 2>&1 && curl -s -o /dev/null -w 'timeline: %{http_code}, ' http://localhost:8000/api/dashboard/public/threats-timeline 2>&1 && curl -s -o /dev/null -w 'top-threats: %{http_code}' http://localhost:8000/api/dashboard/public/top-threats 2>&1"
expect "password:" { send "$password\r" }
expect eof

set endpoints [string trim $expect_out(buffer)]
puts "Результат (endpoints): $endpoints"
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

