#!/usr/bin/expect -f
# Правильное добавление Location Bubble Router
set timeout 60
set password "Sergio675"
set server "root@149.154.65.180"

puts "=== ПРАВИЛЬНОЕ ДОБАВЛЕНИЕ LOCATION BUBBLE ROUTER ==="
puts ""

spawn ssh $server
expect {
    "password:" {
        send "$password\r"
        expect "# "
    }
}

send "cd /opt/aladdin-backend\r"
expect "# "

# Восстановление из backup
send "cp main.py.backup_20251213_160926 main.py\r"
expect "# "

# Добавление импорта
puts "1. Добавление импорта..."
send "sed -i '/from security.api.routers.crash_detection_router import router as crash_detection_router/a from security.api.routers.location_bubble_router import router as location_bubble_router' main.py\r"
expect "# "

# Добавление регистрации после последнего except блока
puts "2. Добавление регистрации router..."
send "sed -i '/except Exception as e:/a try:\n    app.include_router(location_bubble_router)\n    print(\"✅ Location Bubble Router зарегистрирован\")\nexcept Exception as e:\n    print(f\"⚠️ Не удалось зарегистрировать Location Bubble Router: {e}\")' main.py\r"
expect "# "

# Более простой способ - добавить после последнего except блока
send "python3 << 'PYEOF'\nimport re\n\nwith open('main.py', 'r') as f:\n    content = f.read()\n\n# Находим последний except блок для crash_detection\npattern = r'(except Exception as e:\\s*\\n\\s*print\\(f\"⚠️ Не удалось зарегистрировать Crash Detection Router: \\{e\\}\"\\)\\s*\\n)'\nmatch = re.search(pattern, content)\nif match:\n    insert_pos = match.end()\n    new_code = '''try:\n    app.include_router(location_bubble_router)\n    print(\"✅ Location Bubble Router зарегистрирован\")\nexcept Exception as e:\n    print(f\"⚠️ Не удалось зарегистрировать Location Bubble Router: {e}\")\n\n'''\n    content = content[:insert_pos] + new_code + content[insert_pos:]\n    with open('main.py', 'w') as f:\n        f.write(content)\n    print('✅ Router добавлен')\nelse:\n    print('❌ Не найдено место для вставки')\nPYEOF\r"
expect "# "

# Проверка синтаксиса
puts "3. Проверка синтаксиса..."
send "python3 -m py_compile main.py\r"
expect {
    "# " {
        puts "✅ Синтаксис корректен"
    }
    "SyntaxError" {
        puts "❌ Ошибка синтаксиса"
        send "cp main.py.backup_20251213_160926 main.py\r"
        expect "# "
    }
}

# Перезапуск
puts "4. Перезапуск сервиса..."
send "systemctl restart aladdin-backend\r"
expect "# "
sleep 3

# Health check
puts "5. Проверка health endpoint..."
send "curl -s http://localhost:8000/api/location/bubble/health | python3 -m json.tool\r"
expect "# "

puts ""
puts "✅ Готово!"
puts ""

send "exit\r"
expect eof
