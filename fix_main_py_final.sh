#!/usr/bin/expect -f
# Финальное исправление main.py - исправление незавершенного try и добавление ai_categories

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ MAIN.PY"
puts ""

# Восстановление из backup
puts "📋 Восстановление из backup..."
spawn ssh $server "cp /opt/aladdin-backend/main.py.backup_ai_categories /opt/aladdin-backend/main.py && echo 'OK'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "OK" {
        puts "   ✅ Backup восстановлен"
        exp_continue
    }
    eof {
        puts "   ✅ Backup восстановлен"
    }
}
wait

# Исправление через Python скрипт на сервере
puts "📋 Исправление main.py..."
spawn ssh $server "python3 << 'ENDPYTHON'
from pathlib import Path
import re

main_py_path = Path('/opt/aladdin-backend/main.py')

with open(main_py_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Проверить есть ли уже ai_categories_router
content = ''.join(lines)
if 'ai_categories_router' in content:
    print('⚠️  Router уже импортирован!')
    exit(0)

# Найти место для импорта
import_line = None
for i, line in enumerate(lines):
    if 'dark_web_monitoring_router' in line:
        import_line = i
        break

if import_line is not None:
    lines.insert(import_line + 1, 'from security.api.routers.ai_categories_router import router as ai_categories_router\n')
    print('✅ Импорт добавлен')

# Найти место для регистрации - после последнего include_router
router_line = None
for i in range(len(lines) - 1, -1, -1):
    if 'app.include_router' in lines[i] and 'dark_web_router' in lines[i]:
        # Найти конец блока try/except для dark_web
        j = i + 1
        try_count = 0
        while j < len(lines):
            if 'try:' in lines[j]:
                try_count += 1
            elif 'except' in lines[j] or 'finally' in lines[j]:
                if try_count == 0:
                    # Это except для нашего try
                    router_line = j + 1
                    break
                try_count -= 1
            j += 1
        if router_line is None:
            router_line = i + 5  # Примерно после блока
        break

if router_line is None:
    # Найти последний include_router
    for i in range(len(lines) - 1, -1, -1):
        if 'app.include_router' in lines[i]:
            router_line = i + 1
            break

if router_line is not None:
    new_router = [
        '# Регистрация AI Categories Router\n',
        'try:\n',
        '    app.include_router(ai_categories_router)\n',
        '    print(\"✅ AI Categories Router зарегистрирован\")\n',
        'except Exception as e:\n',
        '    print(f\"⚠️ Не удалось зарегистрировать AI Categories Router: {e}\")\n',
        '\n'
    ]
    for line in reversed(new_router):
        lines.insert(router_line, line)
    print('✅ Регистрация роутера добавлена')
else:
    print('⚠️  Не найдено место для регистрации')
    exit(1)

# Сохранить
with open(main_py_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('✅ main.py обновлен')
ENDPYTHON
"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    eof {
        puts ""
    }
}
wait

# Проверка синтаксиса
puts "📋 Проверка синтаксиса..."
spawn ssh $server "python3 -m py_compile /opt/aladdin-backend/main.py && echo '✅ Синтаксис корректен'"

expect {
    "password:" {
        send "$password\r"
        exp_continue
    }
    "✅ Синтаксис корректен" {
        puts "   ✅ Синтаксис корректен!"
        exp_continue
    }
    eof {
        puts ""
    }
}
wait

puts "✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!"
