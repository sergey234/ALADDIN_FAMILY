# 🔍 ПОИСК КОНФИГУРАЦИИ БД (без Docker)

**Цель:** Найти параметры подключения к PostgreSQL в Python проекте

---

## 📋 КОМАНДЫ ДЛЯ ВЫПОЛНЕНИЯ НА СЕРВЕРЕ

### 1. Найти файлы конфигурации:

```bash
find /opt/aladdin-backend -name 'config.py' -o -name 'settings.py' -o -name 'database.py' | head -5
```

### 2. Проверить main.py:

```bash
find /opt/aladdin-backend -name 'main.py' | head -1 | xargs cat | grep -iE 'database|postgres|db|sqlalchemy'
```

### 3. Найти все упоминания подключения:

```bash
grep -r 'psycopg2\|postgresql\|DATABASE_URL\|SQLALCHEMY\|create_engine' /opt/aladdin-backend --include='*.py' | head -10
```

### 4. Проверить процессы PostgreSQL:

```bash
ps aux | grep postgres
```

### 5. Проверить сетевые подключения:

```bash
netstat -tuln | grep 5432 || ss -tuln | grep 5432
```

---

## 🎯 АЛЬТЕРНАТИВНЫЙ ВАРИАНТ: Выполнить через Python скрипт

Если не удается найти параметры, можно выполнить SQL через Python, используя те же параметры, что и в приложении:

```bash
# Создать скрипт
cat > /tmp/execute_referral_sql.py << 'EOF'
import sys
import os

# Добавить путь к проекту
sys.path.insert(0, '/opt/aladdin-backend')

try:
    # Попробовать импортировать конфигурацию из проекта
    from app.config import DATABASE_URL, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME
    # или
    # from app.settings import DATABASE_URL
    # или
    # from app.database import get_db_url
    
    print("✅ Конфигурация найдена в проекте")
    
except ImportError:
    # Если не удалось импортировать, попробовать найти вручную
    print("⚠️  Не удалось импортировать конфигурацию автоматически")
    print("Нужно найти параметры вручную")
    sys.exit(1)

# Выполнить SQL
import psycopg2
from urllib.parse import urlparse

try:
    # Если есть DATABASE_URL
    if 'DATABASE_URL' in locals():
        parsed = urlparse(DATABASE_URL)
        conn_params = {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'user': parsed.username,
            'password': parsed.password,
            'database': parsed.path.lstrip('/')
        }
    else:
        # Использовать отдельные параметры
        conn_params = {
            'host': DB_HOST,
            'port': DB_PORT or 5432,
            'user': DB_USER,
            'password': DB_PASSWORD,
            'database': DB_NAME
        }
    
    print(f"Подключение к БД: {conn_params['host']}:{conn_params['port']}/{conn_params['database']}")
    
    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()
    
    with open('/tmp/REFERRAL_DB_SETUP.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    
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
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

# Выполнить скрипт
cd /opt/aladdin-backend
python3 /tmp/execute_referral_sql.py
```

---

## 📝 ЧТО ИСКАТЬ В ВЫВОДЕ

После выполнения команд ищите:

1. **DATABASE_URL** - строка подключения вида `postgresql://user:password@host:port/database`
2. **Отдельные параметры:**
   - `DB_HOST` или `DATABASE_HOST`
   - `DB_PORT` или `DATABASE_PORT`
   - `DB_USER` или `DATABASE_USER`
   - `DB_PASSWORD` или `DATABASE_PASSWORD`
   - `DB_NAME` или `DATABASE_NAME`
3. **SQLAlchemy connection string** - в `create_engine()` или `SQLALCHEMY_DATABASE_URI`

---

После получения параметров можно выполнить SQL скрипт с правильными параметрами.


