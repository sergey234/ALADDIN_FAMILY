# ✅ ИТОГОВЫЙ ОТЧЕТ: Исправление 401 ошибки для `/api/family/stats` (BUILD 121)

## 📋 Статус исправления

### ✅ Локально исправлено

- ✅ `app/auth/auth.py` - исправлено
- ✅ `docs/server/auth.py` - исправлено
- ✅ Исправление протестировано локально
- ✅ Обратная совместимость сохранена

### ⏳ Ожидает деплоя на сервер

**Проблема:** SSH порт 22 недоступен (таймаут), автоматический деплой невозможен.

**Решение:** Использовать ручной деплой (см. инструкции ниже).

---

## 🔍 Что было исправлено

### Проблема
Серверный код `get_current_user` проверял только поля `user_id` или `id` в JWT payload, но device tokens используют поле `sub` (subject).

### Исправление
Добавлена поддержка поля `sub` с приоритетом: `user_id` > `id` > `sub`

**Было:**
```python
if "user_id" not in payload and "id" not in payload:
    raise HTTPException(...)
user_id = payload.get("user_id") or payload.get("id")
```

**Стало:**
```python
if "user_id" not in payload and "id" not in payload and "sub" not in payload:
    raise HTTPException(...)
user_id = payload.get("user_id") or payload.get("id") or payload.get("sub")
```

---

## 🚀 Инструкции по деплою

### Вариант 1: Через SCP (если SSH доступен)

```bash
cd /Users/sergejhlystov/ALADDIN_NEW/ALADDIN_NEW/mobile_apps/ALADDIN_iOS
scp app/auth/auth.py root@149.154.65.180:/opt/aladdin-backend/app/auth/auth.py
# Пароль: Sergio675
```

### Вариант 2: Через SSH + ручное редактирование

```bash
# 1. Подключиться к серверу
ssh root@149.154.65.180
# Пароль: Sergio675

# 2. Создать backup
cp /opt/aladdin-backend/app/auth/auth.py /opt/aladdin-backend/app/auth/auth.py.backup_$(date +%Y%m%d_%H%M%S)

# 3. Открыть файл
nano /opt/aladdin-backend/app/auth/auth.py

# 4. Найти строки 69-80 и заменить на исправленный код (см. выше)

# 5. Сохранить (Ctrl+O, Enter, Ctrl+X)

# 6. Проверить синтаксис
python3 -m py_compile /opt/aladdin-backend/app/auth/auth.py

# 7. Перезапустить сервер
systemctl restart aladdin-backend
# ИЛИ
pm2 restart aladdin-backend
```

### Вариант 3: Через SFTP клиент

1. Подключиться через FileZilla/Cyberduck:
   - Host: `149.154.65.180`
   - Port: `22` (или другой, если изменен)
   - Username: `root`
   - Password: `Sergio675`

2. Перейти в `/opt/aladdin-backend/app/auth/`

3. Создать backup `auth.py`

4. Загрузить локальный файл `app/auth/auth.py`

5. Перезапустить сервер через SSH

---

## 📁 Файлы для деплоя

**Локальный файл:** `app/auth/auth.py`  
**Путь на сервере:** `/opt/aladdin-backend/app/auth/auth.py`

**Изменения в файле:**
- Строки 69-80: Добавлена поддержка поля `sub` в JWT payload

---

## 🧪 Тестирование после деплоя

```bash
# 1. Проверить что сервер работает
curl https://aladdin-ai.ru/api/health

# 2. Проверить /api/family/stats с device token
curl -H "Authorization: Bearer YOUR_DEVICE_TOKEN" https://aladdin-ai.ru/api/family/stats

# Ожидается: 200 OK с данными статистики семьи
# Было: 401 Unauthorized
```

---

## ✅ Ожидаемый результат

После деплоя:
- ✅ `/api/family/stats` будет работать с device tokens (с полем `sub`)
- ✅ Обратная совместимость сохранена (user tokens с `user_id` или `id` продолжают работать)
- ✅ Приоритет: `user_id` > `id` > `sub`

---

## 📝 Дополнительные документы

- `docs/ИСПРАВЛЕНИЕ_401_FAMILY_STATS.md` - детальное описание проблемы
- `docs/ПЛАН_ДЕПЛОЯ_ИСПРАВЛЕНИЯ_401.md` - план деплоя
- `docs/РУЧНОЙ_ДЕПЛОЙ_ИСПРАВЛЕНИЯ_401.md` - инструкции по ручному деплою

---

## 🔧 Скрипты для деплоя

Созданы скрипты для автоматического деплоя (требуют доступ к SSH):
- `deploy_auth_fix.sh` - bash скрипт
- `deploy_auth_fix.py` - Python скрипт

**Примечание:** Скрипты не могут выполниться автоматически из-за недоступности SSH порта 22. Используйте ручной деплой.

---

**Дата:** 16 марта 2026  
**Build:** 121  
**Статус:** ✅ Готово к деплою (требуется ручной деплой)
