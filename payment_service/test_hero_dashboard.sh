#!/usr/bin/expect -f

# Тестирование hero-блока dashboard на сайте

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🧪 ТЕСТИРОВАНИЕ HERO-БЛОКА DASHBOARD"
puts "=========================================="
puts ""

# 1. Проверить что API доступен
puts "1️⃣ Проверяю доступность API..."
spawn ssh $server "curl -s http://localhost:8000/api/dashboard/public/stats 2>&1 | head -5"
expect "password:" { send "$password\r" }
expect eof

set api_result [string trim $expect_out(buffer)]
puts "Результат (API):"
puts "$api_result"
puts ""

# 2. Проверить что сайт доступен
puts "2️⃣ Проверяю доступность сайта..."
spawn ssh $server "curl -s -o /dev/null -w 'HTTP %{http_code}' https://aladdin-ai.ru/ 2>&1"
expect "password:" { send "$password\r" }
expect eof

set site_result [string trim $expect_out(buffer)]
puts "Результат (сайт): $site_result"
puts ""

# 3. Проверить что в index.html есть dashboard код
puts "3️⃣ Проверяю наличие dashboard кода в index.html..."
spawn ssh $server "grep -c 'renderHeroStats' /var/www/aladdin-ai.ru/index.html 2>&1 || echo '0'"
expect "password:" { send "$password\r" }
expect eof

set hero_code [string trim $expect_out(buffer)]
puts "Результат (renderHeroStats): $hero_code"
if {[string match "0" $hero_code]} {
    puts "❌ Dashboard код не найден в index.html"
} else {
    puts "✅ Dashboard код найден в index.html"
}
puts ""

# 4. Проверить что есть вызов API
puts "4️⃣ Проверяю наличие вызова API в index.html..."
spawn ssh $server "grep -c 'api/dashboard/public/stats' /var/www/aladdin-ai.ru/index.html 2>&1 || echo '0'"
expect "password:" { send "$password\r" }
expect eof

set api_call [string trim $expect_out(buffer)]
puts "Результат (API вызов): $api_call"
if {[string match "0" $api_call]} {
    puts "❌ Вызов API не найден в index.html"
} else {
    puts "✅ Вызов API найден в index.html"
}
puts ""

puts "=========================================="
puts "✅ Проверка завершена!"
puts ""

