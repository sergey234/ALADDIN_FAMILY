#!/bin/bash

# Скрипт для автоматической загрузки обновленных методов оплаты на сервер
# Пароль: Sergio675

set -e

SERVER="root@149.154.65.180"
PASSWORD="Sergio675"
REMOTE_BASE="/var/www"
BACKUP_DIR="/var/www/backups"

echo "🚀 Начинаем загрузку обновленных методов оплаты на сервер..."
echo ""

# Функция для выполнения SSH команд с паролем
ssh_with_password() {
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$@"
}

# Функция для загрузки файлов с паролем
scp_with_password() {
    sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$@"
}

# Проверяем, установлен ли sshpass
if ! command -v sshpass &> /dev/null; then
    echo "❌ sshpass не установлен. Устанавливаем..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install hudochenkov/sshpass/sshpass
        else
            echo "❌ Нужно установить Homebrew или sshpass вручную"
            echo "   brew install hudochenkov/sshpass/sshpass"
            exit 1
        fi
    else
        # Linux
        sudo apt-get update && sudo apt-get install -y sshpass
    fi
fi

# 1. Найти директорию сайта на сервере
echo "🔍 Ищем директорию сайта на сервере..."
SITE_DIR=$(ssh_with_password $SERVER "find $REMOTE_BASE -name 'index.html' -path '*aladdin*' 2>/dev/null | head -1 | xargs dirname 2>/dev/null || echo ''")

if [ -z "$SITE_DIR" ]; then
    echo "⚠️  Не найдена директория через поиск. Пробуем стандартные пути..."
    SITE_DIR=$(ssh_with_password $SERVER "ls -d $REMOTE_BASE/aladdin-ai.ru 2>/dev/null || ls -d $REMOTE_BASE/html 2>/dev/null || echo '/var/www/html'")
fi

echo "✅ Найдена директория: $SITE_DIR"
echo ""

# 2. Создать бэкап на сервере
echo "📦 Создаем бэкап на сервере..."
ssh_with_password $SERVER "mkdir -p $BACKUP_DIR && \
  mkdir -p $SITE_DIR/cms && \
  cp $SITE_DIR/index.html $BACKUP_DIR/index.html.backup_\$(date +%Y%m%d_%H%M%S) 2>/dev/null && \
  cp $SITE_DIR/cms/methods.json $BACKUP_DIR/methods.json.backup_\$(date +%Y%m%d_%H%M%S) 2>/dev/null || true && \
  echo '✅ Бэкап создан'"

# 3. Загрузить обновленные файлы
echo "📤 Загружаем обновленные файлы..."
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
scp_with_password landing/index.html $SERVER:$SITE_DIR/
scp_with_password landing/cms/methods.json $SERVER:$SITE_DIR/cms/

# 4. Установить права доступа
echo "🔐 Устанавливаем права доступа..."
ssh_with_password $SERVER "chmod 644 $SITE_DIR/index.html $SITE_DIR/cms/methods.json && \
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

