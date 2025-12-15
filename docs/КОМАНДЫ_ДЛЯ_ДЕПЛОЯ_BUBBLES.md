# 🚀 КОМАНДЫ ДЛЯ ДЕПЛОЯ LOCATION BUBBLE AGENT

**Дата:** 12 декабря 2025  
**Статус:** ✅ Готово к выполнению

---

## 📋 ВСЕ КОМАНДЫ В ОДНОМ МЕСТЕ

### Шаг 1: Копирование файлов на сервер

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS

# Агент
scp security/ai_agents/location_bubble_agent.py \
    root@149.154.65.180:/opt/aladdin-backend/security/ai_agents/

# API Router
scp security/api/routers/location_bubble_router.py \
    root@149.154.65.180:/opt/aladdin-backend/security/api/routers/

# Registry entry
scp security/ai_agents/function_registry_entry_location_bubble.json \
    root@149.154.65.180:/tmp/

# Скрипты
scp register_location_bubble_in_sfm.py root@149.154.65.180:/tmp/
scp add_location_bubble_to_main.py root@149.154.65.180:/tmp/
```

**Пароль:** `Sergio675`

---

### Шаг 2: Подключение к серверу и регистрация в SFM

```bash
ssh root@149.154.65.180
# Пароль: Sergio675

cd /tmp
python3 register_location_bubble_in_sfm.py
```

**Ожидаемый вывод:**
```
=== РЕГИСТРАЦИЯ LOCATION BUBBLE AGENT В SFM ===

✅ Запись загружена: location_bubble_agent
✅ Backup создан: /opt/aladdin-backend/data/sfm/function_registry_backup_YYYYMMDD_HHMMSS.json
✅ Агент зарегистрирован в SFM
   - Всего агентов: X
   - Всего функций: X
   - Всего API endpoints: X
   - Функций Location Bubble Agent: 5
   - API endpoints Location Bubble Agent: 6
```

---

### Шаг 3: Интеграция в main.py

```bash
# На сервере
python3 add_location_bubble_to_main.py
```

**Ожидаемый вывод:**
```
=== ИНТЕГРАЦИЯ LOCATION BUBBLE ROUTER В MAIN.PY ===

✅ Найден main.py: /opt/aladdin-backend/api/main.py
✅ Backup создан: /opt/aladdin-backend/api/main.py.backup_YYYYMMDD_HHMMSS
✅ Импорт добавлен
✅ Регистрация router добавлена
✅ Синтаксис проверен

✅ Интеграция завершена!
   - Импорт: from security.api.routers.location_bubble_router import router as location_bubble_router
   - Регистрация: app.include_router(location_bubble_router)
```

---

### Шаг 4: Перезапуск сервиса

```bash
# На сервере
systemctl restart aladdin-backend
systemctl status aladdin-backend
```

---

### Шаг 5: Проверка работы

```bash
# На сервере
curl http://localhost:8000/api/location/bubble/health
```

**Ожидаемый ответ:**
```json
{
  "status": "healthy",
  "agent": "location_bubble_agent",
  "version": "1.0.0",
  "timestamp": "2025-12-12T..."
}
```

---

## ✅ ПРОВЕРКА ДЕПЛОЯ

```bash
# На сервере

# 1. Проверка файлов
ls -lh /opt/aladdin-backend/security/ai_agents/location_bubble_agent.py
ls -lh /opt/aladdin-backend/security/api/routers/location_bubble_router.py

# 2. Проверка регистрации в SFM
grep -A 5 "location_bubble_agent" /opt/aladdin-backend/data/sfm/function_registry.json

# 3. Проверка импорта в main.py
grep "location_bubble_router" /opt/aladdin-backend/api/main.py
# или
grep "location_bubble_router" /opt/aladdin-backend/main.py

# 4. Проверка логов
journalctl -u aladdin-backend -n 50 | grep -i "location_bubble"

# 5. Проверка health endpoint
curl -s http://localhost:8000/api/location/bubble/health | python3 -m json.tool
```

---

## 🔧 ЕСЛИ ЧТО-ТО ПОШЛО НЕ ТАК

### Восстановление из backup:

```bash
# На сервере

# Восстановление SFM registry
cp /opt/aladdin-backend/data/sfm/function_registry_backup_*.json \
   /opt/aladdin-backend/data/sfm/function_registry.json

# Восстановление main.py
cp /opt/aladdin-backend/api/main.py.backup_* \
   /opt/aladdin-backend/api/main.py
# или
cp /opt/aladdin-backend/main.py.backup_* \
   /opt/aladdin-backend/main.py
```

---

**Все готово! Выполните команды по порядку.** 🚀
