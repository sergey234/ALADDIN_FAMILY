#!/bin/bash
# Скрипт для настройки роутинга /privacy и /terms
# Использование: ./настроить_роутинг.sh

echo "=== НАСТРОЙКА РОУТИНГА ДЛЯ /privacy И /terms ==="
echo ""

# Подключение к серверу
echo "Подключение к серверу..."
ssh sergio675@149.154.65.180 << 'ENDSSH'

echo "=== ПРОВЕРКА ФАЙЛОВ ==="
ls -la /var/www/aladdin-ai.ru/privacy.html /var/www/aladdin-ai.ru/terms.html

echo ""
echo "=== СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ ==="
sudo cp /etc/nginx/sites-available/aladdin-ai.ru /etc/nginx/sites-available/aladdin-ai.ru.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Резервная копия создана"

echo ""
echo "=== ПРОВЕРКА ТЕКУЩЕГО КОНФИГА ==="
sudo grep -n "server {" /etc/nginx/sites-available/aladdin-ai.ru | head -3

echo ""
echo "=== ПРОВЕРКА СУЩЕСТВУЮЩИХ LOCATION БЛОКОВ ==="
sudo grep -n "location.*privacy\|location.*terms" /etc/nginx/sites-available/aladdin-ai.ru || echo "Location блоки для privacy/terms не найдены"

echo ""
echo "=== ИНСТРУКЦИЯ ==="
echo "Теперь нужно отредактировать конфиг:"
echo "1. sudo nano /etc/nginx/sites-available/aladdin-ai.ru"
echo "2. Найти блок server { ... }"
echo "3. Добавить ПЕРЕД location / { :"
echo ""
echo "   location = /privacy {"
echo "       return 301 /privacy.html;"
echo "   }"
echo ""
echo "   location = /terms {"
echo "       return 301 /terms.html;"
echo "   }"
echo ""
echo "4. Сохранить (Ctrl+O, Enter, Ctrl+X)"
echo "5. sudo nginx -t"
echo "6. sudo systemctl reload nginx"
echo "7. curl -I https://aladdin-ai.ru/privacy"

ENDSSH

echo ""
echo "=== ГОТОВО ==="
