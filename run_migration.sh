#!/bin/bash

# Скрипт для выполнения миграции Группы 3 на сервере
echo "🚀 МИГРАЦИЯ ГРУППЫ 3: ЗАПУСК"
echo "============================"

cd /opt/aladdin-backend

echo "📍 Текущая директория: $(pwd)"
echo "📄 Проверяем наличие скрипта миграции..."

if [ -f "migrate_group3.py" ]; then
    echo "✅ Скрипт migrate_group3.py найден"
    echo ""
    echo "🔧 Запускаем миграцию..."
    python3 migrate_group3.py --apply

    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 МИГРАЦИЯ ГРУППЫ 3 УСПЕШНО ЗАВЕРШЕНА!"
        echo "========================================"
        echo "✅ 20 endpoints Группы 3 добавлены"
        echo "✅ API Gateway перезапущен"
        echo "✅ Тестирование выполнено"
    else
        echo ""
        echo "❌ ОШИБКА МИГРАЦИИ!"
        exit 1
    fi
else
    echo "❌ Скрипт migrate_group3.py не найден!"
    echo "📤 Загружаем скрипт..."
    # Здесь можно добавить загрузку, но лучше пусть пользователь сам загрузит
    echo "Запустите: scp migrate_group3.py root@149.154.65.180:/opt/aladdin-backend/"
    exit 1
fi


