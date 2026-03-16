#!/bin/bash
# Скрипт для применения миграции и тестирования на сервере
# Использование: ./deploy_and_test.sh

set -e  # Остановка при ошибке

SERVER="149.154.65.180"
USER="root"
REMOTE_DIR="/opt/aladdin-backend"
LOCAL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "============================================================"
echo "РАЗВЕРТЫВАНИЕ МИГРАЦИИ И ТЕСТИРОВАНИЕ НА СЕРВЕРЕ"
echo "============================================================"
echo ""
echo "Сервер: $SERVER"
echo "Пользователь: $USER"
echo "Удаленная директория: $REMOTE_DIR"
echo ""

# Проверяем наличие необходимых файлов
echo "📋 Проверка файлов..."
if [ ! -f "$LOCAL_DIR/create_component_tables.sql" ]; then
    echo "❌ Файл create_component_tables.sql не найден!"
    exit 1
fi

if [ ! -f "$LOCAL_DIR/apply_migration.py" ]; then
    echo "❌ Файл apply_migration.py не найден!"
    exit 1
fi

if [ ! -f "$LOCAL_DIR/test_endpoints.py" ]; then
    echo "❌ Файл test_endpoints.py не найден!"
    exit 1
fi

echo "✅ Все файлы найдены"
echo ""

# Копируем файлы на сервер
echo "📤 Копирование файлов на сервер..."
scp "$LOCAL_DIR/create_component_tables.sql" "$USER@$SERVER:$REMOTE_DIR/app/database/migrations/"
scp "$LOCAL_DIR/apply_migration.py" "$USER@$SERVER:$REMOTE_DIR/app/database/migrations/"
scp "$LOCAL_DIR/test_endpoints.py" "$USER@$SERVER:$REMOTE_DIR/app/database/migrations/"
scp "$LOCAL_DIR/verify_endpoints.py" "$USER@$SERVER:$REMOTE_DIR/app/database/migrations/"

echo "✅ Файлы скопированы"
echo ""

# Применяем миграцию
echo "🔧 Применение миграции..."
ssh "$USER@$SERVER" "cd $REMOTE_DIR && python3 app/database/migrations/apply_migration.py"

if [ $? -eq 0 ]; then
    echo "✅ Миграция применена успешно"
else
    echo "❌ Ошибка применения миграции"
    exit 1
fi

echo ""

# Тестируем endpoints
echo "🧪 Тестирование endpoints..."
ssh "$USER@$SERVER" "cd $REMOTE_DIR && export API_BASE_URL='https://aladdin-ai.ru' && python3 app/database/migrations/test_endpoints.py"

if [ $? -eq 0 ]; then
    echo "✅ Тестирование завершено успешно"
else
    echo "⚠️ Тестирование завершено с предупреждениями"
fi

echo ""

# Проверяем соответствие документации
echo "📋 Проверка соответствия документации..."
ssh "$USER@$SERVER" "cd $REMOTE_DIR && python3 app/database/migrations/verify_endpoints.py"

if [ $? -eq 0 ]; then
    echo "✅ Все endpoints соответствуют документации"
else
    echo "⚠️ Обнаружены расхождения"
fi

echo ""
echo "============================================================"
echo "✅ РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО"
echo "============================================================"
