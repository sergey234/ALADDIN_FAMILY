#!/usr/bin/expect -f
# Правильное исправление main.py

set timeout 120
set password "Sergio675"
set server "root@149.154.65.180"

puts "🔧 ПРАВИЛЬНОЕ ИСПРАВЛЕНИЕ MAIN.PY"
puts ""

# Шаг 1: Проверка контекста вокруг строки 889
puts "📋 Шаг 1: Проверка контекста..."
spawn ssh $server "sed -n '880,900p' /opt/aladdin-backend/main.py"

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

# Шаг 2: Восстановление из backup
puts "📋 Шаг 2: Восстановление из backup..."
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

# Шаг 3: Правильная интеграция - найти последний include_router и добавить после него
puts "📋 Шаг 3: Правильная интеграция..."
spawn ssh $server "python3 << 'PYEOF'
from pathlib import Path
import re

main_py_path = Path('/opt/aladdin-backend/main.py')

with open(main_py_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Проверить есть ли уже
if 'ai_categories_router' in content:
    print('⚠️  Router уже импортирован!')
    exit(0)

# Добавить импорт после других импортов routers
import_pattern = r'(from\s+security\.api\.routers\.\w+\s+import\s+router[^\n]*)'
matches = list(re.finditer(import_pattern, content))

if matches:
    last_match = matches[-1]
    insert_pos = last_match.end()
    new_import = '\nfrom security.api.routers.ai_categories_router import router as ai_categories_router'
    content = content[:insert_pos] + new_import + content[insert_pos:]
    print('✅ Импорт добавлен')

# Найти последний include_router и добавить ПОСЛЕ него (не внутри try)
router_pattern = r'app\.include_router\([^)]+\)'
router_matches = list(re.finditer(router_pattern, content))

if router_matches:
    # Найти конец последнего include_router
    last_match = router_matches[-1]
    # Найти конец строки после include_router
    end_pos = content.find('\\n', last_match.end())
    if end_pos == -1:
        end_pos = len(content)
    else:
        end_pos += 1  # Включая символ новой строки
    
    # Проверить что после этого нет незавершенного try
    next_lines = content[end_pos:end_pos+200]
    if 'try:' in next_lines and 'except' not in next_lines[:100]:
        # Есть незавершенный try - добавим перед ним
        try_pos = content.find('try:', end_pos)
        if try_pos != -1:
            end_pos = try_pos
    
    new_router = '\n# Регистрация AI Categories Router\ntry:\n    app.include_router(ai_categories_router)\n    print(\"✅ AI Categories Router зарегистрирован\")\nexcept Exception as e:\n    print(f\"⚠️ Не удалось зарегистрировать AI Categories Router: {e}\")\n'
    content = content[:end_pos] + new_router + content[end_pos:]
    print('✅ Регистрация роутера добавлена')
else:
    print('⚠️  Не найдено место для регистрации')
    exit(1)

# Сохранить
with open(main_py_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ main.py обновлен')
PYEOF
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
puts "📋 Шаг 4: Проверка синтаксиса..."
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
