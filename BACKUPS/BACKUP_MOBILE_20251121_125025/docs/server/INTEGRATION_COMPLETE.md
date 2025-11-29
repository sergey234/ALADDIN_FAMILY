# ✅ ИНТЕГРАЦИЯ ЗАВЕРШЕНА: Реферальная программа

**Дата:** 22 ноября 2024  
**Сервер:** 149.154.65.180  
**Статус:** Файлы загружены, требуется ручная настройка

---

## ✅ ЧТО УЖЕ СДЕЛАНО АВТОМАТИЧЕСКИ

### 1. SQL скрипт загружен
- **Путь:** `/tmp/REFERRAL_DB_SETUP.sql`
- **Статус:** ✅ Загружен на сервер
- **Действие:** Требуется выполнение для создания таблиц

### 2. Python файлы загружены
- **REFERRAL_API_ENDPOINTS.py** → `/opt/aladdin-backend/app/routers/referral.py`
- **REFERRAL_PAYMENT_INTEGRATION.py** → `/opt/aladdin-backend/app/referral_payment_integration.py`
- **REFERRAL_SERVER_IMPLEMENTATION.py** → `/opt/aladdin-backend/app/referral_implementation.py`
- **Статус:** ✅ Все файлы загружены

### 3. Landing страница загружена
- **Путь:** `/var/www/aladdin-ai.ru/invite.html`
- **Статус:** ✅ Загружена, права настроены (644)

### 4. Nginx конфигурация загружена
- **Путь:** `/tmp/nginx_referral.conf`
- **Статус:** ✅ Готова к добавлению в конфигурацию

---

## ⚠️ ЧТО НУЖНО СДЕЛАТЬ ВРУЧНУЮ

### ШАГ 1: Выполнить SQL скрипт (5 минут)

```bash
# Подключиться к серверу
ssh root@149.154.65.180

# Выполнить SQL скрипт (замените на ваши параметры БД)
psql -U ваш_пользователь -d ваша_база -f /tmp/REFERRAL_DB_SETUP.sql

# Проверить что таблицы созданы
psql -U ваш_пользователь -d ваша_база -c "\dt referral*"
```

**Ожидаемый результат:**
- ✅ Таблица `referral_codes` создана
- ✅ Таблица `referrals` создана
- ✅ Таблица `referral_discounts` создана
- ✅ Функции `get_or_create_referral_code()` созданы

---

### ШАГ 2: Интегрировать API endpoints (10 минут)

**Файл:** `/opt/aladdin-backend/app/routers/referral.py`

```python
# В вашем main.py или routers/__init__.py:

from app.routers.referral import router as referral_router

app.include_router(referral_router, prefix="/api/referral", tags=["referral"])
```

**Настройка авторизации:**
```python
# В referral.py раскомментировать и настроить:
from app.auth import get_current_user
from app.database import get_db

# Заменить заглушки на реальную проверку токена
user = verify_token(token)  # Ваша функция
user_id = user["id"]
```

---

### ШАГ 3: Интегрировать функции в код оплаты (15 минут)

**Файл:** `/opt/aladdin-backend/app/referral_payment_integration.py`

#### 3.1: В `/api/payments/create`

```python
from app.referral_payment_integration import process_referral_code_on_payment, apply_referral_discount

@router.post("/api/payments/create")
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ... существующая логика ...
    
    # ✅ ДОБАВИТЬ: Обработка реферального кода
    referral_id = process_referral_code_on_payment(
        db, payment_data.referralCode, new_user_id, payment_data.amount
    )
    
    # ✅ ДОБАВИТЬ: Если это реферер, применить скидку
    if not payment_data.referralCode:
        calculated_price = calculate_price(payment_data.tariffId, payment_data.periodMonths)
        final_amount = apply_referral_discount(db, current_user.id, calculated_price)
        payment_data.amount = final_amount
    
    # ... остальная логика ...
```

#### 3.2: В `/api/payments/status/{payment_id}`

```python
from app.referral_payment_integration import process_referral_on_payment_confirmation

@router.get("/api/payments/status/{payment_id}")
async def check_payment_status(
    payment_id: str,
    db: Session = Depends(get_db)
):
    payment = get_payment(payment_id, db)
    
    # ... существующая логика ...
    
    if payment.status == 'paid':
        # ✅ ДОБАВИТЬ: Обработка реферальной программы
        process_referral_on_payment_confirmation(db, payment.user_id, payment.amount)
    
    return {"status": payment.status, ...}
```

---

### ШАГ 4: Настроить Nginx (5 минут)

```bash
# Подключиться к серверу
ssh root@149.154.65.180

# Открыть конфигурацию
nano /etc/nginx/sites-available/aladdin-ai.ru

# Добавить блок (из /tmp/nginx_referral.conf):
location /invite/ {
    try_files $uri $uri/ /invite.html?code=$1;
}

# Или если используете Python backend:
location /invite/ {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

# Проверить конфигурацию
nginx -t

# Перезагрузить Nginx
systemctl reload nginx
```

---

### ШАГ 5: Перезапустить FastAPI приложение (2 минуты)

```bash
# Вариант 1: systemd
systemctl restart aladdin-backend

# Вариант 2: pm2
pm2 restart aladdin-backend

# Вариант 3: Вручную
# Остановить и запустить приложение
```

---

## ✅ ПРОВЕРКА РАБОТЫ

### 1. Проверить базу данных:
```sql
SELECT * FROM referral_codes LIMIT 5;
SELECT * FROM referrals LIMIT 5;
SELECT * FROM referral_discounts LIMIT 5;
```

### 2. Проверить API endpoints:
```bash
# С авторизацией
curl -H "Authorization: Bearer YOUR_TOKEN" https://aladdin-ai.ru/api/referral/code
curl -H "Authorization: Bearer YOUR_TOKEN" https://aladdin-ai.ru/api/referral/stats
```

### 3. Проверить landing страницу:
```
https://aladdin-ai.ru/invite/ABC123
```

---

## 📊 ИТОГОВЫЙ СТАТУС

### ✅ Готово (автоматически):
- ✅ SQL скрипт загружен
- ✅ Python файлы загружены
- ✅ Landing страница загружена
- ✅ Nginx конфигурация загружена

### ⚠️ Требуется ручная настройка:
- ⚠️ Выполнить SQL скрипт
- ⚠️ Интегрировать API endpoints
- ⚠️ Интегрировать функции в код оплаты
- ⚠️ Настроить Nginx
- ⚠️ Перезапустить FastAPI

---

## 📖 ДОПОЛНИТЕЛЬНЫЕ МАТЕРИАЛЫ

- **Руководство по интеграции:** `REFERRAL_INTEGRATION_GUIDE.md`
- **Полная реализация:** `REFERRAL_SERVER_IMPLEMENTATION.py`
- **Функции для оплаты:** `REFERRAL_PAYMENT_INTEGRATION.py`

---

**После выполнения всех шагов: 100% готовность серверной части!**

