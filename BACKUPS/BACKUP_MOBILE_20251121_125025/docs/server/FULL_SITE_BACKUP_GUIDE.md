# 🛡️ ПОЛНЫЙ BACKUP ВСЕГО САЙТА: Инструкция

**Сервер:** 149.154.65.180  
**Что сохраняется:** Весь сайт полностью

---

## ✅ ЧТО СОХРАНЯЕТСЯ

### 1. База данных
- Полный dump всех таблиц
- Все данные

### 2. Nginx конфигурация
- Все конфигурации сайтов (`/etc/nginx/sites-available/`)
- Главная конфигурация (`/etc/nginx/nginx.conf`)

### 3. Весь сайт
- Все файлы из `/var/www/aladdin-ai.ru/`
- HTML, CSS, JS файлы
- Все статические файлы

### 4. Python/FastAPI проект
- Весь код проекта
- Все файлы и директории
- Git история (если используется)

### 5. Конфигурационные файлы
- `.env` файлы
- Конфигурации приложений
- Системные настройки

---

## 🚀 КАК ИСПОЛЬЗОВАТЬ

### Просто запустите скрипт:

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
./docs/server/full_site_backup.sh
```

**Скрипт автоматически:**
1. ✅ Подключится к серверу
2. ✅ Создаст backup'ы на сервере
3. ✅ Скачает все на ваш компьютер
4. ✅ Сохранит в `BACKUPS/FULL_SITE_BACKUP_YYYYMMDD_HHMMSS/`

---

## 📁 ГДЕ НАХОДИТСЯ BACKUP

**Локально:**
```
BACKUPS/FULL_SITE_BACKUP_YYYYMMDD_HHMMSS/
├── database_full_backup.sql          # База данных
├── nginx_sites_available/            # Конфигурации Nginx
├── nginx_main.conf                   # Главная конфигурация Nginx
├── website_full_backup.tar.gz        # Весь сайт
├── project_backup.tar.gz             # Python проект
├── config_files_backup.tar.gz        # Конфигурационные файлы
├── BACKUP_INFO.txt                   # Информация о backup
└── full_site_backup_YYYYMMDD_HHMMSS.tar.gz  # Полный архив
```

**На сервере:**
```
/tmp/full_site_backup_YYYYMMDD_HHMMSS/
```

---

## 🔄 ВОССТАНОВЛЕНИЕ ИЗ BACKUP'А

### Восстановить базу данных:
```bash
psql -h localhost -U user -d database < database_full_backup.sql
```

### Восстановить сайт:
```bash
tar -xzf website_full_backup.tar.gz -C /var/www/
```

### Восстановить Nginx:
```bash
cp -r nginx_sites_available/* /etc/nginx/sites-available/
cp nginx_main.conf /etc/nginx/nginx.conf
sudo nginx -t && sudo systemctl reload nginx
```

### Восстановить проект:
```bash
tar -xzf project_backup.tar.gz -C /path/to/project/
```

---

## ⏱️ ВРЕМЯ ВЫПОЛНЕНИЯ

- **Небольшой сайт:** 2-5 минут
- **Средний сайт:** 5-10 минут
- **Большой сайт:** 10-20 минут

Зависит от размера базы данных и файлов.

---

## 💾 РАЗМЕР BACKUP'А

Обычно:
- База данных: 1-100 МБ
- Сайт: 10-500 МБ
- Проект: 50-500 МБ
- **Итого:** 100 МБ - 1 ГБ

---

## ✅ ГОТОВО!

**Запустите скрипт и весь сайт будет сохранен!**

```bash
./docs/server/full_site_backup.sh
```

---

**Последнее обновление:** 22 ноября 2024

