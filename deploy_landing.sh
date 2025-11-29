#!/bin/bash
# 🚀 Скрипт для загрузки лендинга на продакшн-сервер
# Использование: ./deploy_landing.sh

echo "🚀 Загрузка лендинга на продакшн-сервер"
echo "=========================================="
echo ""

LANDING_DIR="/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing"
SERVER="root@149.154.65.180"
SERVER_PATH="/var/www/aladdin-ai.ru"

echo "📦 Локальная директория: $LANDING_DIR"
echo "🌐 Сервер: $SERVER"
echo "📁 Путь на сервере: $SERVER_PATH"
echo ""
echo "📋 Файлы для загрузки:"
ls -lh "$LANDING_DIR"/*.html "$LANDING_DIR"/*.css 2>/dev/null | awk '{printf "   %-20s %6s\n", $9, $5}'
echo ""

echo "🔄 Выполняю rsync..."
echo "   (Введите пароль для root@149.154.65.180)"
echo ""

rsync -avz --progress \
  "$LANDING_DIR/" \
  "$SERVER:$SERVER_PATH/"

if [ $? -eq 0 ]; then
  echo ""
  echo "✅ Файлы успешно загружены!"
  echo ""
  echo "🔧 Теперь выполните на сервере (ssh $SERVER):"
  echo "   chown -R www-data:www-data $SERVER_PATH"
  echo "   find $SERVER_PATH -type d -exec chmod 755 {} \\;"
  echo "   find $SERVER_PATH -type f -exec chmod 644 {} \\;"
  echo "   systemctl reload nginx"
  echo ""
  echo "🌐 Проверьте лендинг: https://aladdin-ai.ru/"
else
  echo ""
  echo "❌ Ошибка при загрузке файлов!"
  exit 1
fi


