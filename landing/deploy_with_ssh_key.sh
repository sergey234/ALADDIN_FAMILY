#!/bin/bash

# Скрипт для автоматической загрузки обновленных методов оплаты на сервер
# Использует SSH ключ (без пароля)
# Основан на ML_SYSTEM_SERVER_ACCESS_GUIDE.md

set -e  # Остановить при ошибке

SERVER="root@149.154.65.180"
SSH_KEY="$HOME/.ssh/aladdin_server"
REMOTE_BASE="/var/www"
BACKUP_DIR="/var/www/backups"

echo "🚀 Начинаем загрузку обновленных методов оплаты на сервер..."
echo ""

# Проверка SSH ключа
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ SSH ключ не найден: $SSH_KEY"
    echo "   Используем стандартный ключ или пароль"
    SSH_OPTIONS=""
else
    echo "✅ Используем SSH ключ: $SSH_KEY"
    SSH_OPTIONS="-i $SSH_KEY"
fi

# 1. Найти директорию сайта на сервере
echo "🔍 Ищем директорию сайта на сервере..."
SITE_DIR=$(ssh $SSH_OPTIONS $SERVER "find $REMOTE_BASE -name 'index.html' -path '*aladdin*' 2>/dev/null | head -1 | xargs dirname 2>/dev/null || echo ''")

if [ -z "$SITE_DIR" ]; then
    echo "⚠️  Не найдена директория через поиск. Пробуем стандартные пути..."
    SITE_DIR=$(ssh $SSH_OPTIONS $SERVER "ls -d $REMOTE_BASE/aladdin-ai.ru 2>/dev/null || ls -d $REMOTE_BASE/html 2>/dev/null || echo '/var/www/html'")
fi

if [ -z "$SITE_DIR" ] || [ "$SITE_DIR" = "" ]; then
    SITE_DIR="/var/www/html"
fi

echo "✅ Найдена директория: $SITE_DIR"
echo ""

# 2. Создать бэкап на сервере
echo "📦 Создаем бэкап на сервере..."
ssh $SSH_OPTIONS $SERVER "mkdir -p $BACKUP_DIR && \
  mkdir -p $SITE_DIR/cms && \
  cp $SITE_DIR/index.html $BACKUP_DIR/index.html.backup_\$(date +%Y%m%d_%H%M%S) 2>/dev/null && \
  cp $SITE_DIR/cms/methods.json $BACKUP_DIR/methods.json.backup_\$(date +%Y%m%d_%H%M%S) 2>/dev/null || true && \
  echo '✅ Бэкап создан'"

# 3. Загрузить обновленные файлы
echo "📤 Загружаем обновленные файлы..."
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

scp $SSH_OPTIONS landing/index.html $SERVER:$SITE_DIR/
scp $SSH_OPTIONS landing/cms/methods.json $SERVER:$SITE_DIR/cms/

# 4. Установить права доступа
echo "🔐 Устанавливаем права доступа..."
ssh $SSH_OPTIONS $SERVER "chmod 644 $SITE_DIR/index.html $SITE_DIR/cms/methods.json && \
  chown www-data:www-data $SITE_DIR/index.html $SITE_DIR/cms/methods.json 2>/dev/null || \
  chown nginx:nginx $SITE_DIR/index.html $SITE_DIR/cms/methods.json 2>/dev/null || \
  chown apache:apache $SITE_DIR/index.html $SITE_DIR/cms/methods.json 2>/dev/null || true"

echo ""
echo "✅ Готово! Файлы загружены на сервер."
echo ""
echo "📋 Проверьте сайт: https://aladdin-ai.ru/"
echo "   Должно быть только 5 методов оплаты:"
echo "   1. QR / Система быстрых платежей"
echo "   2. SberPay"
echo "   3. Карта Сбербанк (Мир/Visa/Mastercard)"
echo "   4. Tinkoff Pay"
echo "   5. Оплата на карту через СБП"
echo ""
echo "💾 Бэкапы сохранены в: $BACKUP_DIR"

