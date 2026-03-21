# ✅ ЧЕКЛИСТ ДЕПЛОЯ: 4 файла для исправления JWT 401

**Дата:** 2026-03-17  
**Статус:** 🚀 **В ПРОЦЕССЕ**

---

## 📋 СПИСОК ДЕЛ ДЛЯ ВЫПОЛНЕНИЯ

### ✅ **ШАГ 1: ПРОВЕРКА ТЕКУЩЕГО СОСТОЯНИЯ НА СЕРВЕРЕ**

**Задача:** Проверить, есть ли уже исправления на сервере

**Команды для выполнения на сервере:**
```bash
cd /opt/aladdin-backend

# Проверка 1: app/auth/auth.py
echo "=== Проверка app/auth/auth.py ==="
grep "aladdin-super-secret-key-change-in-production" app/auth/auth.py && echo "✅ JWT_SECRET найден" || echo "❌ JWT_SECRET НЕ найден"
grep "leeway=60" app/auth/auth.py && echo "✅ leeway найден" || echo "❌ leeway НЕ найден"
grep "JWT-003" app/auth/auth.py && echo "✅ Логирование найдено" || echo "❌ Логирование НЕ найдено"

# Проверка 2: backend/app/services/jwt_service.py
echo
echo "=== Проверка backend/app/services/jwt_service.py ==="
grep "aladdin-super-secret-key-change-in-production" backend/app/services/jwt_service.py && echo "✅ SECRET_KEY найден" || echo "❌ SECRET_KEY НЕ найден"
grep "leeway=60" backend/app/services/jwt_service.py && echo "✅ leeway найден" || echo "❌ leeway НЕ найден"
grep "import os" backend/app/services/jwt_service.py && echo "✅ import os найден" || echo "❌ import os НЕ найден"

# Проверка 3: app/auth/__init__.py
echo
echo "=== Проверка app/auth/__init__.py ==="
grep "aladdin-super-secret-key-change-in-production" app/auth/__init__.py && echo "✅ JWT_SECRET найден" || echo "❌ JWT_SECRET НЕ найден"

# Проверка 4: app/routers/analytics_router.py
echo
echo "=== Проверка app/routers/analytics_router.py ==="
grep "from app.auth.auth import get_current_user" app/routers/analytics_router.py && echo "✅ Правильный импорт найден" || echo "❌ Правильный импорт НЕ найден"
grep -A 5 "except ImportError:" app/routers/analytics_router.py | grep "get_current_user" && echo "❌ Fallback найден (не должно быть!)" || echo "✅ Fallback удален"
```

**Результат:**
- Если все ✅ - исправления уже на сервере, ничего делать не нужно
- Если есть ❌ - нужно задеплоить недостающие файлы

---

### ✅ **ШАГ 2: СОЗДАНИЕ BACKUP**

**Задача:** Создать backup текущих файлов на сервере

**Команды:**
```bash
cd /opt/aladdin-backend

# Создать директорию для backup
mkdir -p /opt/aladdin-backend/backup_jwt_fix_$(date +%Y%m%d_%H%M%S)

# Backup файлов
cp app/auth/auth.py /opt/aladdin-backend/backup_jwt_fix_*/auth.py.backup
cp backend/app/services/jwt_service.py /opt/aladdin-backend/backup_jwt_fix_*/jwt_service.py.backup
cp app/auth/__init__.py /opt/aladdin-backend/backup_jwt_fix_*/__init__.py.backup
cp app/routers/analytics_router.py /opt/aladdin-backend/backup_jwt_fix_*/analytics_router.py.backup

echo "✅ Backup создан в /opt/aladdin-backend/backup_jwt_fix_*/"
```

---

### ✅ **ШАГ 3: ДЕПЛОЙ ФАЙЛОВ**

**Задача:** Задеплоить 4 исправленных файла на сервер

**Файлы для деплоя:**

1. **app/auth/auth.py**
   - Путь на сервере: `/opt/aladdin-backend/app/auth/auth.py`
   - Изменения:
     - JWT_SECRET: `"aladdin-super-secret-key-change-in-production"`
     - Leeway: `leeway=60`
     - Логирование: детальное (JWT-003)

2. **backend/app/services/jwt_service.py**
   - Путь на сервере: `/opt/aladdin-backend/backend/app/services/jwt_service.py`
   - Изменения:
     - SECRET_KEY: `os.getenv("JWT_SECRET", "aladdin-super-secret-key-change-in-production")`
     - import os: добавлен
     - Leeway: `leeway=60`
     - Логирование: детальное (JWT-003)

3. **app/auth/__init__.py**
   - Путь на сервере: `/opt/aladdin-backend/app/auth/__init__.py`
   - Изменения:
     - JWT_SECRET: `"aladdin-super-secret-key-change-in-production"` (было: `"your-secret-key-change-in-production"`)

4. **app/routers/analytics_router.py**
   - Путь на сервере: `/opt/aladdin-backend/app/routers/analytics_router.py`
   - Изменения:
     - Удален fallback `get_current_user`
     - Используется: `from app.auth.auth import get_current_user`

**Метод деплоя:**
- Через git (если используется)
- Через scp/rsync
- Через прямой копирование файлов

---

### ✅ **ШАГ 4: ПЕРЕЗАПУСК СЕРВЕРА**

**Задача:** Перезапустить FastAPI приложение

**Команды (выбрать подходящий):**
```bash
# Вариант 1: systemd
sudo systemctl restart aladdin-api
sudo systemctl status aladdin-api

# Вариант 2: pm2
pm2 restart aladdin-api
pm2 status aladdin-api

# Вариант 3: supervisor
supervisorctl restart aladdin-api
supervisorctl status aladdin-api

# Вариант 4: Прямой перезапуск
pkill -f "uvicorn.*aladdin"
# Затем запустить заново
```

---

### ✅ **ШАГ 5: ТЕСТИРОВАНИЕ ПОСЛЕ ДЕПЛОЯ**

**Задача:** Протестировать все 75 защищенных эндпоинтов

**Команда:**
```bash
cd /path/to/ALADDIN_iOS
python3 docs/server/test_protected_endpoints_jwt_fix.py
```

**Ожидаемый результат:**
- ✅ Успешно: ~73 эндпоинта (96%)
- ⚠️ Валидация (422): ~12 эндпоинтов (16%)
- 🔴 401 ошибка: ~0 эндпоинтов (0%)
- ❓ Другие ошибки: ~3 эндпоинта (4%)

---

### ✅ **ШАГ 6: ПРОВЕРКА ЛОГОВ СЕРВЕРА**

**Задача:** Проверить логи сервера на наличие ошибок 401

**Команды:**
```bash
# Проверить логи FastAPI
tail -f /var/log/aladdin-api.log | grep -i "401\|unauthorized\|jwt-003"

# Или проверить системные логи
journalctl -u aladdin-api -f | grep -i "401\|unauthorized\|jwt-003"
```

**Что искать:**
- ✅ Успешное декодирование токенов: `✅ [JWT-003] decode_token: Успешно декодирован токен`
- ❌ Ошибки декодирования: `❌ [JWT-003] decode_token: Invalid token`

---

### ✅ **ШАГ 7: СОЗДАНИЕ ФИНАЛЬНОГО ОТЧЕТА**

**Задача:** Создать отчет о результатах деплоя

**Содержание отчета:**
- Статус деплоя каждого файла
- Результаты тестирования
- Количество успешных/неуспешных эндпоинтов
- Рекомендации

---

## 📊 ПРОГРЕСС ВЫПОЛНЕНИЯ

- [ ] Шаг 1: Проверка текущего состояния на сервере
- [ ] Шаг 2: Создание backup
- [ ] Шаг 3: Деплой 4 файлов
- [ ] Шаг 4: Перезапуск сервера
- [ ] Шаг 5: Тестирование после деплоя
- [ ] Шаг 6: Проверка логов сервера
- [ ] Шаг 7: Создание финального отчета

---

**Статус:** 🚀 **ГОТОВО К ВЫПОЛНЕНИЮ**
