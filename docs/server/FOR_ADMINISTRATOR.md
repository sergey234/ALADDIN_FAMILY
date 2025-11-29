# 📋 ИНСТРУКЦИЯ ДЛЯ АДМИНИСТРАТОРА: Развертывание реферальной программы

**Сервер:** 149.154.65.180  
**Сайт:** https://aladdin-ai.ru/  
**Дата:** 21 ноября 2024

---

## 🎯 ЗАДАЧА

Развернуть реферальную программу на сервере. Все файлы готовы, нужно только выполнить команды.

---

## 📁 ФАЙЛЫ ДЛЯ РАЗВЕРТЫВАНИЯ

Все файлы находятся в архиве `referral_deployment_files.tar.gz`:

1. **REFERRAL_DB_SETUP.sql** - SQL скрипт для создания таблиц
2. **REFERRAL_API_ENDPOINTS.py** - Python код для API endpoints
3. **REFERRAL_LANDING_PAGE.html** - HTML страница для реферальных ссылок
4. **REFERRAL_REGISTRATION_HANDLER.py** - Обработка регистрации
5. **REFERRAL_PAYMENT_HANDLER.py** - Обработка оплаты
6. **NGINX_CONFIG.conf** - Конфигурация Nginx
7. **AUTO_BACKUP.sh** - Скрипт создания backup'ов
8. **README.md** - Детальные инструкции

---

## 🛡️ ШАГ 1: СОЗДАТЬ BACKUP'Ы (ОБЯЗАТЕЛЬНО!)

```bash
# 1. Распаковать архив
tar -xzf referral_deployment_files.tar.gz
cd referral_deployment_files

# 2. Создать backup'ы
chmod +x AUTO_BACKUP.sh
./AUTO_BACKUP.sh

# Или вручную:
# - Backup БД: pg_dump -h localhost -U user -d database > backup.sql
# - Backup Nginx: cp /etc/nginx/sites-available/aladdin-ai.ru /etc/nginx/sites-available/aladdin-ai.ru.backup
# - Backup проекта: git tag backup-$(date +%Y%m%d)
```

---

## 🗄️ ШАГ 2: БАЗА ДАННЫХ

```bash
# Выполнить SQL скрипт
psql -h localhost -U your_user -d your_database -f REFERRAL_DB_SETUP.sql

# Проверить что таблицы созданы
psql -h localhost -U your_user -d your_database -c "\dt referral*"
```

**Ожидаемый результат:** Должны появиться таблицы `referral_codes` и `referrals`

---

## 🐍 ШАГ 3: PYTHON КОД

```bash
# 1. Скопировать API endpoints в проект
cp REFERRAL_API_ENDPOINTS.py /path/to/fastapi/project/app/routers/

# 2. Настроить импорты в файле (раскомментировать и настроить)
# 3. Добавить роутер в main.py:
#    from app.routers import referral_api
#    app.include_router(referral_api.router)

# 4. Интегрировать обработчики регистрации и оплаты
#    (см. REFERRAL_REGISTRATION_HANDLER.py и REFERRAL_PAYMENT_HANDLER.py)
```

---

## 🌐 ШАГ 4: LANDING СТРАНИЦА

```bash
# Разместить HTML файл
cp REFERRAL_LANDING_PAGE.html /path/to/fastapi/project/templates/referral_landing.html

# Настроить роутинг в FastAPI (см. README.md)
```

---

## ⚙️ ШАГ 5: NGINX

```bash
# 1. Создать backup текущей конфигурации
sudo cp /etc/nginx/sites-available/aladdin-ai.ru /etc/nginx/sites-available/aladdin-ai.ru.backup

# 2. Применить новую конфигурацию (или добавить в существующую)
#    См. NGINX_CONFIG.conf для примера

# 3. Проверить конфигурацию
sudo nginx -t

# 4. Перезагрузить Nginx
sudo systemctl reload nginx
```

---

## ✅ ШАГ 6: ПРОВЕРКА

```bash
# 1. Проверить API endpoints
curl -X GET "https://aladdin-ai.ru/api/referral/code" -H "Authorization: Bearer TOKEN"

# 2. Проверить landing страницу
curl "https://aladdin-ai.ru/invite/TEST123"

# 3. Проверить таблицы в БД
psql -h localhost -U user -d database -c "SELECT * FROM referral_codes LIMIT 1;"
```

---

## 📋 ДЕТАЛЬНЫЕ ИНСТРУКЦИИ

См. файл `README.md` для детальных инструкций по каждому шагу.

---

## 🔄 ОТКАТ (если что-то пошло не так)

```bash
# Восстановить БД
psql -h localhost -U user -d database < backup.sql

# Восстановить Nginx
sudo cp /etc/nginx/sites-available/aladdin-ai.ru.backup /etc/nginx/sites-available/aladdin-ai.ru
sudo nginx -t && sudo systemctl reload nginx

# Восстановить проект (Git)
cd /path/to/project
git checkout backup-YYYYMMDD
```

---

## ❓ ВОПРОСЫ?

Все инструкции находятся в файлах:
- `README.md` - детальные инструкции
- `QUICK_START.md` - быстрый старт
- `REFERRAL_TESTING_CHECKLIST.md` - чеклист тестирования

---

**Время выполнения:** 30-60 минут  
**Сложность:** Средняя  
**Риски:** Низкие (если созданы backup'ы)


