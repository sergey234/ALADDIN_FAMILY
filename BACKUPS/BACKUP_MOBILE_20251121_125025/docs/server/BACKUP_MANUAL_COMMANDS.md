# 📋 РУЧНОЕ СОЗДАНИЕ BACKUP'ОВ: Команды для копирования

**Дата:** 21 ноября 2024  
**Альтернатива скрипту:** Выполняйте команды вручную

---

## 🎯 ВАРИАНТЫ СОЗДАНИЯ BACKUP'ОВ

### ✅ Вариант 1: Ручные команды (рекомендуется для контроля)
Выполняйте команды по одной, видите что происходит

### ✅ Вариант 2: Скрипт (быстро, но меньше контроля)
Запускаете один скрипт, все делается автоматически

---

## 📋 РУЧНЫЕ КОМАНДЫ (Вариант 1)

### 1. Создать директорию для backup'ов
```bash
mkdir -p /tmp/referral_backup_$(date +%Y%m%d_%H%M%S)
cd /tmp/referral_backup_$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=$(pwd)
echo "Backup директория: $BACKUP_DIR"
```

### 2. Backup базы данных
```bash
# Полный backup
pg_dump -h localhost -U your_user -d your_database > $BACKUP_DIR/database_full_backup.sql

# Или только структура (без данных)
pg_dump -h localhost -U your_user -d your_database --schema-only > $BACKUP_DIR/database_schema_only.sql
```

### 3. Backup Nginx конфигурации
```bash
# Конфигурация сайта
sudo cp /etc/nginx/sites-available/aladdin-ai.ru $BACKUP_DIR/nginx_aladdin-ai.ru.backup

# Главная конфигурация (если изменяли)
sudo cp /etc/nginx/nginx.conf $BACKUP_DIR/nginx_main.conf.backup

# Все конфигурации сайтов
sudo cp -r /etc/nginx/sites-available $BACKUP_DIR/nginx_sites_available
```

### 4. Backup Python проекта
```bash
# Вариант A: Git (если используется)
cd /path/to/your/fastapi/project
git add .
git commit -m "Backup before referral deployment"
git tag backup-before-referral-$(date +%Y%m%d)

# Вариант B: Копирование директории
cp -r /path/to/your/fastapi/project $BACKUP_DIR/fastapi_project_backup
```

### 5. Backup переменных окружения
```bash
# Найти и скопировать .env файлы
find /path/to/your/fastapi/project -name ".env*" -exec cp {} $BACKUP_DIR/ \;
```

### 6. Backup статических файлов (если есть)
```bash
sudo cp -r /var/www/aladdin-ai.ru $BACKUP_DIR/static_files_backup
```

### 7. Создать архив (опционально)
```bash
cd /tmp
tar -czf referral_backup_$(date +%Y%m%d_%H%M%S).tar.gz referral_backup_*/
```

---

## 🤔 ПОЧЕМУ СКРИПТ?

### ✅ Плюсы скрипта:
- **Быстро** - одна команда вместо многих
- **Автоматизация** - не нужно помнить все команды
- **Меньше ошибок** - команды уже проверены
- **Повторяемость** - можно запустить снова

### ❌ Минусы скрипта:
- **Меньше контроля** - не видите каждую команду
- **Может быть страшно** - не знаете что происходит внутри
- **Меньше гибкости** - нужно адаптировать под ваш проект

---

## 🎯 МОЯ РЕКОМЕНДАЦИЯ

### Для первого раза: Ручные команды
**Почему:**
- Видите каждую команду
- Понимаете что происходит
- Можете остановиться на любом этапе
- Больше контроля

**Как:**
1. Используйте команды из этого файла
2. Выполняйте по одной
3. Проверяйте результат после каждой команды

### Для повторного использования: Скрипт
**Почему:**
- Быстрее
- Удобнее
- Меньше ошибок

**Как:**
```bash
./CREATE_BACKUP.sh
```

---

## 📋 БЫСТРЫЙ ЧЕКЛИСТ (Ручной способ)

```bash
# 1. Создать директорию
BACKUP_DIR="/tmp/referral_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# 2. Backup БД
pg_dump -h localhost -U user -d database > "$BACKUP_DIR/database.sql"

# 3. Backup Nginx
sudo cp /etc/nginx/sites-available/aladdin-ai.ru "$BACKUP_DIR/nginx.conf"

# 4. Backup проекта (Git)
cd /path/to/project && git tag backup-$(date +%Y%m%d)

# 5. Проверить что все сохранено
ls -la "$BACKUP_DIR"
```

---

## ✅ ИТОГ

**Выбирайте то, что вам удобнее:**

- 🟢 **Ручные команды** - больше контроля, видите каждый шаг
- 🟡 **Скрипт** - быстрее, автоматизация

**Оба способа создадут одинаковые backup'ы!**

---

**Последнее обновление:** 21 ноября 2024

