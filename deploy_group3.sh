#!/bin/bash

# Скрипт для развертывания Группы 3 на сервер
echo "🚀 ЗАГРУЗКА ГРУППЫ 3 НА СЕРВЕР"
echo "=================================="

SERVER="149.154.65.180"
USER="root"
SCRIPT_PATH="/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/migrate_group3.py"
REMOTE_PATH="/opt/aladdin-backend/"

echo "📤 Загружаем скрипт на сервер..."
scp "$SCRIPT_PATH" "$USER@$SERVER:$REMOTE_PATH"

if [ $? -eq 0 ]; then
    echo "✅ Скрипт загружен успешно"
    echo ""
    echo "🔧 Выполняем миграцию на сервере..."

    # Выполняем команды на сервере через SSH
    ssh "$USER@$SERVER" << EOF
cd /opt/aladdin-backend
echo "📍 Текущая директория: \$(pwd)"
echo "📄 Проверяем наличие скрипта..."
ls -la migrate_group3.py

echo ""
echo "🚀 Запускаем миграцию..."
python3 migrate_group3.py --apply

echo ""
echo "✅ МИГРАЦИЯ ГРУППЫ 3 ЗАВЕРШЕНА!"
EOF

    echo ""
    echo "🎉 РАЗВЕРТЫВАНИЕ ГРУППЫ 3 УСПЕШНО ЗАВЕРШЕНО!"

else
    echo "❌ Ошибка загрузки скрипта на сервер"
    exit 1
fi


