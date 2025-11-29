# 🔍 СРАВНЕНИЕ ЛЕНДИНГА: Локальный vs Сервер

**Дата:** 22 ноября 2024  
**Цель:** Сравнить локальный лендинг с тем, что на сервере

---

## 📁 ЛОКАЛЬНЫЙ ЛЕНДИНГ

**Путь:** `/Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS/landing/`

**Файлы:**
- `index.html` - главная страница
- `consent.html` - страница согласия
- `privacy.html` - политика конфиденциальности
- `terms.html` - условия использования
- `success.html` - страница успеха
- CSS, JS файлы (если есть)

---

## 🌐 ЛЕНДИНГ С СЕРВЕРА (из backup)

**Путь на сервере:** `/var/www/aladdin-ai.ru/`  
**Backup:** `BACKUPS/FULL_SITE_BACKUP_*/website_full_backup.tar.gz`

**Файлы:**
- Те же файлы, что были загружены на сервер

---

## 🔍 КАК СРАВНИТЬ

### Вариант 1: Автоматическое сравнение

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Распаковать backup
BACKUP_DIR=$(find BACKUPS/FULL_SITE_BACKUP_* -type d -maxdepth 0 | tail -1)
mkdir -p "$BACKUP_DIR/website_extracted"
tar -xzf "$BACKUP_DIR/website_full_backup.tar.gz" -C "$BACKUP_DIR/website_extracted"

# Сравнить файлы
diff -r landing/ "$BACKUP_DIR/website_extracted/aladdin-ai.ru/"
```

### Вариант 2: Сравнение размеров

```bash
# Размер локального лендинга
du -sh landing/

# Размер лендинга с сервера
du -sh "$BACKUP_DIR/website_extracted/aladdin-ai.ru/"
```

### Вариант 3: Сравнение конкретных файлов

```bash
# Сравнить index.html
diff landing/index.html "$BACKUP_DIR/website_extracted/aladdin-ai.ru/index.html"

# Сравнить consent.html
diff landing/consent.html "$BACKUP_DIR/website_extracted/aladdin-ai.ru/consent.html"
```

---

## ✅ ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

Если лендинг был загружен на сервер через `deploy_with_password.sh`, то:
- ✅ Файлы должны совпадать
- ✅ Размеры должны быть одинаковыми
- ✅ Содержимое должно быть идентичным

---

## 🔧 ЕСЛИ ЕСТЬ РАЗЛИЧИЯ

### Возможные причины:
1. Лендинг был изменен на сервере вручную
2. Лендинг не был загружен полностью
3. На сервере есть дополнительные файлы

### Что делать:
1. Проверить различия: `diff -r landing/ server_backup/`
2. Решить, какой вариант актуальнее
3. Синхронизировать файлы

---

**Последнее обновление:** 22 ноября 2024

