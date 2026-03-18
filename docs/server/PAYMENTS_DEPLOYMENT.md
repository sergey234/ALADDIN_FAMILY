# 🚀 Инструкция по развертыванию системы платежей

## 📋 Шаги развертывания

### 1. Создание таблиц в БД

**На сервере:**
```bash
ssh root@149.154.65.180
cd /opt/aladdin-backend
PGPASSWORD="${ALADDIN_DB_PASSWORD}" psql -h localhost -U aladdin_user -d aladdin_db -f docs/server/PAYMENTS_DB_SETUP.sql
```
**SECURITY:** Не хранить пароль БД в репозитории. Используйте переменную окружения:
```bash
PGPASSWORD="${ALADDIN_DB_PASSWORD}" psql -h localhost -U aladdin_user -d aladdin_db -f docs/server/PAYMENTS_DB_SETUP.sql
```

**Или через expect (для ML системы):**
```bash
expect -c "
set timeout 60
# SECURITY: не хранить SSH/DB пароли в репозитории. Используйте секреты/ENV.
set password \"$env(ALADDIN_SSH_PASSWORD)\"
set db_password \"$env(ALADDIN_DB_PASSWORD)\"
spawn ssh root@149.154.65.180 \"cd /opt/aladdin-backend && PGPASSWORD='\$db_password' psql -h localhost -U aladdin_user -d aladdin_db -f docs/server/PAYMENTS_DB_SETUP.sql\"
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### 2. Копирование файла payments.py на сервер

**Через scp:**
```bash
scp docs/server/payments.py root@149.154.65.180:/opt/aladdin-backend/app/routers/payments.py
```

**Или через expect:**
```bash
expect -c "
set timeout 60
set password \"$env(ALADDIN_SSH_PASSWORD)\"
spawn scp docs/server/payments.py root@149.154.65.180:/opt/aladdin-backend/app/routers/payments.py
expect \"password:\" { send \"\$password\\r\" }
expect eof
"
```

### 3. Обновление main.py на сервере

**На сервере:**
```bash
ssh root@149.154.65.180
cd /opt/aladdin-backend
nano main.py
# Добавить:
# from app.routers import payments
# app.include_router(payments.router, tags=["payments"])
```

### 4. Перезапуск backend

**На сервере:**
```bash
systemctl restart aladdin-backend
# Или если запущен вручную:
cd /opt/aladdin-backend
source venv/bin/activate
pkill -f uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
```

### 5. Проверка работы

**Проверка health:**
```bash
curl http://149.154.65.180:8000/api/health
```

**Проверка создания платежа:**
```bash
curl -X POST http://149.154.65.180:8000/api/payments/create \
  -H "Content-Type: application/json" \
  -d '{
    "tariffId": "family",
    "userAlias": "testuser",
    "pin": "1234",
    "paymentMethod": "qr_sbp",
    "periodMonths": 1,
    "amount": 800.0,
    "referralCode": "ABC123"
  }'
```

## ✅ Чеклист

- [ ] Таблицы `payments` и `payment_methods` созданы
- [ ] Файл `payments.py` скопирован на сервер
- [ ] `main.py` обновлен (добавлен импорт и router)
- [ ] Backend перезапущен
- [ ] Endpoints работают (проверка через curl)

## 📝 Примечания

- Endpoints работают без авторизации (для анонимных платежей с лендинга)
- Реферальная программа обрабатывается автоматически при наличии `referralCode`
- Если `user_id` отсутствует, реферальная программа будет обработана позже при подтверждении платежа


