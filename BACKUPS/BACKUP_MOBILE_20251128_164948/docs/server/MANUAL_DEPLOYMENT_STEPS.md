# 📋 РУЧНОЕ ВЫПОЛНЕНИЕ ШАГОВ НА СЕРВЕРЕ (без скрипта)

**Сервер:** 149.154.65.180  
**Пользователь:** root  
**Пароль:** Sergio675

---

## 🔐 ПОДКЛЮЧЕНИЕ К СЕРВЕРУ

```bash
ssh root@149.154.65.180
# Введите пароль: Sergio675
```

---

## 📋 ШАГ 1: ВЫПОЛНИТЬ SQL СКРИПТ

**Файл:** `/tmp/REFERRAL_DB_SETUP.sql`

### Вариант 1: Если знаете параметры БД

```bash
# Подключиться к PostgreSQL
psql -h localhost -U ваш_пользователь -d ваша_база_данных

# Выполнить скрипт
\i /tmp/REFERRAL_DB_SETUP.sql

# Или напрямую:
psql -h localhost -U ваш_пользователь -d ваша_база_данных -f /tmp/REFERRAL_DB_SETUP.sql
```

### Вариант 2: Если не знаете параметры

```bash
# Найти параметры подключения
cat /opt/aladdin-backend/.env | grep -i postgres
# или
cat /etc/postgresql/*/main/postgresql.conf | grep -i listen

# Попробовать стандартные варианты:
psql -h localhost -U postgres -d postgres -f /tmp/REFERRAL_DB_SETUP.sql
psql -h localhost -U aladdin -d aladdin -f /tmp/REFERRAL_DB_SETUP.sql
```

### Проверка:

```bash
psql -h localhost -U ваш_пользователь -d ваша_база_данных -c "\dt referral*"
```

**Ожидаемый результат:**
- Таблицы `referral_codes` и `referrals` созданы

---

## 📋 ШАГ 2: ИНТЕГРИРОВАТЬ API ENDPOINTS

**Файлы в `/tmp/`:**
- `REFERRAL_API_ENDPOINTS.py`
- `REFERRAL_REGISTRATION_HANDLER.py`
- `REFERRAL_PAYMENT_HANDLER.py`

### Действия:

```bash
# 1. Найти где находится FastAPI проект
cd /opt/aladdin-backend
# или
cd /var/www/aladdin
# или где у вас проект

# 2. Скопировать файлы в проект
cp /tmp/REFERRAL_API_ENDPOINTS.py app/routers/
cp /tmp/REFERRAL_REGISTRATION_HANDLER.py app/routers/
cp /tmp/REFERRAL_PAYMENT_HANDLER.py app/routers/

# 3. Открыть main.py и добавить роутеры
nano app/main.py
# или
vim app/main.py
```

### Добавить в `main.py`:

```python
from app.routers import referral_api, referral_registration, referral_payment

app.include_router(referral_api.router, prefix="/api", tags=["referral"])
app.include_router(referral_registration.router, prefix="/api", tags=["referral"])
app.include_router(referral_payment.router, prefix="/api", tags=["referral"])
```

### Перезапустить приложение:

```bash
# Если используется systemd:
systemctl restart aladdin-backend

# Если используется PM2:
pm2 restart aladdin-backend

# Если запущено вручную:
# Остановить процесс и запустить заново
```

---

## 📋 ШАГ 3: ПРИМЕНИТЬ NGINX КОНФИГУРАЦИЮ

**Файл:** `/tmp/nginx_referral.conf`

### Действия:

```bash
# 1. Сделать backup текущей конфигурации
cp /etc/nginx/sites-available/aladdin-ai.ru /etc/nginx/sites-available/aladdin-ai.ru.backup

# 2. Открыть текущую конфигурацию
nano /etc/nginx/sites-available/aladdin-ai.ru
# или
vim /etc/nginx/sites-available/aladdin-ai.ru

# 3. Добавить блок для /invite/{code}:
```

### Добавить в конфигурацию Nginx:

```nginx
location /invite/ {
    # Проксировать на Python backend для обработки кода
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Или отдавать статический файл invite.html
    # try_files $uri $uri/ /invite.html;
}

# Или проще - отдавать статический файл:
location ~ ^/invite/(.+)$ {
    root /var/www/aladdin-ai.ru;
    try_files /invite.html =404;
}
```

### Проверить и перезагрузить:

```bash
# Проверить конфигурацию
nginx -t

# Если все ОК - перезагрузить
systemctl reload nginx
```

---

## ✅ ПРОВЕРКА

### 1. Проверить базу данных:

```bash
psql -h localhost -U ваш_пользователь -d ваша_база_данных -c "SELECT * FROM referral_codes LIMIT 1;"
```

### 2. Проверить API:

```bash
curl https://aladdin-ai.ru/api/referral/code
# (нужна авторизация)
```

### 3. Проверить сайт:

```bash
curl https://aladdin-ai.ru/invite.html
curl https://aladdin-ai.ru/invite/ABC123
```

---

## 🆘 ЕСЛИ ЧТО-ТО НЕ РАБОТАЕТ

### Проблема: Не могу подключиться к БД

```bash
# Проверить что PostgreSQL запущен
systemctl status postgresql

# Проверить логи
tail -f /var/log/postgresql/postgresql-*.log
```

### Проблема: API не отвечает

```bash
# Проверить что FastAPI запущен
systemctl status aladdin-backend
# или
pm2 list

# Проверить логи
journalctl -u aladdin-backend -f
# или
pm2 logs aladdin-backend
```

### Проблема: Nginx не перезагружается

```bash
# Проверить синтаксис
nginx -t

# Посмотреть ошибки
tail -f /var/log/nginx/error.log
```

---

**Последнее обновление:** 22 ноября 2024


