# 🔍 ПОИСК ПОДКЛЮЧЕНИЯ К БАЗЕ ДАННЫХ

**Проблема:** `psql` не найден на сервере

---

## ✅ ВАРИАНТЫ РЕШЕНИЯ

### Вариант 1: Установить PostgreSQL клиент

```bash
# Установить PostgreSQL клиент
apt update
apt install postgresql-client -y

# После установки выполнить SQL скрипт
psql -U ваш_пользователь -d ваша_база -f /tmp/REFERRAL_DB_SETUP.sql
```

---

### Вариант 2: PostgreSQL в Docker

Если PostgreSQL запущен в Docker:

```bash
# Найти контейнер
docker ps | grep postgres

# Выполнить SQL скрипт через Docker
docker exec -i имя_контейнера psql -U ваш_пользователь -d ваша_база < /tmp/REFERRAL_DB_SETUP.sql

# Или подключиться к контейнеру
docker exec -it имя_контейнера psql -U ваш_пользователь -d ваша_база
# Затем в psql:
\i /tmp/REFERRAL_DB_SETUP.sql
```

---

### Вариант 3: Найти параметры подключения в Python проекте

```bash
# Проверить .env файл
cat /opt/aladdin-backend/.env | grep -i db

# Проверить config.py
cat /opt/aladdin-backend/app/config.py | grep -i database

# Проверить settings.py
find /opt/aladdin-backend -name "settings.py" -exec grep -i database {} \;
```

После нахождения параметров подключения используйте их для `psql`.

---

### Вариант 4: Выполнить через Python скрипт

Создать временный Python скрипт для выполнения SQL:

```bash
# Создать скрипт
cat > /tmp/execute_sql.py << 'EOF'
import psycopg2
import sys

# Параметры подключения (замените на ваши)
conn_params = {
    'host': 'localhost',
    'port': 5432,
    'user': 'ваш_пользователь',
    'password': 'ваш_пароль',
    'database': 'ваша_база'
}

try:
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()
    
    # Читаем SQL файл
    with open('/tmp/REFERRAL_DB_SETUP.sql', 'r') as f:
        sql = f.read()
    
    # Выполняем SQL
    cursor.execute(sql)
    conn.commit()
    
    print("✅ SQL скрипт выполнен успешно")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Ошибка: {e}")
    sys.exit(1)
EOF

# Выполнить скрипт
python3 /tmp/execute_sql.py
```

---

## 🔍 КОМАНДЫ ДЛЯ ДИАГНОСТИКИ

Выполните на сервере для определения способа подключения:

```bash
# 1. Проверить установлен ли PostgreSQL
which psql
dpkg -l | grep postgresql

# 2. Проверить Docker
docker ps | grep postgres
docker ps -a | grep postgres

# 3. Проверить процессы
ps aux | grep postgres

# 4. Проверить конфигурацию Python проекта
cat /opt/aladdin-backend/.env 2>/dev/null | grep -i db
find /opt/aladdin-backend -name "*.py" -exec grep -l "DATABASE\|database\|postgres" {} \;

# 5. Проверить сетевые подключения
netstat -tuln | grep 5432
ss -tuln | grep 5432
```

---

## 📋 ЧТО НУЖНО УЗНАТЬ

1. **Где находится PostgreSQL?**
   - Локально на сервере?
   - В Docker контейнере?
   - На другом сервере?

2. **Параметры подключения:**
   - Хост (host)
   - Порт (обычно 5432)
   - Пользователь (user)
   - Пароль (password)
   - Имя базы данных (database)

3. **Как обычно подключаются к БД?**
   - Через Python приложение?
   - Через какой-то скрипт?
   - Через веб-интерфейс?

---

После получения этой информации мы сможем выполнить SQL скрипт правильным способом.


