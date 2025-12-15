#!/bin/bash
# Команды для настройки роутинга /privacy и /terms на сервере
# Сервер: 149.154.65.180
# Дата: 11 декабря 2025

echo "=== НАСТРОЙКА РОУТИНГА ДЛЯ /privacy И /terms ==="
echo ""

# ШАГ 1: Подключение к серверу
echo "ШАГ 1: Подключитесь к серверу:"
echo "ssh root@149.154.65.180"
echo ""

# ШАГ 2: Проверка существования файлов
echo "ШАГ 2: Проверьте что файлы существуют:"
echo "ls -la /var/www/aladdin-ai.ru/privacy.html"
echo "ls -la /var/www/aladdin-ai.ru/terms.html"
echo ""

# ШАГ 3: Резервная копия конфига
echo "ШАГ 3: Создайте резервную копию конфига:"
echo "cp /etc/nginx/sites-available/aladdin-ai.ru /etc/nginx/sites-available/aladdin-ai.ru.backup.$(date +%Y%m%d_%H%M%S)"
echo ""

# ШАГ 4: Редактирование конфига
echo "ШАГ 4: Откройте конфиг для редактирования:"
echo "nano /etc/nginx/sites-available/aladdin-ai.ru"
echo ""
echo "Или используйте vi:"
echo "vi /etc/nginx/sites-available/aladdin-ai.ru"
echo ""

# ШАГ 5: Добавить location блоки
echo "ШАГ 5: Добавьте следующие location блоки в server {} секцию:"
echo ""
echo "location = /privacy {"
echo "    return 301 /privacy.html;"
echo "}"
echo ""
echo "location = /terms {"
echo "    return 301 /terms.html;"
echo "}"
echo ""

# ШАГ 6: Проверка конфига
echo "ШАГ 6: Проверьте конфиг nginx:"
echo "nginx -t"
echo ""

# ШАГ 7: Перезагрузка nginx
echo "ШАГ 7: Если проверка успешна, перезагрузите nginx:"
echo "systemctl reload nginx"
echo ""

# ШАГ 8: Проверка работы
echo "ШАГ 8: Проверьте что роутинг работает:"
echo "curl -I https://aladdin-ai.ru/privacy"
echo "curl -I https://aladdin-ai.ru/terms"
echo ""

echo "=== ГОТОВО ==="
