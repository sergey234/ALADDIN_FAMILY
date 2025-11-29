# 🛡️ ПРОСТОЙ СПОСОБ: Создать backup вручную

**Дата:** 21 ноября 2024  
**Самый простой способ:** Выполните эти 4 команды

---

## ✅ МИНИМАЛЬНЫЙ BACKUP (4 команды)

### 1. База данных
```bash
pg_dump -h localhost -U your_user -d your_database > backup_database_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Nginx
```bash
sudo cp /etc/nginx/sites-available/aladdin-ai.ru /etc/nginx/sites-available/aladdin-ai.ru.backup_$(date +%Y%m%d_%H%M%S)
```

### 3. Python проект (Git)
```bash
cd /path/to/your/fastapi/project
git add . && git commit -m "Backup before referral" && git tag backup-$(date +%Y%m%d)
```

### 4. Проверить
```bash
ls -la backup_*  # Проверить что файлы созданы
git tag          # Проверить что Git tag создан
```

---

## 🎯 ГОТОВО!

Теперь у вас есть backup'ы:
- ✅ База данных: `backup_database_YYYYMMDD_HHMMSS.sql`
- ✅ Nginx: `/etc/nginx/sites-available/aladdin-ai.ru.backup_YYYYMMDD_HHMMSS`
- ✅ Проект: Git tag `backup-YYYYMMDD`

---

## 💡 ПОЧЕМУ НЕ СКРИПТ?

**Скрипт - это просто удобство, не обязательно!**

Вы можете:
- ✅ Выполнить команды вручную (больше контроля)
- ✅ Использовать скрипт (быстрее)

**Оба способа работают одинаково!**

---

**Выбирайте то, что вам удобнее!** 🎯


