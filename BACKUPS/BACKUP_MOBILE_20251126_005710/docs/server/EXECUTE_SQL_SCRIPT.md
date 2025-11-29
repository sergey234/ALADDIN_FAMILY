# 📋 ВЫПОЛНЕНИЕ SQL СКРИПТА: Поиск параметров подключения

**Проблема:** PostgreSQL клиент установлен, но подключение не удается

---

## 🔍 ШАГ 1: Найти параметры подключения

Выполните на сервере:

```bash
# 1. Проверить .env файл
cat /opt/aladdin-backend/.env 2>/dev/null | grep -iE 'db|database|postgres|host|port|user|password'

# 2. Найти файлы конфигурации
find /opt/aladdin-backend -name '*.py' -type f | xargs grep -l 'DATABASE\|database\|postgres' | head -5

# 3. Проверить config.py или settings.py
find /opt/aladdin-backend -name 'config.py' -o -name 'settings.py' | head -3

# 4. Проверить Docker
docker ps | grep postgres
```

---

## 📋 ШАГ 2: Выполнить SQL скрипт с правильными параметрами

После получения параметров используйте один из вариантов:

### Вариант 1: Локальный PostgreSQL

```bash
psql -h localhost -U ваш_пользователь -d ваша_база -f /tmp/REFERRAL_DB_SETUP.sql
```

### Вариант 2: Удаленный PostgreSQL

```bash
psql -h IP_АДРЕС -p ПОРТ -U ваш_пользователь -d ваша_база -f /tmp/REFERRAL_DB_SETUP.sql
```

### Вариант 3: Через Docker

```bash
# Если PostgreSQL в Docker
docker exec -i имя_контейнера psql -U ваш_пользователь -d ваша_база < /tmp/REFERRAL_DB_SETUP.sql
```

### Вариант 4: Через Python скрипт

Если не удается подключиться через psql, создайте Python скрипт:

```bash
cat > /tmp/execute_referral_sql.py << 'EOF'
import psycopg2
import sys

# Замените на ваши параметры из .env или config.py
conn_params = {
    'host': 'localhost',  # или IP адрес
    'port': 5432,  # или ваш порт
    'user': 'ваш_пользователь',
    'password': 'ваш_пароль',
    'database': 'ваша_база'
}

try:
    print("Подключение к БД...")
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()
    
    print("Чтение SQL файла...")
    with open('/tmp/REFERRAL_DB_SETUP.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    
    print("Выполнение SQL...")
    cursor.execute(sql)
    conn.commit()
    
    print("✅ SQL скрипт выполнен успешно!")
    
    # Проверить таблицы
    cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename LIKE 'referral%'")
    tables = cursor.fetchall()
    print(f"\n✅ Создано таблиц: {len(tables)}")
    for table in tables:
        print(f"   - {table[0]}")
    
    cursor.close()
    conn.close()
    
except psycopg2.Error as e:
    print(f"❌ Ошибка PostgreSQL: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Ошибка: {e}")
    sys.exit(1)
EOF

# Выполнить скрипт
cd /opt/aladdin-backend
python3 /tmp/execute_referral_sql.py
```

---

## 🔍 ЧТО НУЖНО УЗНАТЬ

Из конфигурации Python проекта нужно найти:

1. **DB_HOST** или **DATABASE_HOST** - хост БД
2. **DB_PORT** или **DATABASE_PORT** - порт (обычно 5432)
3. **DB_USER** или **DATABASE_USER** - пользователь
4. **DB_PASSWORD** или **DATABASE_PASSWORD** - пароль
5. **DB_NAME** или **DATABASE_NAME** - имя базы данных

---

## ✅ ПРОВЕРКА ПОСЛЕ ВЫПОЛНЕНИЯ

```bash
# Подключиться к БД
psql -h ХОСТ -p ПОРТ -U ПОЛЬЗОВАТЕЛЬ -d БАЗА

# В psql проверить таблицы
\dt referral*

# Проверить функции
\df get_or_create_referral_code

# Выйти
\q
```

---

После получения параметров подключения мы сможем выполнить SQL скрипт.


