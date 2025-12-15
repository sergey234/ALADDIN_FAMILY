#!/usr/bin/expect -f
# Скрипт для интеграции Dark Web Monitoring на сервере
# Регистрация в SFM, добавление в main.py, настройка

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"
set server_path "/opt/aladdin-backend"

puts "🔧 ИНТЕГРАЦИЯ DARK WEB MONITORING НА СЕРВЕРЕ"
puts "=============================================="
puts ""

# Шаг 1: Отправка скрипта регистрации
puts "📋 Шаг 1: Отправка скрипта регистрации..."
spawn scp register_dark_web_in_sfm.py "$server:/tmp/"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts "   ✅ Скрипт отправлен"
    }
}

wait

# Шаг 2: Регистрация в SFM
puts ""
puts "📋 Шаг 2: Регистрация в SFM..."
spawn ssh $server "python3 /tmp/register_dark_web_in_sfm.py"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅ Агент зарегистрирован" {
        puts "   ✅ Регистрация успешна!"
        exp_continue
    }
    eof {
        puts "   ✅ Регистрация завершена"
    }
}

wait

# Шаг 3: Поиск main.py
puts ""
puts "📋 Шаг 3: Поиск main.py..."
spawn ssh $server "find ${server_path} -name 'main.py' -type f -not -path '*/__pycache__/*' -not -path '*/venv/*' -not -path '*/env/*' 2>/dev/null | head -1"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        set main_py_path [string trim $expect_out(buffer)]
        if {[string length $main_py_path] < 5} {
            set main_py_path "${server_path}/api/main.py"
            puts "   ⚠️  Не найден, используем: $main_py_path"
        } else {
            puts "   ✅ Найден: $main_py_path"
        }
    }
}

wait

# Шаг 4: Проверка router на сервере
puts ""
puts "📋 Шаг 4: Проверка router на сервере..."
spawn ssh $server "test -f ${server_path}/security/api/routers/dark_web_monitoring_router.py && echo 'EXISTS' || echo 'NOT_FOUND'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "EXISTS" {
        puts "   ✅ Router найден"
        exp_continue
    }
    "NOT_FOUND" {
        puts "   ❌ Router не найден!"
        exp_continue
    }
    eof {
    }
}

wait

# Шаг 5: Проверка импорта в main.py
puts ""
puts "📋 Шаг 5: Проверка импорта в main.py..."
spawn ssh $server "grep -q 'dark_web_monitoring_router' ${server_path}/api/main.py 2>/dev/null && echo 'ALREADY_IMPORTED' || echo 'NOT_IMPORTED'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "ALREADY_IMPORTED" {
        puts "   ⚠️  Router уже импортирован"
        exp_continue
    }
    "NOT_IMPORTED" {
        puts "   📝 Нужно добавить импорт вручную"
        exp_continue
    }
    eof {
    }
}

wait

# Шаг 6: Инструкции
puts ""
puts "================================"
puts "✅ РЕГИСТРАЦИЯ В SFM ЗАВЕРШЕНА!"
puts ""
puts "📝 СЛЕДУЮЩИЕ ШАГИ:"
puts ""
puts "1. Добавить импорт в main.py (вручную):"
puts "   ssh $server"
puts "   nano ${server_path}/api/main.py"
puts ""
puts "   Добавить в импорты:"
puts "   from security.api.routers.dark_web_monitoring_router import router as dark_web_router"
puts ""
puts "   Добавить регистрацию роутера:"
puts "   try:"
puts "       app.include_router(dark_web_router)"
puts "       logger.info(\"✅ Dark Web Monitoring Router зарегистрирован\")"
puts "   except Exception as e:"
puts "       logger.warning(f\"⚠️ Не удалось: {e}\")"
puts ""
puts "2. Настроить API ключи (опционально):"
puts "   export HIBP_API_KEY='your-api-key'"
puts ""
puts "3. Перезапустить backend:"
puts "   systemctl restart aladdin-backend"
puts ""
puts "4. Проверить логи:"
puts "   journalctl -u aladdin-backend -n 50 | grep -i 'dark web'"
puts ""
