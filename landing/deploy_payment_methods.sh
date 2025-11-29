#!/bin/bash

# Скрипт для загрузки обновленных методов оплаты на сервер
# Использование: ./deploy_payment_methods.sh

set -e  # Остановить при ошибке

SERVER="root@149.154.65.180"
REMOTE_DIR="/var/www/aladdin-ai.ru"
BACKUP_DIR="/var/www/aladdin-ai.ru/backups"

echo "🚀 Начинаем загрузку обновленных методов оплаты..."

# 1. Создать бэкап на сервере
echo "📦 Создаем бэкап на сервере..."
ssh $SERVER "mkdir -p $BACKUP_DIR && \
  cp $REMOTE_DIR/index.html $BACKUP_DIR/index.html.backup_\$(date +%Y%m%d_%H%M%S) && \
  cp $REMOTE_DIR/cms/methods.json $BACKUP_DIR/methods.json.backup_\$(date +%Y%m%d_%H%M%S) && \
  echo '✅ Бэкап создан'"

# 2. Загрузить обновленные файлы
echo "📤 Загружаем обновленные файлы..."
scp landing/index.html $SERVER:$REMOTE_DIR/
scp landing/cms/methods.json $SERVER:$REMOTE_DIR/cms/

# 3. Установить права доступа
echo "🔐 Устанавливаем права доступа..."
ssh $SERVER "chmod 644 $REMOTE_DIR/index.html $REMOTE_DIR/cms/methods.json && \
  chown www-data:www-data $REMOTE_DIR/index.html $REMOTE_DIR/cms/methods.json 2>/dev/null || true"

echo "✅ Готово! Файлы загружены на сервер."
echo ""
echo "📋 Проверьте сайт: https://aladdin-ai.ru/"
echo "   Должно быть только 5 методов оплаты:"
echo "   1. QR / Система быстрых платежей"
echo "   2. SberPay"
echo "   3. Карта Сбербанк (Мир/Visa/Mastercard)"
echo "   4. Tinkoff Pay"
echo "   5. Оплата на карту через СБП"

