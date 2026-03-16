# 🚀 ДЕПЛОЙ ИСПРАВЛЕНИЯ ЧЕРЕЗ NGINX + SSL + SYSTEMD

## 📋 Архитектура сервера

**Сервер:** 149.154.65.180  
**Веб-сервер:** Nginx (порт 443 HTTPS)  
**Backend:** FastAPI/Uvicorn (порт 8000/8002)  
**Управление:** systemd  
**SSL:** Let's Encrypt / самоподписанный сертификат

---

## 🎯 ЦЕЛЬ ДЕПЛОЯ

**Файл для обновления:** `/opt/aladdin-backend/app/auth/auth.py`

**Что исправлено:**
- Добавлена поддержка поля `sub` в JWT токенах (для device tokens)
- Сохранена обратная совместимость с `user_id` и `id`
- Приоритет: `user_id` > `id` > `sub`

---

## 🔧 МЕТОДЫ ДЕПЛОЯ

### МЕТОД 1: Через SSH (если доступен)

#### Шаг 1: Подключение
```bash
ssh root@149.154.65.180
# Пароль: Sergio675
```

#### Шаг 2: Создание backup
```bash
cd /opt/aladdin-backend/app/auth
cp auth.py auth.py.backup_$(date +%Y%m%d_%H%M%S)
```

#### Шаг 3: Загрузка файла
```bash
# На локальной машине:
scp app/auth/auth.py root@149.154.65.180:/opt/aladdin-backend/app/auth/auth.py

# Или через SFTP:
sftp root@149.154.65.180
put app/auth/auth.py /opt/aladdin-backend/app/auth/auth.py
exit
```

#### Шаг 4: Проверка синтаксиса
```bash
python3 -m py_compile /opt/aladdin-backend/app/auth/auth.py
```

#### Шаг 5: Перезапуск через systemd
```bash
# Найти имя сервиса
systemctl list-units --type=service | grep -i aladdin

# Перезапустить (примеры имен):
systemctl restart aladdin-backend
# ИЛИ
systemctl restart aladdin-backend.service
# ИЛИ
systemctl restart aladdin

# Проверить статус
systemctl status aladdin-backend --no-pager -l
```

#### Шаг 6: Проверка через HTTPS
```bash
curl -k https://aladdin-ai.ru/api/health
```

---

### МЕТОД 2: Через веб-интерфейс управления (если есть)

Если на сервере есть веб-интерфейс для управления файлами (например, через Nginx или панель управления):

1. **Войти в веб-интерфейс:**
   - URL: `https://149.154.65.180:8443` или другой порт
   - Логин: `root`
   - Пароль: `Sergio675`

2. **Перейти в файловый менеджер:**
   - Путь: `/opt/aladdin-backend/app/auth/`

3. **Создать backup:**
   - Скопировать `auth.py` → `auth.py.backup_YYYYMMDD_HHMMSS`

4. **Загрузить новый файл:**
   - Загрузить локальный `app/auth/auth.py`
   - Заменить существующий `auth.py`

5. **Перезапустить через терминал веб-интерфейса:**
   ```bash
   systemctl restart aladdin-backend
   ```

---

### МЕТОД 3: Через Git (если используется)

Если код хранится в Git репозитории:

```bash
# На сервере:
cd /opt/aladdin-backend
git pull origin main  # или другая ветка

# Проверить изменения
git diff app/auth/auth.py

# Перезапустить
systemctl restart aladdin-backend
```

---

### МЕТОД 4: Через Nginx upload модуль (если настроен)

Если на сервере настроен модуль загрузки файлов через Nginx:

1. **Загрузить файл через веб-форму:**
   - URL: `https://aladdin-ai.ru/upload` (если настроен)
   - Выбрать файл: `app/auth/auth.py`
   - Указать путь: `/opt/aladdin-backend/app/auth/auth.py`

2. **Перезапустить через SSH или веб-интерфейс**

---

## 🔍 ПРОВЕРКА СТРУКТУРЫ СЕРВЕРА

### Проверка systemd сервисов

```bash
# Список всех сервисов
systemctl list-units --type=service --all

# Поиск сервисов ALADDIN
systemctl list-units --type=service | grep -i aladdin

# Проверка конкретного сервиса
systemctl status aladdin-backend
systemctl status aladdin
systemctl status backend
```

### Проверка Nginx конфигурации

```bash
# Конфигурация Nginx
cat /etc/nginx/sites-available/aladdin-ai.ru
# ИЛИ
cat /etc/nginx/conf.d/aladdin.conf

# Проверка конфигурации
nginx -t

# Перезагрузка Nginx (если нужно)
systemctl reload nginx
```

### Проверка процессов backend

```bash
# Поиск процессов uvicorn
ps aux | grep uvicorn

# Поиск процессов Python
ps aux | grep python | grep aladdin

# Проверка портов
netstat -tlnp | grep 8000
netstat -tlnp | grep 8002
```

---

## 📝 ПРОВЕРКА ИСПРАВЛЕНИЯ

### После деплоя проверить:

1. **Синтаксис Python:**
   ```bash
   python3 -m py_compile /opt/aladdin-backend/app/auth/auth.py
   ```

2. **Содержимое файла (должна быть строка с `sub`):**
   ```bash
   grep -n "sub" /opt/aladdin-backend/app/auth/auth.py
   ```
   
   Должны быть строки:
   ```
   71:    if "user_id" not in payload and "id" not in payload and "sub" not in payload:
   80:    user_id = payload.get("user_id") or payload.get("id") or payload.get("sub")
   ```

3. **Логи systemd:**
   ```bash
   journalctl -u aladdin-backend -n 50 --no-pager
   ```

4. **Тест через HTTPS:**
   ```bash
   curl -k https://aladdin-ai.ru/api/health
   curl -H "Authorization: Bearer YOUR_TOKEN" https://aladdin-ai.ru/api/family/stats
   ```

---

## 🚨 ОТКАТ (если что-то пошло не так)

```bash
# Восстановить backup
cd /opt/aladdin-backend/app/auth
cp auth.py.backup_* auth.py

# Перезапустить сервис
systemctl restart aladdin-backend

# Проверить статус
systemctl status aladdin-backend
```

---

## 📊 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После успешного деплоя:

- ✅ `/api/family/stats` возвращает `200 OK` вместо `401`
- ✅ Device tokens (с полем `sub`) работают корректно
- ✅ User tokens (с полями `user_id` или `id`) продолжают работать
- ✅ Логи systemd показывают успешный запуск сервиса
- ✅ Nginx проксирует запросы к backend без ошибок

---

## 🔗 СВЯЗАННЫЕ ФАЙЛЫ

- **Локальный файл:** `app/auth/auth.py`
- **Серверный файл:** `/opt/aladdin-backend/app/auth/auth.py`
- **Backup:** `/opt/aladdin-backend/app/auth/auth.py.backup_*`
- **Логи:** `journalctl -u aladdin-backend`

---

**Дата:** 16 марта 2026  
**Build:** 121  
**Статус:** ✅ Готово к деплою
