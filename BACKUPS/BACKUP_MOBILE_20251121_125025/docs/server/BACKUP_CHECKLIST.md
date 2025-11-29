# 📋 ЧТО СОХРАНИТЬ: Детальный список файлов

**Дата:** 21 ноября 2024  
**Важно:** Сохраните эти файлы ПЕРЕД развертыванием!

---

## 🔴 КРИТИЧНО: Обязательно сохранить

### 1. База данных (КРИТИЧНО!)

**Что сохранить:**
- Вся база данных PostgreSQL
- Таблицы: `users`, `subscriptions`, `payments`, и все остальные

**Что может испортиться:**
- ❌ Если таблицы `referral_codes` или `referrals` уже существуют с другой структурой
- ❌ Конфликты при создании индексов
- ❌ Потеря данных, если случайно выполнить `DROP TABLE`

**Как сохранить:**
```bash
# Полный backup базы данных
pg_dump -h localhost -U your_user -d your_database > backup_database_$(date +%Y%m%d_%H%M%S).sql

# Или только структура (без данных)
pg_dump -h localhost -U your_user -d your_database --schema-only > backup_schema_$(date +%Y%m%d_%H%M%S).sql
```

**Где хранить:**
- `/tmp/referral_backup_YYYYMMDD_HHMMSS/database_backup.sql`
- Или в безопасном месте на сервере

---

### 2. Nginx конфигурация (КРИТИЧНО!)

**Что сохранить:**
- `/etc/nginx/sites-available/aladdin-ai.ru`
- `/etc/nginx/nginx.conf` (если изменяли)
- Все SSL сертификаты

**Что может испортиться:**
- ❌ Потеря существующих настроек сайта
- ❌ Потеря SSL сертификатов (пути к файлам)
- ❌ Потеря настроек проксирования
- ❌ Потеря настроек для других доменов (если есть)
- ❌ Сайт может перестать работать

**Как сохранить:**
```bash
# Сохранить конфигурацию сайта
sudo cp /etc/nginx/sites-available/aladdin-ai.ru /etc/nginx/sites-available/aladdin-ai.ru.backup_$(date +%Y%m%d_%H%M%S)

# Сохранить главную конфигурацию (если нужно)
sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup_$(date +%Y%m%d_%H%M%S)

# Проверить SSL сертификаты
ls -la /etc/letsencrypt/live/aladdin-ai.ru/
```

**Где хранить:**
- `/tmp/referral_backup_YYYYMMDD_HHMMSS/nginx_backup.conf`
- Или в `/etc/nginx/sites-available/` с расширением `.backup`

---

### 3. Python/FastAPI проект (ВАЖНО!)

**Что сохранить:**
- Весь проект FastAPI
- Все файлы в директории проекта
- Особенно: `app/routers/`, `app/models/`, `app/database.py`

**Что может испортиться:**
- ❌ Перезапись существующих файлов с таким же именем
- ❌ Конфликты импортов
- ❌ Потеря существующего кода
- ❌ Ошибки в приложении из-за конфликтов

**Как сохранить:**
```bash
# Вариант 1: Git (РЕКОМЕНДУЕТСЯ)
cd /path/to/your/fastapi/project
git add .
git commit -m "Backup before referral program deployment"
git tag backup-before-referral-$(date +%Y%m%d)

# Вариант 2: Копирование директории
cp -r /path/to/your/fastapi/project /path/to/backup/fastapi_project_$(date +%Y%m%d_%H%M%S)

# Вариант 3: Тар-архив
tar -czf /tmp/fastapi_backup_$(date +%Y%m%d_%H%M%S).tar.gz /path/to/your/fastapi/project
```

**Где хранить:**
- Git репозиторий (лучший вариант)
- `/tmp/referral_backup_YYYYMMDD_HHMMSS/fastapi_project/`
- Или отдельная директория на сервере

---

## 🟡 ВАЖНО: Желательно сохранить

### 4. Статические файлы (HTML, CSS, JS)

**Что сохранить:**
- `/var/www/aladdin-ai.ru/` (если есть)
- Все HTML шаблоны
- Статические файлы (CSS, JS, изображения)

**Что может испортиться:**
- ❌ Перезапись существующих HTML файлов
- ❌ Потеря кастомных стилей

**Как сохранить:**
```bash
# Если есть статические файлы
cp -r /var/www/aladdin-ai.ru /var/www/aladdin-ai.ru.backup_$(date +%Y%m%d_%H%M%S)
```

---

### 5. Переменные окружения (.env файлы)

**Что сохранить:**
- `.env` файлы в проекте
- Конфигурационные файлы
- Секретные ключи

**Что может испортиться:**
- ❌ Потеря настроек подключения к БД
- ❌ Потеря API ключей
- ❌ Потеря секретных токенов

**Как сохранить:**
```bash
# Сохранить .env файлы
cp /path/to/project/.env /path/to/project/.env.backup_$(date +%Y%m%d_%H%M%S)
```

---

### 6. Логи (для отладки)

**Что сохранить:**
- Логи приложения
- Логи Nginx
- Логи системы

**Что может испортиться:**
- ❌ Потеря истории ошибок
- ❌ Сложнее отладить проблемы

**Как сохранить:**
```bash
# Логи Nginx
sudo cp /var/log/nginx/error.log /var/log/nginx/error.log.backup_$(date +%Y%m%d_%H%M%S)
sudo cp /var/log/nginx/access.log /var/log/nginx/access.log.backup_$(date +%Y%m%d_%H%M%S)
```

---

## 📊 ТАБЛИЦА: Что может испортиться

| Компонент | Что может испортиться | Риск | Защита |
|-----------|----------------------|------|--------|
| **База данных** | Таблицы с другой структурой, потеря данных | 🔴 Высокий | `IF NOT EXISTS` в SQL |
| **Nginx** | Потеря конфигурации, сайт не работает | 🔴 Высокий | Backup конфигурации |
| **Python код** | Перезапись файлов, конфликты | 🟡 Средний | Git, копирование |
| **Статические файлы** | Перезапись HTML/CSS | 🟡 Средний | Копирование |
| **Переменные окружения** | Потеря настроек | 🟡 Средний | Backup .env |
| **Логи** | Потеря истории | 🟢 Низкий | Не критично |

---

## 🛡️ ЧТО ЗАЩИЩЕНО В СКРИПТАХ

### SQL скрипт (`REFERRAL_DB_SETUP.sql`):
✅ Использует `CREATE TABLE IF NOT EXISTS` - не перезапишет таблицы  
✅ Использует `CREATE INDEX IF NOT EXISTS` - не создаст дубликаты  
✅ Использует `ON CONFLICT DO NOTHING` - не удалит данные  

### Python скрипт:
⚠️ Проверяет существование директорий  
⚠️ НО: Может перезаписать файлы с таким же именем  

### Nginx скрипт:
⚠️ Проверяет существование конфигурации  
⚠️ НО: Перезапишет файл, если подтвердите  

---

## 📋 ПОЛНЫЙ ЧЕКЛИСТ BACKUP'ОВ

### Обязательно:
- [ ] База данных (полный dump)
- [ ] Nginx конфигурация (`/etc/nginx/sites-available/aladdin-ai.ru`)
- [ ] Python проект (Git commit или копирование)

### Желательно:
- [ ] Статические файлы (если есть)
- [ ] Переменные окружения (.env файлы)
- [ ] Логи (для отладки)

---

## 🚀 БЫСТРЫЙ BACKUP (одной командой)

Используйте скрипт:
```bash
./BACKUP_SCRIPT.sh
```

Он создаст все необходимые backup'ы автоматически!

---

## 🔄 ВОССТАНОВЛЕНИЕ ИЗ BACKUP'А

### База данных:
```bash
psql -h localhost -U your_user -d your_database < backup_database_YYYYMMDD_HHMMSS.sql
```

### Nginx:
```bash
sudo cp /etc/nginx/sites-available/aladdin-ai.ru.backup_YYYYMMDD /etc/nginx/sites-available/aladdin-ai.ru
sudo nginx -t
sudo systemctl reload nginx
```

### Python проект:
```bash
# Из Git
cd /path/to/project
git checkout backup-before-referral-YYYYMMDD

# Или из копии
cp -r /path/to/backup/fastapi_project_YYYYMMDD_HHMMSS/* /path/to/project/
```

---

## ✅ ИТОГ

**Сохраните:**
1. ✅ База данных (критично!)
2. ✅ Nginx конфигурация (критично!)
3. ✅ Python проект (важно!)

**Используйте:**
- `./BACKUP_SCRIPT.sh` - автоматический backup
- Или создайте backup'ы вручную по инструкциям выше

**Помните:** Backup'ы - ваша страховка! 🛡️

---

**Последнее обновление:** 21 ноября 2024

