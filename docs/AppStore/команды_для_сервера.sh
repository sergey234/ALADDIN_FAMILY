#!/bin/bash
# Команды для выполнения на сервере после подключения
# Скопируйте и выполните эти команды на сервере

echo "=== НАСТРОЙКА РОУТИНГА /privacy И /terms ==="

# 1. Проверка файлов
echo ""
echo "1. Проверка файлов:"
ls -la /var/www/aladdin-ai.ru/privacy.html /var/www/aladdin-ai.ru/terms.html

# 2. Резервная копия
echo ""
echo "2. Создание резервной копии:"
sudo cp /etc/nginx/sites-available/aladdin-ai.ru /etc/nginx/sites-available/aladdin-ai.ru.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Резервная копия создана"

# 3. Просмотр текущего конфига (первые строки)
echo ""
echo "3. Текущий конфиг (первые 30 строк):"
sudo head -30 /etc/nginx/sites-available/aladdin-ai.ru

# 4. Проверка существующих location блоков
echo ""
echo "4. Проверка существующих location блоков:"
sudo grep -n "location" /etc/nginx/sites-available/aladdin-ai.ru | head -10

# 5. Добавление location блоков (автоматически)
echo ""
echo "5. Добавление location блоков..."

# Создаем временный файл с location блоками
cat > /tmp/nginx_locations.txt << 'LOCATIONS'
    # Редирект /privacy на privacy.html
    location = /privacy {
        return 301 /privacy.html;
    }

    # Редирект /terms на terms.html
    location = /terms {
        return 301 /terms.html;
    }

LOCATIONS

# Находим строку с "location / {" и добавляем перед ней
sudo python3 << 'PYTHON'
import re
import sys

config_file = '/etc/nginx/sites-available/aladdin-ai.ru'
locations_file = '/tmp/nginx_locations.txt'

# Читаем конфиг
with open(config_file, 'r') as f:
    content = f.read()

# Читаем location блоки для добавления
with open(locations_file, 'r') as f:
    locations = f.read()

# Проверяем что блоки еще не добавлены
if 'location = /privacy' in content:
    print("⚠️ Location блоки уже добавлены!")
    sys.exit(0)

# Находим "location / {" и добавляем перед ним
pattern = r'(\s+)(location\s+/\s*\{)'
replacement = locations + r'\1\2'

new_content = re.sub(pattern, replacement, content, count=1)

if new_content == content:
    print("⚠️ Не удалось найти место для вставки")
    print("Нужно добавить вручную перед 'location / {'")
    sys.exit(1)

# Сохраняем
with open(config_file, 'w') as f:
    f.write(new_content)

print("✅ Location блоки добавлены!")
PYTHON

# 6. Проверка синтаксиса
echo ""
echo "6. Проверка синтаксиса nginx:"
sudo nginx -t

# 7. Перезагрузка nginx
if [ $? -eq 0 ]; then
    echo ""
    echo "7. Перезагрузка nginx:"
    sudo systemctl reload nginx
    echo "✅ Nginx перезагружен"
else
    echo "❌ Ошибка в конфиге! Исправьте вручную"
    exit 1
fi

# 8. Проверка работы
echo ""
echo "8. Проверка работы:"
curl -I http://localhost/privacy 2>/dev/null | head -3
curl -I http://localhost/terms 2>/dev/null | head -3

echo ""
echo "=== ГОТОВО ==="
echo "Проверьте в браузере:"
echo "- https://aladdin-ai.ru/privacy"
echo "- https://aladdin-ai.ru/terms"
