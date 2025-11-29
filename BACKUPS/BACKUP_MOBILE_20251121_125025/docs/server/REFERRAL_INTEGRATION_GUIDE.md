# 🔧 РУКОВОДСТВО ПО ИНТЕГРАЦИИ: Реферальная программа на сервере

**Дата:** 22 ноября 2024  
**Сервер:** 149.154.65.180

---

## ✅ ЧТО УЖЕ ГОТОВО

### Файлы для интеграции:
1. ✅ `REFERRAL_DB_SETUP.sql` — SQL схема (3 таблицы)
2. ✅ `REFERRAL_API_ENDPOINTS.py` — 4 API endpoints (полная реализация)
3. ✅ `REFERRAL_PAYMENT_INTEGRATION.py` — функции для интеграции в оплату
4. ✅ `REFERRAL_SERVER_IMPLEMENTATION.py` — полная реализация всех функций
5. ✅ `landing/invite.html` — реферальная страница

---

## 📋 ПОШАГОВАЯ ИНТЕГРАЦИЯ

### ШАГ 1: База данных (5 минут)

```bash
# 1. Подключиться к серверу
ssh root@149.154.65.180

# 2. Подключиться к PostgreSQL
psql -U ваш_пользователь -d ваша_база

# 3. Выполнить SQL скрипт
\i /path/to/REFERRAL_DB_SETUP.sql

# Или напрямую:
psql -U ваш_пользователь -d ваша_база -f REFERRAL_DB_SETUP.sql
```

**Проверка:**
```sql
-- Проверить что таблицы созданы
\dt referral*

-- Проверить функции
\df get_or_create_referral_code
```

---

### ШАГ 2: Интеграция API endpoints (10 минут)

**Файл:** `REFERRAL_API_ENDPOINTS.py`

```python
# В вашем main.py или routers/__init__.py:

from app.routers.referral import router as referral_router

app.include_router(referral_router, prefix="/api/referral", tags=["referral"])
```

**Настройка авторизации:**
```python
# В REFERRAL_API_ENDPOINTS.py раскомментировать:
from app.auth import get_current_user
from app.database import get_db

# И заменить:
# user_id = 1  # Заглушка
# На:
user = verify_token(token)  # Ваша функция
user_id = user["id"]
```

---

### ШАГ 3: Интеграция в оплату (15 минут)

**Файл:** `REFERRAL_PAYMENT_INTEGRATION.py`

#### 3.1: В `/api/payments/create`

```python
from app.referral_payment_integration import process_referral_code_on_payment, apply_referral_discount

@router.post("/api/payments/create")
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # ... существующая логика создания платежа ...
    
    # ✅ ДОБАВИТЬ: Обработка реферального кода
    referral_id = process_referral_code_on_payment(
        db, payment_data.referralCode, new_user_id, payment_data.amount
    )
    
    # ✅ ДОБАВИТЬ: Если это реферер (не приглашенный), применить скидку
    if not payment_data.referralCode:
        calculated_price = calculate_price(payment_data.tariffId, payment_data.periodMonths)
        final_amount = apply_referral_discount(db, current_user.id, calculated_price)
        payment_data.amount = final_amount
    
    # ... остальная логика ...
    return {"paymentId": payment.id, ...}
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
    
    # ... существующая логика проверки статуса ...
    
    if payment.status == 'paid':
        # ✅ ДОБАВИТЬ: Обработка реферальной программы
        process_referral_on_payment_confirmation(db, payment.user_id, payment.amount)
    
    return {"status": payment.status, ...}
```

---

### ШАГ 4: Загрузка landing страницы (5 минут)

```bash
# 1. Загрузить invite.html на сервер
scp landing/invite.html root@149.154.65.180:/var/www/aladdin-ai.ru/invite.html

# 2. Настроить права доступа
ssh root@149.154.65.180
chmod 644 /var/www/aladdin-ai.ru/invite.html
```

---

### ШАГ 5: Настройка Nginx (5 минут)

**Файл:** `NGINX_CONFIG.conf`

```bash
# 1. Загрузить конфигурацию на сервер
scp docs/server/NGINX_CONFIG.conf root@149.154.65.180:/tmp/nginx_referral.conf

# 2. Подключиться к серверу
ssh root@149.154.65.180

# 3. Добавить в существующую конфигурацию или создать новую
nano /etc/nginx/sites-available/aladdin-ai.ru

# 4. Добавить блок:
location /invite/ {
    try_files $uri $uri/ /invite.html?code=$1;
}

# Или если используете Python backend:
location /invite/ {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

# 5. Проверить конфигурацию
nginx -t

# 6. Перезагрузить Nginx
systemctl reload nginx
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

## 📝 ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **Авторизация:** Все API endpoints требуют токен в заголовке `Authorization: Bearer {token}`
2. **База данных:** Убедитесь, что таблица `users` существует перед созданием `referral_codes`
3. **Транзакции:** Используйте транзакции БД для атомарности операций
4. **Ошибки:** Обрабатывайте ошибки gracefully (не падать при отсутствии реферального кода)

---

## 🎯 ГОТОВНОСТЬ

После выполнения всех шагов:
- ✅ База данных: 100%
- ✅ API Endpoints: 100%
- ✅ Обработка оплаты: 100%
- ✅ Landing страница: 100%

**Итого: 100% готовность серверной части!**

