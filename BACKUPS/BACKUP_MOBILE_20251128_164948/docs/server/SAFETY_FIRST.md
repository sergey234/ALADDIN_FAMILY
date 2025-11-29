# 🛡️ БЕЗОПАСНОСТЬ ПРЕЖДЕ ВСЕГО

**ВАЖНО:** Прочитайте перед развертыванием!

---

## ⚠️ РИСКИ И ЗАЩИТЫ

### Что может пойти не так:

1. **База данных** - перезапись существующих таблиц
2. **Nginx** - потеря существующей конфигурации
3. **Python код** - конфликты с существующим кодом

### Защиты:

✅ SQL скрипт использует `IF NOT EXISTS` - не перезапишет таблицы  
✅ Скрипт создает backup'ы автоматически  
✅ Есть режим `--dry-run` для проверки  
✅ Требуются подтверждения перед критическими операциями  

---

## 📋 ЧТО СОХРАНИТЬ (ОБЯЗАТЕЛЬНО!)

### 1. База данных
```bash
./BACKUP_SCRIPT.sh
# Или вручную:
pg_dump -h localhost -U user -d database > backup.sql
```

### 2. Nginx конфигурация
```bash
sudo cp /etc/nginx/sites-available/aladdin-ai.ru /etc/nginx/sites-available/aladdin-ai.ru.backup
```

### 3. Python проект
```bash
cd /path/to/project
git add . && git commit -m "Backup before referral"
git tag backup-before-referral
```

---

## 🎯 РЕКОМЕНДАЦИИ

### ✅ РЕКОМЕНДУЮ: Ручное развертывание

**Почему безопаснее:**
- Полный контроль
- Можно проверить каждый шаг
- Легче откатить

**Как:**
1. Создать backup'ы (`./BACKUP_SCRIPT.sh`)
2. Следовать `README.md`
3. Выполнять команды по одной

### 🟡 АЛЬТЕРНАТИВА: Безопасный скрипт

**Если используете скрипт:**
```bash
# 1. Сначала backup
./BACKUP_SCRIPT.sh

# 2. Проверка в dry-run режиме
./DEPLOY_SCRIPT_SAFE.sh --dry-run

# 3. Реальное развертывание
./DEPLOY_SCRIPT_SAFE.sh
```

---

## 🔄 ОТКАТ ИЗМЕНЕНИЙ

Если что-то пошло не так:

```bash
# Восстановить БД
psql -h localhost -U user -d database < backup.sql

# Восстановить Nginx
sudo cp /etc/nginx/sites-available/aladdin-ai.ru.backup /etc/nginx/sites-available/aladdin-ai.ru
sudo nginx -t && sudo systemctl reload nginx

# Восстановить проект
cd /path/to/project
git checkout backup-before-referral
```

---

**Помните: Backup'ы - ваша страховка!** 🛡️


