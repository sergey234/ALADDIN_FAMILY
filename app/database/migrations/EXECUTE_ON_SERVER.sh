#!/bin/bash
# Скрипт для выполнения на сервере
# Использование: После подключения к серверу выполнить этот скрипт
# ssh root@149.154.65.180
# cd /opt/aladdin-backend
# bash app/database/migrations/EXECUTE_ON_SERVER.sh

set -e  # Остановка при ошибке

echo "============================================================"
echo "ПРИМЕНЕНИЕ МИГРАЦИИ И ТЕСТИРОВАНИЕ НА СЕРВЕРЕ"
echo "============================================================"
echo ""
echo "Текущая директория: $(pwd)"
echo "Дата: $(date)"
echo ""

# Проверяем наличие файлов
echo "📋 Проверка файлов..."
MIGRATION_DIR="app/database/migrations"

if [ ! -f "$MIGRATION_DIR/create_component_tables.sql" ]; then
    echo "❌ Файл create_component_tables.sql не найден!"
    exit 1
fi

if [ ! -f "$MIGRATION_DIR/apply_migration.py" ]; then
    echo "❌ Файл apply_migration.py не найден!"
    exit 1
fi

if [ ! -f "$MIGRATION_DIR/test_endpoints.py" ]; then
    echo "❌ Файл test_endpoints.py не найден!"
    exit 1
fi

if [ ! -f "$MIGRATION_DIR/verify_endpoints.py" ]; then
    echo "❌ Файл verify_endpoints.py не найден!"
    exit 1
fi

echo "✅ Все файлы найдены"
echo ""

# ШАГ 1: Применение миграции
echo "============================================================"
echo "🔧 ШАГ 1: Применение миграции"
echo "============================================================"
echo ""

python3 "$MIGRATION_DIR/apply_migration.py"

MIGRATION_EXIT=$?
if [ $MIGRATION_EXIT -eq 0 ]; then
    echo ""
    echo "✅ Миграция применена успешно!"
else
    echo ""
    echo "❌ Ошибка применения миграции (код: $MIGRATION_EXIT)"
    exit 1
fi

echo ""
echo "============================================================"
echo "🧪 ШАГ 2: Тестирование endpoints"
echo "============================================================"
echo ""

export API_BASE_URL="https://aladdin-ai.ru"
python3 "$MIGRATION_DIR/test_endpoints.py"

TEST_EXIT=$?
if [ $TEST_EXIT -eq 0 ]; then
    echo ""
    echo "✅ Тестирование завершено успешно!"
else
    echo ""
    echo "⚠️ Тестирование завершено с предупреждениями (код: $TEST_EXIT)"
fi

echo ""
echo "============================================================"
echo "📋 ШАГ 3: Проверка соответствия документации"
echo "============================================================"
echo ""

python3 "$MIGRATION_DIR/verify_endpoints.py"

VERIFY_EXIT=$?
if [ $VERIFY_EXIT -eq 0 ]; then
    echo ""
    echo "✅ Все endpoints соответствуют документации!"
else
    echo ""
    echo "⚠️ Обнаружены расхождения (код: $VERIFY_EXIT)"
fi

echo ""
echo "============================================================"
echo "📊 ИТОГОВЫЙ РЕЗУЛЬТАТ"
echo "============================================================"
echo ""
echo "Миграция:        $([ $MIGRATION_EXIT -eq 0 ] && echo '✅ Успешно' || echo '❌ Ошибка')"
echo "Тестирование:    $([ $TEST_EXIT -eq 0 ] && echo '✅ Успешно' || echo '⚠️ Предупреждения')"
echo "Документация:    $([ $VERIFY_EXIT -eq 0 ] && echo '✅ Успешно' || echo '⚠️ Расхождения')"
echo ""

if [ $MIGRATION_EXIT -eq 0 ] && [ $TEST_EXIT -eq 0 ] && [ $VERIFY_EXIT -eq 0 ]; then
    echo "✅ ВСЕ ЗАДАЧИ ВЫПОЛНЕНЫ УСПЕШНО!"
    echo ""
    echo "Статус:"
    echo "  ✅ Миграция применена"
    echo "  ✅ Endpoints протестированы"
    echo "  ✅ Документация проверена"
    exit 0
else
    echo "⚠️ Некоторые задачи завершились с предупреждениями"
    echo ""
    echo "Проверьте логи выше для деталей"
    exit 1
fi
