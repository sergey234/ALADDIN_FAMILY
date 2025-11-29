#!/usr/bin/expect -f
# ============================================
# АВТОМАТИЧЕСКАЯ ИНТЕГРАЦИЯ: Реферальная программа (с паролем)
# ============================================
# Использует expect для автоматизации SSH команд
# ============================================

set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"
set local_dir "/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS"
set python_project_path "/opt/aladdin-backend"
set web_root "/var/www/aladdin-ai.ru"

puts "=== 🚀 АВТОМАТИЧЕСКАЯ ИНТЕГРАЦИЯ РЕФЕРАЛЬНОЙ ПРОГРАММЫ ==="
puts ""

# ============================================
# ШАГ 1: Загрузка SQL скрипта
# ============================================

puts "📊 ШАГ 1: Загрузка SQL скрипта..."

spawn scp "${local_dir}/docs/server/REFERRAL_DB_SETUP.sql" "${server}:/tmp/REFERRAL_DB_SETUP.sql"
expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}

puts "✅ SQL скрипт загружен"
puts "⚠️  ВНИМАНИЕ: Нужно вручную выполнить SQL скрипт на сервере"
puts ""

# ============================================
# ШАГ 2: Загрузка Python файлов
# ============================================

puts "🐍 ШАГ 2: Загрузка Python файлов..."

# Создать директорию routers если её нет
spawn ssh $server "mkdir -p ${python_project_path}/app/routers"
expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "yes/no" {
        send "yes\r"
        exp_continue
    }
    eof
}

# Загрузить REFERRAL_API_ENDPOINTS.py
spawn scp "${local_dir}/docs/server/REFERRAL_API_ENDPOINTS.py" "${server}:${python_project_path}/app/routers/referral.py"
expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof
}
puts "  ✅ REFERRAL_API_ENDPOINTS.py загружен"

# Загрузить REFERRAL_PAYMENT_INTEGRATION.py
spawn scp "${local_dir}/docs/server/REFERRAL_PAYMENT_INTEGRATION.py" "${server}:${python_project_path}/app/referral_payment_integration.py"
expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof
}
puts "  ✅ REFERRAL_PAYMENT_INTEGRATION.py загружен"

# Загрузить REFERRAL_SERVER_IMPLEMENTATION.py
spawn scp "${local_dir}/docs/server/REFERRAL_SERVER_IMPLEMENTATION.py" "${server}:${python_project_path}/app/referral_implementation.py"
expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof
}
puts "  ✅ REFERRAL_SERVER_IMPLEMENTATION.py загружен"

puts "✅ Python файлы загружены"
puts ""

# ============================================
# ШАГ 3: Загрузка landing страницы
# ============================================

puts "🌐 ШАГ 3: Загрузка landing страницы..."

spawn scp "${local_dir}/landing/invite.html" "${server}:${web_root}/invite.html"
expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof
}

# Настроить права доступа
spawn ssh $server "chmod 644 ${web_root}/invite.html"
expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof
}

puts "✅ Landing страница загружена"
puts ""

# ============================================
# ШАГ 4: Загрузка Nginx конфигурации
# ============================================

puts "⚙️  ШАГ 4: Загрузка Nginx конфигурации..."

spawn scp "${local_dir}/docs/server/NGINX_CONFIG.conf" "${server}:/tmp/nginx_referral.conf"
expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof
}

puts "✅ Nginx конфигурация загружена"
puts ""

# ============================================
# ИТОГ
# ============================================

puts "=== ✅ АВТОМАТИЧЕСКАЯ ИНТЕГРАЦИЯ ЗАВЕРШЕНА ==="
puts ""
puts "📋 Что сделано автоматически:"
puts "  ✅ SQL скрипт загружен на сервер (/tmp/REFERRAL_DB_SETUP.sql)"
puts "  ✅ Python файлы загружены на сервер"
puts "  ✅ Landing страница загружена"
puts "  ✅ Nginx конфигурация загружена"
puts ""
puts "📋 Что нужно сделать вручную:"
puts "  1. Выполнить SQL скрипт:"
puts "     ssh $server"
puts "     psql -U ваш_пользователь -d ваша_база -f /tmp/REFERRAL_DB_SETUP.sql"
puts ""
puts "  2. Настроить Nginx:"
puts "     ssh $server"
puts "     nano /etc/nginx/sites-available/aladdin-ai.ru"
puts "     # Добавить блок location /invite/ из /tmp/nginx_referral.conf"
puts "     nginx -t"
puts "     systemctl reload nginx"
puts ""
puts "  3. Интегрировать функции в код оплаты (см. REFERRAL_INTEGRATION_GUIDE.md)"
puts ""
puts "  4. Перезапустить FastAPI приложение:"
puts "     systemctl restart aladdin-backend"
puts "     # или"
puts "     pm2 restart aladdin-backend"
puts ""
puts "📖 Подробные инструкции: docs/server/REFERRAL_INTEGRATION_GUIDE.md"


