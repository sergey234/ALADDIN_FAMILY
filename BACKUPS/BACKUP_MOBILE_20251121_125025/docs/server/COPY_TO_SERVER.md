# 🚀 КАК СКОПИРОВАТЬ И ЗАПУСТИТЬ НА СЕРВЕРЕ

**Сервер:** 149.154.65.180

---

## 📋 БЫСТРЫЙ СПОСОБ (3 команды)

### 1. Скопировать скрипт на сервер
```bash
# С вашего компьютера
scp docs/server/AUTO_BACKUP.sh user@149.154.65.180:/tmp/
```

### 2. Подключиться к серверу
```bash
ssh user@149.154.65.180
```

### 3. Запустить скрипт
```bash
cd /tmp
chmod +x AUTO_BACKUP.sh
./AUTO_BACKUP.sh
```

---

## ✅ ГОТОВО!

Скрипт автоматически:
- ✅ Найдет базу данных
- ✅ Сохранит Nginx конфигурацию
- ✅ Найдет и сохранит Python проект
- ✅ Создаст архив

**Все backup'ы будут в:** `/tmp/referral_backup_YYYYMMDD_HHMMSS/`

---

## 🔧 ЕСЛИ НУЖНО УКАЗАТЬ ПАРАМЕТРЫ ВРУЧНУЮ

```bash
# Указать параметры БД
export DB_USER=your_user
export DB_NAME=your_database
export DB_HOST=localhost

# Указать путь к проекту
export PROJECT_PATH=/path/to/your/fastapi/project

# Запустить скрипт
./AUTO_BACKUP.sh
```

---

**Скрипт сделает все автоматически!** 🎯

