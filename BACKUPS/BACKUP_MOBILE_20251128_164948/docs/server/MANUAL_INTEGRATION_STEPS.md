# 📋 РУЧНАЯ ИНТЕГРАЦИЯ: Пошаговые инструкции

**Дата:** 22 ноября 2024  
**Сервер:** 149.154.65.180

---

## ✅ ШАГ 1: Выполнить SQL скрипт (5 минут)

### Команды:

```bash
# 1. Подключиться к серверу
ssh root@149.154.65.180

# 2. Выполнить SQL скрипт (замените на ваши параметры БД)
psql -U ваш_пользователь -d ваша_база -f /tmp/REFERRAL_DB_SETUP.sql

# 3. Проверить что таблицы созданы
psql -U ваш_пользователь -d ваша_база -c "\dt referral*"

# 4. Проверить функции
psql -U ваш_пользователь -d ваша_база -c "\df get_or_create_referral_code"
```

### Ожидаемый результат:
- ✅ Таблица `referral_codes` создана
- ✅ Таблица `referrals` создана
- ✅ Таблица `referral_discounts` создана
- ✅ Функции созданы

---

## ✅ ШАГ 2: Интегрировать API endpoints (10 минут)

### 2.1: Найти файл main.py

```bash
# На сервере найти main.py
ssh root@149.154.65.180
find /opt/aladdin-backend -name "main.py" -type f
```

### 2.2: Добавить роутер в main.py

**Откройте файл:** `/opt/aladdin-backend/app/main.py` (или где находится ваш main.py)

**Добавьте импорт:**
```python
from app.routers.referral import router as referral_router
```

**Добавьте роутер в app:**
```python
app.include_router(referral_router, prefix="/api/referral", tags=["referral"])
```

**Пример полного кода:**
```python
from fastapi import FastAPI
from app.routers import some_router  # ваши существующие роутеры
from app.routers.referral import router as referral_router  # ✅ ДОБАВИТЬ

app = FastAPI()

app.include_router(some_router)  # ваши существующие роутеры
app.include_router(referral_router, prefix="/api/referral", tags=["referral"])  # ✅ ДОБАВИТЬ
```

### 2.3: Настроить авторизацию в referral.py

**Откройте файл:** `/opt/aladdin-backend/app/routers/referral.py`

**Найдите строки:**
```python
# TODO: Раскомментировать после настройки авторизации
# user = verify_token(token)
# user_id = user["id"]

user_id = 1  # Заменить на реальный user_id из токена
```

**Замените на:**
```python
# Раскомментируйте импорты в начале файла:
from app.auth import get_current_user  # или ваша функция авторизации
from app.database import get_db

# В каждом endpoint замените:
user = verify_token(token)  # Ваша функция проверки токена
if not user:
    raise HTTPException(status_code=401, detail="Unauthorized")
user_id = user["id"]
```

---

## ✅ ШАГ 3: Интегрировать функции в код оплаты (15 минут)

### 3.1: Найти файл обработки платежей

```bash
# На сервере найти файлы с платежами
ssh root@149.154.65.180
find /opt/aladdin-backend -name "*payment*.py" -type f
```

### 3.2: Добавить импорт в файл платежей

**Откройте файл с `/api/payments/create`** (например: `/opt/aladdin-backend/app/routers/payments.py`)

**Добавьте в начало файла:**
```python
from app.referral_payment_integration import (
    process_referral_code_on_payment,
    apply_referral_discount,
    process_referral_on_payment_confirmation
)
```

### 3.3: Модифицировать `/api/payments/create`

**Найдите функцию создания платежа:**
```python
@router.post("/api/payments/create")
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ... существующая логика ...
```

**Добавьте после создания платежа (перед return):**
```python
    # ... существующая логика создания платежа ...
    
    # ✅ ДОБАВИТЬ: Обработка реферального кода
    if hasattr(payment_data, 'referralCode') and payment_data.referralCode:
        referral_id = process_referral_code_on_payment(
            db, payment_data.referralCode, new_user_id, payment_data.amount
        )
    
    # ✅ ДОБАВИТЬ: Если это реферер (не приглашенный), применить скидку
    if not (hasattr(payment_data, 'referralCode') and payment_data.referralCode):
        calculated_price = calculate_price(payment_data.tariffId, payment_data.periodMonths)  # ваша функция
        final_amount = apply_referral_discount(db, current_user.id, calculated_price)
        payment_data.amount = final_amount
    
    # ... остальная логика ...
    return {"paymentId": payment.id, ...}
```

### 3.4: Модифицировать `/api/payments/status/{payment_id}`

**Найдите функцию проверки статуса:**
```python
@router.get("/api/payments/status/{payment_id}")
async def check_payment_status(
    payment_id: str,
    db: Session = Depends(get_db)
):
    payment = get_payment(payment_id, db)
    # ... существующая логика ...
```

**Добавьте после проверки статуса:**
```python
    # ... существующая логика проверки статуса ...
    
    if payment.status == 'paid':
        # ✅ ДОБАВИТЬ: Обработка реферальной программы
        process_referral_on_payment_confirmation(db, payment.user_id, payment.amount)
    
    return {"status": payment.status, ...}
```

---

## ✅ ШАГ 4: Настроить Nginx (5 минут)

### 4.1: Открыть конфигурацию Nginx

```bash
ssh root@149.154.65.180
nano /etc/nginx/sites-available/aladdin-ai.ru
```

### 4.2: Добавить блок location /invite/

**Найдите блок `server {` и добавьте внутри:**

**Вариант 1: Статический файл (если invite.html уже загружен):**
```nginx
location /invite/ {
    try_files $uri $uri/ /invite.html?code=$1;
}
```

**Вариант 2: Прокси на Python backend:**
```nginx
location /invite/ {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### 4.3: Проверить и перезагрузить Nginx

```bash
# Проверить конфигурацию
nginx -t

# Если все ОК, перезагрузить
systemctl reload nginx
```

---

## ✅ ШАГ 5: Перезапустить FastAPI приложение (2 минуты)

### Вариант 1: systemd

```bash
ssh root@149.154.65.180
systemctl restart aladdin-backend
systemctl status aladdin-backend
```

### Вариант 2: pm2

```bash
ssh root@149.154.65.180
pm2 restart aladdin-backend
pm2 status
```

### Вариант 3: Вручную

```bash
# Найти процесс
ps aux | grep uvicorn

# Остановить и запустить заново
# (зависит от вашей конфигурации)
```

---

## ✅ ПРОВЕРКА РАБОТЫ

### 1. Проверить базу данных:

```bash
ssh root@149.154.65.180
psql -U ваш_пользователь -d ваша_база

# В psql:
SELECT * FROM referral_codes LIMIT 5;
SELECT * FROM referrals LIMIT 5;
SELECT * FROM referral_discounts LIMIT 5;
\q
```

### 2. Проверить API endpoints:

```bash
# С авторизацией (замените YOUR_TOKEN на реальный токен)
curl -H "Authorization: Bearer YOUR_TOKEN" https://aladdin-ai.ru/api/referral/code
curl -H "Authorization: Bearer YOUR_TOKEN" https://aladdin-ai.ru/api/referral/stats
```

### 3. Проверить landing страницу:

```
Откройте в браузере:
https://aladdin-ai.ru/invite/ABC123
```

---

## 📝 ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **Авторизация:** Убедитесь, что функция `verify_token()` правильно работает
2. **База данных:** Проверьте что таблица `users` существует перед созданием `referral_codes`
3. **Транзакции:** Функции уже используют транзакции БД
4. **Ошибки:** Функции обрабатывают ошибки gracefully

---

## 🎯 ГОТОВНОСТЬ

После выполнения всех шагов:
- ✅ База данных: 100%
- ✅ API Endpoints: 100%
- ✅ Обработка оплаты: 100%
- ✅ Landing страница: 100%
- ✅ Nginx: 100%

**Итого: 100% готовность серверной части!**


