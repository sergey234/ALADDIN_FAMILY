# 🛡️ ПОШАГОВОЕ СОЗДАНИЕ BACKUP'ОВ: Выполняйте команды по одной

**Дата:** 21 ноября 2024  
**Способ:** Ручные команды (максимальный контроль)  
**Время:** 5-10 минут

---

## 📋 ИНСТРУКЦИЯ: Выполняйте команды по порядку

### ✅ ШАГ 1: Создать директорию для backup'ов

```bash
# Создать директорию с текущей датой и временем
BACKUP_DIR="/tmp/referral_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cd "$BACKUP_DIR"

# Проверить что директория создана
echo "Backup директория: $BACKUP_DIR"
ls -la
```

**Что произошло:** Создана директория для хранения всех backup'ов  
**Проверка:** Должна появиться пустая директория

---

### ✅ ШАГ 2: Backup базы данных

```bash
# ВАЖНО: Замените your_user, your_database, localhost на ваши значения!

# Полный backup базы данных (со всеми данными)
pg_dump -h localhost -U your_user -d your_database > "$BACKUP_DIR/database_full_backup.sql"

# Проверить что файл создан
ls -lh "$BACKUP_DIR/database_full_backup.sql"
```

**Что произошло:** Создан полный backup базы данных  
**Проверка:** Должен появиться файл `database_full_backup.sql`  
**Размер:** Зависит от размера БД (может быть несколько МБ или ГБ)

**Если нужен только backup структуры (без данных):**
```bash
# Только структура таблиц (без данных)
pg_dump -h localhost -U your_user -d your_database --schema-only > "$BACKUP_DIR/database_schema_only.sql"
```

---

### ✅ ШАГ 3: Backup Nginx конфигурации

```bash
# Backup конфигурации сайта aladdin-ai.ru
sudo cp /etc/nginx/sites-available/aladdin-ai.ru "$BACKUP_DIR/nginx_aladdin-ai.ru.backup"

# Проверить что файл создан
ls -lh "$BACKUP_DIR/nginx_aladdin-ai.ru.backup"

# Также сохранить главную конфигурацию (на всякий случай)
sudo cp /etc/nginx/nginx.conf "$BACKUP_DIR/nginx_main.conf.backup" 2>/dev/null || echo "Главная конфигурация не найдена или не изменялась"
```

**Что произошло:** Сохранена конфигурация Nginx  
**Проверка:** Должен появиться файл `nginx_aladdin-ai.ru.backup`  
**Размер:** Обычно несколько КБ

---

### ✅ ШАГ 4: Backup Python/FastAPI проекта

**Вариант A: Если используется Git (РЕКОМЕНДУЕТСЯ)**

```bash
# Перейти в директорию проекта
cd /path/to/your/fastapi/project

# Проверить что это Git репозиторий
git status

# Создать commit с текущими изменениями
git add .
git commit -m "Backup before referral program deployment"

# Создать Git tag для быстрого восстановления
git tag backup-before-referral-$(date +%Y%m%d)

# Проверить что tag создан
git tag | grep backup

# Вернуться в backup директорию
cd "$BACKUP_DIR"
```

**Что произошло:** Создан Git commit и tag для восстановления  
**Проверка:** Команда `git tag` должна показать новый tag

**Вариант B: Если Git не используется**

```bash
# Копировать весь проект
cp -r /path/to/your/fastapi/project "$BACKUP_DIR/fastapi_project_backup"

# Проверить что директория скопирована
ls -lh "$BACKUP_DIR/fastapi_project_backup"
```

**Что произошло:** Скопирован весь проект  
**Проверка:** Должна появиться директория `fastapi_project_backup`

---

### ✅ ШАГ 5: Backup переменных окружения (.env файлы)

```bash
# Найти и скопировать все .env файлы из проекта
find /path/to/your/fastapi/project -name ".env*" -type f -exec cp {} "$BACKUP_DIR/" \;

# Проверить что файлы скопированы
ls -la "$BACKUP_DIR" | grep ".env"
```

**Что произошло:** Сохранены все .env файлы  
**Проверка:** Должны появиться файлы `.env` или `.env.*`

---

### ✅ ШАГ 6: Backup статических файлов (если есть)

```bash
# Если есть статические файлы на сервере
if [ -d "/var/www/aladdin-ai.ru" ]; then
    sudo cp -r /var/www/aladdin-ai.ru "$BACKUP_DIR/static_files_backup"
    echo "Статические файлы скопированы"
else
    echo "Директория статических файлов не найдена (это нормально, если не используется)"
fi
```

**Что произошло:** Сохранены статические файлы (если есть)  
**Проверка:** Может быть или не быть, в зависимости от вашей настройки

---

### ✅ ШАГ 7: Создать информационный файл

```bash
# Создать файл с информацией о backup'е
cat > "$BACKUP_DIR/BACKUP_INFO.txt" << EOF
===========================================
BACKUP ИНФОРМАЦИЯ
===========================================
Дата создания: $(date)
Backup директория: $BACKUP_DIR

СОЗДАННЫЕ BACKUP'Ы:
- База данных: database_full_backup.sql
- Nginx: nginx_aladdin-ai.ru.backup
- Python проект: Git tag или fastapi_project_backup/
- Переменные окружения: .env файлы

ВОССТАНОВЛЕНИЕ:
1. База данных:
   psql -h localhost -U user -d database < database_full_backup.sql

2. Nginx:
   sudo cp nginx_aladdin-ai.ru.backup /etc/nginx/sites-available/aladdin-ai.ru
   sudo nginx -t && sudo systemctl reload nginx

3. Python проект (Git):
   cd /path/to/project
   git checkout backup-before-referral-YYYYMMDD

ВАЖНО: Сохраните этот backup в безопасном месте!
===========================================
EOF

# Показать содержимое
cat "$BACKUP_DIR/BACKUP_INFO.txt"
```

**Что произошло:** Создан файл с информацией о backup'е  
**Проверка:** Должен появиться файл `BACKUP_INFO.txt`

---

### ✅ ШАГ 8: Проверить все backup'ы

```bash
# Показать все созданные файлы
echo "=== ВСЕ BACKUP'Ы ==="
ls -lh "$BACKUP_DIR"

# Показать размер директории
du -sh "$BACKUP_DIR"

# Показать путь к backup директории
echo ""
echo "Backup директория: $BACKUP_DIR"
echo "Сохраните этот путь!"
```

**Что произошло:** Проверены все созданные backup'ы  
**Проверка:** Должны быть видны все файлы

---

### ✅ ШАГ 9: Создать архив (опционально, но рекомендуется)

```bash
# Создать tar.gz архив для удобного хранения
cd /tmp
tar -czf referral_backup_$(date +%Y%m%d_%H%M%S).tar.gz "$(basename "$BACKUP_DIR")"

# Проверить что архив создан
ls -lh referral_backup_*.tar.gz

# Показать размер архива
du -sh referral_backup_*.tar.gz
```

**Что произошло:** Создан сжатый архив всех backup'ов  
**Проверка:** Должен появиться файл `.tar.gz`  
**Преимущество:** Один файл вместо множества, легче хранить и переносить

---

## ✅ ИТОГ: Что должно быть создано

После выполнения всех шагов у вас должно быть:

1. ✅ **База данных:** `database_full_backup.sql`
2. ✅ **Nginx:** `nginx_aladdin-ai.ru.backup`
3. ✅ **Python проект:** Git tag или директория `fastapi_project_backup/`
4. ✅ **Переменные окружения:** `.env` файлы
5. ✅ **Информация:** `BACKUP_INFO.txt`
6. ✅ **Архив (опционально):** `referral_backup_YYYYMMDD_HHMMSS.tar.gz`

---

## 🎯 ВАЖНО: Сохраните путь!

```bash
echo "Backup директория: $BACKUP_DIR"
echo "Сохраните этот путь для восстановления!"
```

**Запишите путь к backup директории!** Он понадобится для восстановления.

---

## 🔄 ВОССТАНОВЛЕНИЕ (на всякий случай)

Если что-то пойдет не так, используйте эти команды:

### Восстановить базу данных:
```bash
psql -h localhost -U your_user -d your_database < "$BACKUP_DIR/database_full_backup.sql"
```

### Восстановить Nginx:
```bash
sudo cp "$BACKUP_DIR/nginx_aladdin-ai.ru.backup" /etc/nginx/sites-available/aladdin-ai.ru
sudo nginx -t
sudo systemctl reload nginx
```

### Восстановить проект (Git):
```bash
cd /path/to/your/fastapi/project
git checkout backup-before-referral-YYYYMMDD
```

---

## ✅ ГОТОВО!

Теперь у вас есть полный backup всех критичных файлов!

**Следующий шаг:** Можно приступать к развертыванию реферальной программы.

---

**Последнее обновление:** 21 ноября 2024


