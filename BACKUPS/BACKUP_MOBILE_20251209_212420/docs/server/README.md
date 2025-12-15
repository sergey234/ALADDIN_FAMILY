# 🚀 ИНСТРУКЦИЯ: Развертывание реферальной программы

**Сервер:** 149.154.65.180  
**Сайт:** https://aladdin-ai.ru/  
**Дата:** 21 ноября 2024

---

## 📋 БЫСТРЫЙ СТАРТ

### 1. База данных (5 минут)
```bash
# Подключиться к серверу
ssh user@149.154.65.180

# Выполнить SQL скрипт
psql -U your_user -d your_database -f REFERRAL_DB_SETUP.sql
```

### 2. API Endpoints (30 минут)
```bash
# Скопировать файл в проект
cp REFERRAL_API_ENDPOINTS.py /path/to/your/fastapi/project/

# Настроить импорты и зависимости
# Реализовать логику в каждом endpoint
```

### 3. Landing страница (10 минут)
```bash
# Разместить HTML файл
cp REFERRAL_LANDING_PAGE.html /var/www/aladdin-ai.ru/templates/

# Настроить роутинг в FastAPI
```

### 4. Регистрация и оплата (30 минут)
```bash
# Интегрировать обработчики
cp REFERRAL_REGISTRATION_HANDLER.py /path/to/your/project/
cp REFERRAL_PAYMENT_HANDLER.py /path/to/your/project/
```

### 5. Nginx (5 минут)
```bash
# Применить конфигурацию
sudo cp NGINX_CONFIG.conf /etc/nginx/sites-available/aladdin-ai.ru
sudo nginx -t
sudo systemctl reload nginx
```

---

## 📁 СТРУКТУРА ФАЙЛОВ

```
docs/server/
├── README.md                           # Этот файл
├── REFERRAL_DB_SETUP.sql               # SQL скрипт для БД
├── REFERRAL_API_ENDPOINTS.py           # API endpoints
├── REFERRAL_LANDING_PAGE.html          # Landing страница
├── REFERRAL_REGISTRATION_HANDLER.py    # Обработка регистрации
├── REFERRAL_PAYMENT_HANDLER.py        # Обработка оплаты
├── NGINX_CONFIG.conf                   # Nginx конфигурация
└── REFERRAL_TESTING_CHECKLIST.md       # Чеклист тестирования
```

---

## 🔧 ДЕТАЛЬНЫЕ ИНСТРУКЦИИ

### Шаг 1: База данных

**Файл:** `REFERRAL_DB_SETUP.sql`

**Что делает:**
- Создает таблицы `referral_codes` и `referrals`
- Создает индексы для быстрого поиска
- Создает функции для генерации кодов

**Команда:**
```bash
psql -h localhost -U your_user -d your_database -f REFERRAL_DB_SETUP.sql
```

**Проверка:**
```sql
-- Проверить таблицы
\dt referral*

-- Проверить функции
\df generate_referral_code
\df get_or_create_referral_code
```

---

### Шаг 2: API Endpoints

**Файл:** `REFERRAL_API_ENDPOINTS.py`

**Что делать:**

1. **Скопировать в проект:**
```bash
cp REFERRAL_API_ENDPOINTS.py /path/to/your/fastapi/app/routers/
```

2. **Настроить импорты:**
```python
# Раскомментировать и настроить:
from app.database import get_db
from app.auth import get_current_user
from app.models import User, ReferralCode, Referral
```

3. **Реализовать логику:**
- В каждом endpoint раскомментировать код
- Настроить запросы к базе данных
- Протестировать каждый endpoint

4. **Добавить роутер в main.py:**
```python
from app.routers import referral_api

app.include_router(referral_api.router)
```

**Тестирование:**
```bash
# Тест endpoint 1
curl -X GET "https://aladdin-ai.ru/api/referral/code" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Тест endpoint 2
curl -X GET "https://aladdin-ai.ru/api/referral/stats" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Шаг 3: Landing страница

**Файл:** `REFERRAL_LANDING_PAGE.html`

**Что делать:**

1. **Разместить файл:**
```bash
# Вариант 1: Статический файл
cp REFERRAL_LANDING_PAGE.html /var/www/aladdin-ai.ru/static/invite.html

# Вариант 2: Шаблон FastAPI
cp REFERRAL_LANDING_PAGE.html /path/to/your/fastapi/templates/referral_landing.html
```

2. **Настроить роутинг в FastAPI:**
```python
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

@app.get("/invite/{code}", response_class=HTMLResponse)
async def referral_invite(code: str, request: Request):
    # Проверить, что код существует
    referral_code = db.query(ReferralCode).filter(
        ReferralCode.code == code
    ).first()
    
    if not referral_code:
        return RedirectResponse(url="/", status_code=301)
    
    return templates.TemplateResponse("referral_landing.html", {
        "request": request,
        "referral_code": code
    })
```

3. **Протестировать:**
```
Открыть в браузере: https://aladdin-ai.ru/invite/ABC123
```

---

### Шаг 4: Регистрация

**Файл:** `REFERRAL_REGISTRATION_HANDLER.py`

**Что делать:**

1. **Интегрировать в существующий код регистрации:**
```python
# В вашем endpoint регистрации добавить:
if user_data.referral_code:
    referral_code_obj = db.query(ReferralCode).filter(
        ReferralCode.code == user_data.referral_code
    ).first()
    
    if referral_code_obj:
        referral = Referral(
            referrer_id=referral_code_obj.user_id,
            invited_user_id=new_user.id,
            referral_code=user_data.referral_code,
            status="pending"
        )
        db.add(referral)
        db.commit()
```

2. **Добавить JavaScript на страницу регистрации:**
```javascript
// Скопировать код из REFERRAL_REGISTRATION_HANDLER.py
// (раздел JAVASCRIPT ДЛЯ ФРОНТЕНДА)
```

---

### Шаг 5: Оплата

**Файл:** `REFERRAL_PAYMENT_HANDLER.py`

**Что делать:**

1. **Интегрировать в существующий код оплаты:**
```python
# В вашем endpoint активации подписки добавить:
referral = db.query(Referral).filter(
    Referral.invited_user_id == user_id,
    Referral.status == "pending"
).first()

if referral:
    referral.status = "completed"
    referral.converted_at = datetime.now()
    # Начислить награду и применить скидку
    db.commit()
```

---

### Шаг 6: Nginx

**Файл:** `NGINX_CONFIG.conf`

**Что делать:**

1. **Скопировать конфигурацию:**
```bash
sudo cp NGINX_CONFIG.conf /etc/nginx/sites-available/aladdin-ai.ru
```

2. **Создать симлинк:**
```bash
sudo ln -s /etc/nginx/sites-available/aladdin-ai.ru /etc/nginx/sites-enabled/
```

3. **Проверить конфигурацию:**
```bash
sudo nginx -t
```

4. **Перезагрузить nginx:**
```bash
sudo systemctl reload nginx
```

---

## ✅ ПРОВЕРКА

После выполнения всех шагов проверить:

1. **База данных:**
```sql
SELECT * FROM referral_codes LIMIT 1;
SELECT * FROM referrals LIMIT 1;
```

2. **API Endpoints:**
```bash
curl -X GET "https://aladdin-ai.ru/api/referral/code" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

3. **Landing страница:**
```
Открыть: https://aladdin-ai.ru/invite/TEST123
```

4. **Регистрация:**
```
Открыть: https://aladdin-ai.ru/register?ref=TEST123
Зарегистрироваться и проверить в БД
```

5. **Оплата:**
```
Оплатить подписку и проверить обновление статуса в БД
```

---

## 🐛 РЕШЕНИЕ ПРОБЛЕМ

### Проблема: Таблицы не создаются
**Решение:** Проверить права доступа к базе данных

### Проблема: API возвращает 401
**Решение:** Проверить авторизацию и токен

### Проблема: Landing страница не открывается
**Решение:** Проверить роутинг в FastAPI и nginx конфигурацию

### Проблема: Реферал не засчитывается
**Решение:** Проверить логику в обработчике оплаты

---

## 📞 ПОДДЕРЖКА

Если возникли проблемы:
1. Проверить логи: `tail -f /var/log/nginx/error.log`
2. Проверить логи FastAPI
3. Проверить базу данных: `SELECT * FROM referrals;`

---

**Последнее обновление:** 21 ноября 2024


