# 🔄 АЛЬТЕРНАТИВНЫЙ СПОСОБ: Выполнение SQL скрипта

**Проблема:** Не удается найти параметры подключения к БД

---

## 🎯 ВАРИАНТ 1: БД на удаленном сервере

Если PostgreSQL находится на другом сервере, нужно узнать его адрес:

```bash
# Проверить конфигурацию приложения
cat /opt/aladdin-backend/app/main.py
cat /opt/aladdin-backend/app/config.py 2>/dev/null

# Или проверить переменные окружения процесса
ps aux | grep python | grep aladdin
# Затем проверить переменные окружения процесса
```

---

## 🎯 ВАРИАНТ 2: Выполнить через Python приложение

Если приложение уже работает и подключено к БД, можно выполнить SQL через него:

```bash
# Создать скрипт который использует существующее подключение
cat > /tmp/execute_sql_via_app.py << 'EOF'
import sys
sys.path.insert(0, '/opt/aladdin-backend')

# Попробовать импортировать существующее подключение
try:
    from app.database import get_db, engine
    from sqlalchemy import text
    
    print("✅ Подключение к БД найдено")
    
    # Прочитать SQL файл
    with open('/tmp/REFERRAL_DB_SETUP.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Выполнить через engine
    with engine.connect() as conn:
        # Разделить на отдельные команды
        commands = [cmd.strip() for cmd in sql.split(';') if cmd.strip() and not cmd.strip().startswith('--')]
        
        for command in commands:
            if command:
                try:
                    conn.execute(text(command))
                    print(f"✅ Выполнено: {command[:50]}...")
                except Exception as e:
                    print(f"⚠️  Пропущено (возможно уже существует): {e}")
        
        conn.commit()
    
    print("\n✅ SQL скрипт выполнен!")
    
except ImportError as e:
    print(f"❌ Не удалось импортировать подключение: {e}")
    print("Нужно найти способ подключения вручную")
    sys.exit(1)
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

cd /opt/aladdin-backend
python3 /tmp/execute_sql_via_app.py
```

---

## 🎯 ВАРИАНТ 3: Ручной ввод параметров

Если знаете параметры подключения, можно выполнить напрямую:

```bash
# С параметрами подключения
psql -h IP_АДРЕС_СЕРВЕРА -p ПОРТ -U ПОЛЬЗОВАТЕЛЬ -d БАЗА_ДАННЫХ -f /tmp/REFERRAL_DB_SETUP.sql

# Пример:
# psql -h 192.168.1.100 -p 5432 -U aladdin_user -d aladdin_db -f /tmp/REFERRAL_DB_SETUP.sql
```

---

## 🎯 ВАРИАНТ 4: Проверить логи приложения

Если приложение работает, в логах могут быть параметры подключения:

```bash
# Проверить логи systemd
journalctl -u aladdin-backend -n 100 | grep -i database

# Или логи pm2
pm2 logs aladdin-backend --lines 100 | grep -i database

# Или файлы логов
find /opt/aladdin-backend -name '*.log' | xargs grep -i database | head -5
```

---

## 🔍 ДИАГНОСТИКА

Выполните для понимания структуры:

```bash
# 1. Структура проекта
ls -la /opt/aladdin-backend/
ls -la /opt/aladdin-backend/app/

# 2. main.py
cat /opt/aladdin-backend/app/main.py | head -100

# 3. Проверить процессы
ps aux | grep python | grep aladdin

# 4. Проверить переменные окружения процесса
# (замените PID на реальный PID процесса)
cat /proc/PID/environ | tr '\0' '\n' | grep -i db
```

---

После получения информации о структуре проекта и способе подключения к БД, мы сможем выполнить SQL скрипт правильным способом.

