# 🚀 РУКОВОДСТВО ПО РАЗВЕРТЫВАНИЮ МИГРАЦИИ

**Дата:** 2026-03-14  
**Статус:** ✅ Готово к развертыванию

---

## 📋 ПОДГОТОВКА

### **Требования:**

1. ✅ Доступ к серверу `149.154.65.180` через SSH
2. ✅ Учетные данные: `root` / `Sergio675`
3. ✅ Python 3 на сервере
4. ✅ Библиотеки: `psycopg2`, `requests` (если нужны)

---

## 🚀 СПОСОБЫ РАЗВЕРТЫВАНИЯ

### **ВАРИАНТ 1: Автоматический скрипт (рекомендуется)**

```bash
cd /path/to/aladdin-backend/app/database/migrations
./remote_execute.sh
```

**Что делает:**
1. ✅ Подключается к серверу
2. ✅ Применяет миграцию
3. ✅ Тестирует endpoints
4. ✅ Проверяет соответствие документации

---

### **ВАРИАНТ 2: Ручное выполнение**

#### **Шаг 1: Копирование файлов на сервер**

```bash
# С локального компьютера
scp create_component_tables.sql root@149.154.65.180:/opt/aladdin-backend/app/database/migrations/
scp apply_migration.py root@149.154.65.180:/opt/aladdin-backend/app/database/migrations/
scp test_endpoints.py root@149.154.65.180:/opt/aladdin-backend/app/database/migrations/
scp verify_endpoints.py root@149.154.65.180:/opt/aladdin-backend/app/database/migrations/
```

#### **Шаг 2: Подключение к серверу**

```bash
ssh root@149.154.65.180
# Введите пароль: Sergio675
```

#### **Шаг 3: Применение миграции**

```bash
cd /opt/aladdin-backend
python3 app/database/migrations/apply_migration.py
```

**Ожидаемый результат:**
```
✅ Подключение установлено
✅ Миграция успешно применена!
✅ dark_web_leaks
✅ dark_web_scans
✅ identity_theft_attempts
✅ location_requests
✅ data_cleanup_records
✅ tracker_blocks
✅ ai_category_reports
✅ Все индексы созданы
```

#### **Шаг 4: Тестирование endpoints**

```bash
cd /opt/aladdin-backend
export API_BASE_URL="https://aladdin-ai.ru"
export TEST_TOKEN="your_token_here"  # Опционально
python3 app/database/migrations/test_endpoints.py
```

#### **Шаг 5: Проверка соответствия документации**

```bash
cd /opt/aladdin-backend
python3 app/database/migrations/verify_endpoints.py
```

---

### **ВАРИАНТ 3: Прямое применение SQL**

Если скрипт Python не работает, можно применить SQL напрямую:

```bash
ssh root@149.154.65.180
psql -U aladdin_user -d aladdin_db -f /opt/aladdin-backend/app/database/migrations/create_component_tables.sql
```

---

## 🔍 ПРОВЕРКА РЕЗУЛЬТАТОВ

### **Проверка созданных таблиц:**

```sql
-- Подключиться к PostgreSQL
psql -U aladdin_user -d aladdin_db

-- Проверить таблицы
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN (
    'dark_web_leaks',
    'dark_web_scans',
    'identity_theft_attempts',
    'location_requests',
    'data_cleanup_records',
    'tracker_blocks',
    'ai_category_reports'
)
ORDER BY table_name;
```

**Ожидаемый результат:** 7 таблиц

---

### **Проверка индексов:**

```sql
SELECT tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN (
    'dark_web_leaks',
    'dark_web_scans',
    'identity_theft_attempts',
    'location_requests',
    'data_cleanup_records',
    'tracker_blocks',
    'ai_category_reports'
)
ORDER BY tablename, indexname;
```

**Ожидаемый результат:** 21 индекс

---

## ⚠️ РЕШЕНИЕ ПРОБЛЕМ

### **Проблема 1: "psycopg2 не установлен"**

```bash
# На сервере
pip3 install psycopg2-binary
```

### **Проблема 2: "requests не установлен"**

```bash
# На сервере
pip3 install requests
```

### **Проблема 3: "Permission denied"**

```bash
# Проверить права доступа
ls -la /opt/aladdin-backend/app/database/migrations/

# Дать права на выполнение
chmod +x /opt/aladdin-backend/app/database/migrations/*.py
```

### **Проблема 4: "Connection refused"**

```bash
# Проверить подключение к PostgreSQL
psql -U aladdin_user -d aladdin_db -h localhost

# Проверить переменную окружения DATABASE_URL
echo $DATABASE_URL
```

---

## ✅ ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ

### **После применения миграции:**

- ✅ 7 таблиц созданы
- ✅ 21 индекс создан
- ✅ Нет ошибок

### **После тестирования endpoints:**

- ✅ Все endpoints возвращают HTTP 200
- ✅ Структура ответов корректна
- ✅ Данные корректны (или пустые если таблицы пустые)

### **После проверки документации:**

- ✅ Все 33 endpoints соответствуют документации
- ✅ Нет отсутствующих endpoints
- ✅ Нет лишних endpoints

---

## 📊 ИТОГОВАЯ ПРОВЕРКА

После выполнения всех шагов проверьте:

1. ✅ Таблицы созданы в БД
2. ✅ Endpoints работают
3. ✅ Graceful degradation работает
4. ✅ Все соответствует документации

---

## 🎯 БЫСТРЫЙ СТАРТ

```bash
# 1. Перейти в директорию миграций
cd /path/to/aladdin-backend/app/database/migrations

# 2. Запустить автоматический скрипт
./remote_execute.sh

# ИЛИ выполнить вручную:
ssh root@149.154.65.180
cd /opt/aladdin-backend
python3 app/database/migrations/apply_migration.py
python3 app/database/migrations/test_endpoints.py
python3 app/database/migrations/verify_endpoints.py
```

---

## ✅ ГОТОВО К РАЗВЕРТЫВАНИЮ!

Все файлы подготовлены и готовы к использованию.
