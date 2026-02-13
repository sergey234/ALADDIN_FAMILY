#!/bin/bash
# 🚀 Скрипт для загрузки Components и System роутеров на сервер
# ✅ ЗАДАЧИ 21, 23: Автоматическая загрузка и подключение роутеров

set -e

SERVER="root@149.154.65.180"
PASSWORD="Sergio675"
BACKEND_PATH="/opt/aladdin-backend"
ROUTERS_PATH="$BACKEND_PATH/security/api/routers"

echo "🚀 НАЧАЛО ЗАГРУЗКИ РОУТЕРОВ"
echo "================================"

# Функция для выполнения команд через expect
run_ssh() {
    local command="$1"
    expect <<EOF
set timeout 120
spawn ssh -o StrictHostKeyChecking=no $SERVER "$command"
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    eof
}
EOF
}

# Функция для загрузки файла через SCP
upload_file() {
    local local_file="$1"
    local remote_file="$2"
    expect <<EOF
set timeout 120
spawn scp -o StrictHostKeyChecking=no "$local_file" $SERVER:"$remote_file"
expect {
    "password:" { send "$PASSWORD\r"; exp_continue }
    eof
}
EOF
}

# ШАГ 1: Создание резервных копий
echo ""
echo "📦 ШАГ 1: Создание резервных копий..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
run_ssh "cp $BACKEND_PATH/main.py $BACKEND_PATH/main.py.backup_$TIMESTAMP"
echo "✅ Резервная копия main.py создана: main.py.backup_$TIMESTAMP"

# ШАГ 2: Загрузка components_router.py
echo ""
echo "📤 ШАГ 2: Загрузка components_router.py..."
upload_file "components_router.py" "$ROUTERS_PATH/components_router.py"
echo "✅ components_router.py загружен"

# ШАГ 3: Загрузка system_router.py
echo ""
echo "📤 ШАГ 3: Загрузка system_router.py..."
upload_file "system_router.py" "$ROUTERS_PATH/system_router.py"
echo "✅ system_router.py загружен"

# ШАГ 4: Обновление main.py (добавление импортов и подключений)
echo ""
echo "📝 ШАГ 4: Обновление main.py..."

# Создаем временный скрипт для обновления main.py
cat > /tmp/update_main.py <<'PYTHON_SCRIPT'
import sys
import re

# Читаем main.py
with open('/opt/aladdin-backend/main.py', 'r') as f:
    content = f.read()

# Проверяем, есть ли уже импорты
if 'from security.api.routers.components_router import router as components_router' not in content:
    # Находим место после импорта ai_assistant_router
    pattern = r'(from security\.api\.routers\.ai_assistant_router import router as ai_assistant_router)'
    replacement = r'\1\n\n# ✅ ЗАДАЧА 21: Components Router\ntry:\n    from security.api.routers.components_router import router as components_router\n    components_router_available = True\nexcept ImportError as e:\n    print(f"⚠️ Components router not available: {e}")\n    components_router_available = False\n    components_router = None\n\n# ✅ ЗАДАЧА 23: System Router\ntry:\n    from security.api.routers.system_router import router as system_router\n    system_router_available = True\nexcept ImportError as e:\n    print(f"⚠️ System router not available: {e}")\n    system_router_available = False\n    system_router = None'
    content = re.sub(pattern, replacement, content)

# Проверяем, есть ли уже подключения
if 'app.include_router(components_router)' not in content:
    # Находим место после подключения ai_assistant_router
    pattern = r'(app\.include_router\(ai_assistant_router\))'
    replacement = r'\1\n\n# ✅ ЗАДАЧА 21: Подключение Components Router\nif components_router_available:\n    try:\n        app.include_router(components_router)\n        print("✅ Роутер Components подключен")\n    except Exception as e:\n        print(f"❌ Ошибка подключения Components: {e}")\n\n# ✅ ЗАДАЧА 23: Подключение System Router\nif system_router_available:\n    try:\n        app.include_router(system_router)\n        print("✅ Роутер System подключен")\n    except Exception as e:\n        print(f"❌ Ошибка подключения System: {e}")'
    content = re.sub(pattern, replacement, content)

# Записываем обновленный main.py
with open('/opt/aladdin-backend/main.py', 'w') as f:
    f.write(content)

print("✅ main.py обновлен")
PYTHON_SCRIPT

# Загружаем скрипт на сервер и выполняем
upload_file "/tmp/update_main.py" "/tmp/update_main.py"
run_ssh "python3 /tmp/update_main.py"
run_ssh "rm /tmp/update_main.py"
echo "✅ main.py обновлен"

# ШАГ 5: Проверка синтаксиса
echo ""
echo "🔍 ШАГ 5: Проверка синтаксиса..."
run_ssh "cd $BACKEND_PATH && python3 -m py_compile security/api/routers/components_router.py security/api/routers/system_router.py main.py"
echo "✅ Синтаксис проверен"

# ШАГ 6: Перезапуск сервера
echo ""
echo "🔄 ШАГ 6: Перезапуск сервера..."
run_ssh "systemctl restart aladdin-backend.service"
sleep 5
echo "✅ Сервер перезапущен"

# ШАГ 7: Проверка статуса
echo ""
echo "📊 ШАГ 7: Проверка статуса сервиса..."
run_ssh "systemctl status aladdin-backend.service | head -10"

# ШАГ 8: Тестирование endpoints
echo ""
echo "🧪 ШАГ 8: Тестирование endpoints..."
echo ""
echo "Тестирование Components endpoints:"
run_ssh "curl -s http://127.0.0.1:8000/api/components/health | head -5"
run_ssh "curl -s http://127.0.0.1:8000/api/components/list | head -5"
echo ""
echo "Тестирование System endpoints:"
run_ssh "curl -s http://127.0.0.1:8000/api/system/health | head -5"
run_ssh "curl -s http://127.0.0.1:8000/api/system/info | head -5"

echo ""
echo "✅ ВСЕ РОУТЕРЫ ЗАГРУЖЕНЫ И ПОДКЛЮЧЕНЫ!"
echo "================================"
