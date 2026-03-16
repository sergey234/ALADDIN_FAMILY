#!/bin/bash
# Скрипт для выполнения команд на удаленном сервере
# Использование: ./remote_execute.sh

SERVER="149.154.65.180"
USER="root"
REMOTE_DIR="/opt/aladdin-backend"

echo "============================================================"
echo "ВЫПОЛНЕНИЕ КОМАНД НА СЕРВЕРЕ: $SERVER"
echo "============================================================"
echo ""

# Команда 1: Применить миграцию
echo "🔧 ШАГ 1: Применение миграции..."
echo "----------------------------------------"
ssh "$USER@$SERVER" << 'ENDSSH'
cd /opt/aladdin-backend
echo "Текущая директория: $(pwd)"
echo "Проверка файла миграции..."
if [ -f "app/database/migrations/create_component_tables.sql" ]; then
    echo "✅ Файл миграции найден"
    echo "Применение миграции..."
    python3 app/database/migrations/apply_migration.py
else
    echo "❌ Файл миграции не найден!"
    exit 1
fi
ENDSSH

MIGRATION_EXIT=$?
if [ $MIGRATION_EXIT -eq 0 ]; then
    echo "✅ Миграция применена успешно"
else
    echo "❌ Ошибка применения миграции (код: $MIGRATION_EXIT)"
    exit 1
fi

echo ""
echo "============================================================"
echo "🧪 ШАГ 2: Тестирование endpoints..."
echo "============================================================"
echo ""

# Команда 2: Тестировать endpoints
ssh "$USER@$SERVER" << 'ENDSSH'
cd /opt/aladdin-backend
export API_BASE_URL="https://aladdin-ai.ru"
echo "Тестирование endpoints..."
python3 app/database/migrations/test_endpoints.py
ENDSSH

TEST_EXIT=$?
if [ $TEST_EXIT -eq 0 ]; then
    echo "✅ Тестирование завершено успешно"
else
    echo "⚠️ Тестирование завершено с предупреждениями (код: $TEST_EXIT)"
fi

echo ""
echo "============================================================"
echo "📋 ШАГ 3: Проверка соответствия документации..."
echo "============================================================"
echo ""

# Команда 3: Проверить соответствие документации
ssh "$USER@$SERVER" << 'ENDSSH'
cd /opt/aladdin-backend
echo "Проверка соответствия документации..."
python3 app/database/migrations/verify_endpoints.py
ENDSSH

VERIFY_EXIT=$?
if [ $VERIFY_EXIT -eq 0 ]; then
    echo "✅ Все endpoints соответствуют документации"
else
    echo "⚠️ Обнаружены расхождения (код: $VERIFY_EXIT)"
fi

echo ""
echo "============================================================"
echo "📊 ИТОГОВЫЙ РЕЗУЛЬТАТ"
echo "============================================================"
echo ""
echo "Миграция: $([ $MIGRATION_EXIT -eq 0 ] && echo '✅ Успешно' || echo '❌ Ошибка')"
echo "Тестирование: $([ $TEST_EXIT -eq 0 ] && echo '✅ Успешно' || echo '⚠️ Предупреждения')"
echo "Проверка документации: $([ $VERIFY_EXIT -eq 0 ] && echo '✅ Успешно' || echo '⚠️ Расхождения')"
echo ""

if [ $MIGRATION_EXIT -eq 0 ] && [ $TEST_EXIT -eq 0 ] && [ $VERIFY_EXIT -eq 0 ]; then
    echo "✅ ВСЕ ЗАДАЧИ ВЫПОЛНЕНЫ УСПЕШНО!"
    exit 0
else
    echo "⚠️ Некоторые задачи завершились с предупреждениями"
    exit 1
fi
