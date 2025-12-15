# ✅ ФИНАЛЬНЫЙ ЧЕКЛИСТ: Реферальная программа для продакшна

**Дата:** 21 ноября 2024  
**Сервер:** 149.154.65.180  
**Сайт:** https://aladdin-ai.ru/  
**Реферальные ссылки:** https://aladdin-ai.ru/invite/{code}

---

## 🎯 КРАТКОЕ РЕЗЮМЕ

### ✅ Что уже сделано в приложении:
- ✅ Код исправлен: использует `aladdin-ai.ru/invite/{code}`
- ✅ Локализация обновлена
- ✅ UI/UX исправлен (кнопки кликабельны, скролл работает)
- ✅ API интеграция готова (4 метода в APIService)
- ✅ Модели данных готовы (ReferralOverviewResponse, ReferralStatsResponse, etc.)
- ✅ URL схемы настроены (WhatsApp, Telegram, VK в Info.plist)
- ✅ Fallback механизмы работают

### 📋 Что нужно сделать на сервере:

---

## 📋 ПОЛНЫЙ ЧЕКЛИСТ РЕАЛИЗАЦИИ

### 1️⃣ БАЗА ДАННЫХ (Структура таблиц)

#### ✅ Таблица `referral_codes`
```sql
CREATE TABLE referral_codes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    code VARCHAR(20) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Индексы для быстрого поиска
CREATE INDEX idx_referral_codes_code ON referral_codes(code);
CREATE INDEX idx_referral_codes_user_id ON referral_codes(user_id);
```

**Что хранить:**
- `user_id` - ID пользователя, который приглашает
- `code` - уникальный реферальный код (например: `ABC123`)
- `created_at` - дата создания кода

**Логика:**
- ✅ **У каждого пользователя свой уникальный код!**
- При первом запросе `/api/referral/code` создать код для пользователя
- Код должен быть уникальным (проверка при создании)
- Можно генерировать случайно или использовать `user_id + hash`
- **Важно:** `user_id UNIQUE` означает, что у каждого пользователя может быть только ОДИН код
- **Важно:** `code UNIQUE` означает, что каждый код уникален в базе (не может быть двух одинаковых)

**Пример:**
- Пользователь А (ID=100) → код `ABC123`
- Пользователь Б (ID=200) → код `XYZ789`
- Пользователь В (ID=300) → код `DEF456`

Каждый использует свой код для приглашения друзей!

---

#### ✅ Таблица `referrals`
```sql
CREATE TABLE referrals (
    id SERIAL PRIMARY KEY,
    referrer_id INTEGER NOT NULL,
    invited_user_id INTEGER NOT NULL,
    referral_code VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- 'pending', 'completed', 'cancelled'
    created_at TIMESTAMP DEFAULT NOW(),
    converted_at TIMESTAMP NULL,
    discount_applied DECIMAL(10,2) DEFAULT 0,
    reward_amount DECIMAL(10,2) DEFAULT 0,
    FOREIGN KEY (referrer_id) REFERENCES users(id),
    FOREIGN KEY (invited_user_id) REFERENCES users(id),
    FOREIGN KEY (referral_code) REFERENCES referral_codes(code)
);

-- Индексы
CREATE INDEX idx_referrals_referrer_id ON referrals(referrer_id);
CREATE INDEX idx_referrals_invited_user_id ON referrals(invited_user_id);
CREATE INDEX idx_referrals_status ON referrals(status);
CREATE INDEX idx_referrals_code ON referrals(referral_code);
```

**Что хранить:**
- `referrer_id` - ID пользователя, который пригласил
- `invited_user_id` - ID приглашенного пользователя
- `referral_code` - код, по которому пригласили
- `status` - статус: `pending` (зарегистрировался), `completed` (оплатил), `cancelled` (отменил)
- `created_at` - дата регистрации приглашенного
- `converted_at` - дата оплаты (когда статус стал `completed`)
- `discount_applied` - размер скидки, примененной к приглашенному
- `reward_amount` - размер награды рефереру

**Логика:**
- При регистрации с реферальным кодом → создать запись со `status='pending'`
- При оплате подписки приглашенным → обновить `status='completed'`, установить `converted_at`, начислить награду

---

### 2️⃣ API ENDPOINTS (4 endpoints)

#### ✅ Endpoint 1: GET `/api/referral/code`

**Что делает:** Возвращает реферальный код пользователя и статистику.

**Авторизация:** Требуется (токен в заголовке `Authorization: Bearer {token}`)

**Формат ответа:**
```json
{
  "referral_code": "ABC123",
  "referral_url": "https://aladdin-ai.ru/invite/ABC123",
  "qr_code": "base64_encoded_qr_image_optional",
  "invitations_count": 5,
  "earned_bonus": 1000.0,
  "invited_friends": [
    {
      "friend_id": "user_456",
      "status": "pending",
      "created_at": "2024-11-21T10:00:00Z",
      "converted_at": null,
      "reward_amount": null
    }
  ]
}
```

**Логика реализации:**
1. Проверить токен авторизации
2. Получить `user_id` из токена
3. Найти или создать реферальный код для этого пользователя
4. Посчитать количество приглашенных (`SELECT COUNT(*) FROM referrals WHERE referrer_id = ?`)
5. Посчитать заработанный бонус (`SELECT SUM(reward_amount) FROM referrals WHERE referrer_id = ? AND status = 'completed'`)
6. Получить список приглашенных друзей
7. Вернуть JSON ответ

**Пример (Python FastAPI):**
```python
@app.get("/api/referral/code")
async def get_referral_code(request: Request):
    # 1. Проверить токен
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # 2. Найти или создать код
    referral_code = db.get_or_create_referral_code(user.id)
    
    # 3. Посчитать статистику
    invitations_count = db.count_referrals(user.id)
    earned_bonus = db.calculate_earned_bonus(user.id)
    invited_friends = db.get_invited_friends(user.id)
    
    # 4. Сформировать ответ
    return {
        "referral_code": referral_code.code,
        "referral_url": f"https://aladdin-ai.ru/invite/{referral_code.code}",
        "invitations_count": invitations_count,
        "earned_bonus": earned_bonus,
        "invited_friends": invited_friends
    }
```

---

#### ✅ Endpoint 2: GET `/api/referral/stats`

**Что делает:** Возвращает детальную статистику реферальной программы.

**Авторизация:** Требуется

**Формат ответа:**
```json
{
  "total_referrals": 10,
  "converted_referrals": 3,
  "pending_referrals": 7,
  "total_rewards": 1500.0,
  "conversion_rate": 30.0,
  "referral_tier": "bronze",
  "active_links": 5
}
```

**Логика:**
- `total_referrals` = общее количество приглашенных
- `converted_referrals` = количество оплативших (status='completed')
- `pending_referrals` = количество зарегистрированных, но не оплативших (status='pending')
- `total_rewards` = сумма всех наград
- `conversion_rate` = (converted_referrals / total_referrals) * 100
- `referral_tier` = уровень (bronze, silver, gold) на основе converted_referrals
- `active_links` = количество уникальных кодов, по которым были переходы за последние 30 дней

---

#### ✅ Endpoint 3: GET `/api/referral/history`

**Что делает:** Возвращает историю всех приглашенных пользователей.

**Авторизация:** Требуется

**Формат ответа:**
```json
[
  {
    "referral_id": "ref_123",
    "friend_id": "user_456",
    "status": "completed",
    "created_at": "2024-11-21T10:00:00Z",
    "converted_at": "2024-11-21T15:00:00Z",
    "referral_code": "ABC123",
    "discount_applied": 500.0,
    "reward_amount": 1000.0
  }
]
```

**Логика:**
- Вернуть все записи из таблицы `referrals` для текущего пользователя
- Отсортировать по `created_at DESC` (новые сверху)
- Включить информацию о приглашенном пользователе (имя, email)

---

#### ✅ Endpoint 4: GET `/api/referral/rewards`

**Что делает:** Возвращает информацию о наградах и достижениях.

**Авторизация:** Требуется

**Формат ответа:**
```json
{
  "total_converted": 3,
  "rewards": [
    {
      "reward_id": "reward_1",
      "title_key": "referral_reward_1_title",
      "subtitle_key": "referral_reward_1_subtitle",
      "amount_key": "referral_reward_1_amount",
      "reward_value": "10%",
      "icon": "percent.circle.fill",
      "required_converted": 1,
      "status": "unlocked",
      "remaining": 0,
      "unlocked_at": "2024-11-21T10:00:00Z"
    }
  ]
}
```

**Логика:**
- Определить, какие награды разблокированы на основе `total_converted`
- Вернуть список всех наград с их статусом (unlocked/locked)

---

### 3️⃣ КРАСИВАЯ LANDING СТРАНИЦА `/invite/{code}`

#### ✅ Что нужно создать:

**URL:** `https://aladdin-ai.ru/invite/ABC123`

**Что должно быть на странице:**

1. **Заголовок:** "🎁 Вы приглашены в ALADDIN!"
2. **Информация о коде:** "Ваш друг пригласил вас по коду: **ABC123**"
3. **Описание выгоды:** "Вы оба получите скидку -20% на 1 месяц после тестового периода!"
4. **Кнопка "Зарегистрироваться"** → ведет на `/register?ref=ABC123`
5. **Опционально:** Счетчик "Уже 5 человек присоединились по этому коду!" (если есть API для этого)

**Дизайн:**
- Адаптивный (работает на мобильных и десктопах)
- Красивый, современный дизайн
- Логотип ALADDIN
- Призыв к действию (CTA)

**Пример HTML (базовый):**
```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Приглашение в ALADDIN</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            text-align: center;
            padding: 40px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.1);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        h1 { font-size: 2.5em; margin-bottom: 20px; }
        .code { font-size: 1.5em; font-weight: bold; margin: 20px 0; }
        .benefit { font-size: 1.2em; margin: 30px 0; }
        .btn {
            display: inline-block;
            padding: 15px 40px;
            background: white;
            color: #667eea;
            text-decoration: none;
            border-radius: 30px;
            font-weight: bold;
            font-size: 1.1em;
            margin-top: 30px;
            transition: transform 0.2s;
        }
        .btn:hover { transform: scale(1.05); }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎁 Вы приглашены в ALADDIN!</h1>
        <p>Ваш друг пригласил вас по коду:</p>
        <div class="code">ABC123</div>
        <p class="benefit">Вы оба получите скидку <strong>-20%</strong> на 1 месяц после тестового периода!</p>
        <a href="/register?ref=ABC123" class="btn">Зарегистрироваться</a>
    </div>
</body>
</html>
```

**Как реализовать (Python FastAPI):**
```python
@app.get("/invite/{code}")
async def referral_invite(code: str, request: Request):
    # 1. Проверить, что код существует
    referral_code = db.get_referral_code(code)
    if not referral_code:
        # Если код не найден, редирект на главную или показать ошибку
        return RedirectResponse(url="/", status_code=301)
    
    # 2. Опционально: получить статистику по коду
    # stats = db.get_referral_code_stats(code)
    
    # 3. Показать landing страницу
    return templates.TemplateResponse("referral_landing.html", {
        "request": request,
        "referral_code": code,
        "register_url": f"/register?ref={code}",
        # "stats": stats  # если есть счетчик
    })
```

---

### 4️⃣ ОБРАБОТКА РЕФЕРАЛЬНОГО КОДА ПРИ РЕГИСТРАЦИИ

#### ✅ На странице регистрации `/register`

**Что должно происходить:**

1. **Проверить параметр `ref` в URL** (`?ref=ABC123`)
2. **Сохранить реферальный код** в сессии/cookie/localStorage
3. **Показать сообщение пользователю:** "Вы приглашены по коду ABC123. Вы оба получите скидку!"
4. **При регистрации автоматически применить реферальный код**

**JavaScript на фронтенде:**
```javascript
// На странице регистрации
const urlParams = new URLSearchParams(window.location.search);
const referralCode = urlParams.get('ref');

if (referralCode) {
    // Сохранить код в localStorage
    localStorage.setItem('referral_code', referralCode);
    
    // Показать сообщение пользователю
    showMessage(`Вы приглашены по коду: ${referralCode}. Вы оба получите скидку -20%!`);
}

// При отправке формы регистрации
function submitRegistration(formData) {
    const referralCode = localStorage.getItem('referral_code');
    
    if (referralCode) {
        formData.referral_code = referralCode;
    }
    
    // Отправить на сервер
    fetch('/api/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Регистрация успешна
            localStorage.removeItem('referral_code'); // Очистить после использования
            window.location.href = '/dashboard';
        }
    });
}
```

**На бэкенде (Python):**
```python
@app.post("/api/register")
async def register_user(user_data: UserRegistration):
    # 1. Создать пользователя
    new_user = create_user(user_data)
    
    # 2. Если есть реферальный код, создать запись в referrals
    if user_data.referral_code:
        referral_code_obj = db.get_referral_code(user_data.referral_code)
        if referral_code_obj:
            # Создать запись о реферале
            db.create_referral(
                referrer_id=referral_code_obj.user_id,
                invited_user_id=new_user.id,
                referral_code=user_data.referral_code,
                status="pending"  # Пока не оплатил
            )
    
    return {"success": True, "user_id": new_user.id}
```

---

### 5️⃣ ОБРАБОТКА РЕФЕРАЛЬНОГО КОДА ПРИ ОПЛАТЕ

#### ✅ КРИТИЧНО: Реферал засчитывается при ОПЛАТЕ, а не при регистрации!

**Что должно происходить:**

1. **Пользователь регистрируется с реферальным кодом** → создается запись со `status='pending'`
2. **Пользователь оплачивает подписку** → обновить запись:
   - `status='completed'`
   - `converted_at` = текущая дата
   - `discount_applied` = размер скидки (например, 20%)
   - `reward_amount` = размер награды рефереру (например, 1000₽)
3. **Начислить награду рефереру** (добавить бонус на счет или применить скидку)

**На бэкенде (Python) - при оплате подписки:**
```python
@app.post("/api/subscription/activate")
async def activate_subscription(activation_data: ActivationData):
    # 1. Активировать подписку для пользователя
    subscription = activate_user_subscription(activation_data.user_id, activation_data.code)
    
    # 2. Проверить, есть ли реферальная запись для этого пользователя
    referral = db.get_referral_by_invited_user(activation_data.user_id)
    if referral and referral.status == "pending":
        # 3. Обновить статус реферала на "completed"
        db.update_referral(
            referral_id=referral.id,
            status="completed",
            converted_at=datetime.now(),
            discount_applied=500.0,  # 20% скидка
            reward_amount=1000.0  # Награда рефереру
        )
        
        # 4. Начислить награду рефереру
        db.add_referral_reward(
            user_id=referral.referrer_id,
            amount=1000.0
        )
        
        # 5. Применить скидку к приглашенному пользователю
        apply_discount_to_user(activation_data.user_id, discount_percent=20)
    
    return {"success": True, "subscription": subscription}
```

**Важно:**
- Реферал засчитывается только при ОПЛАТЕ, не при регистрации
- Оба пользователя (реферер и приглашенный) должны получить выгоду
- Награда рефереру начисляется сразу после оплаты приглашенным

---

### 6️⃣ НАСТРОЙКА NGINX (если используется)

**На сервере 149.154.65.180:**

```nginx
server {
    listen 443 ssl http2;
    server_name aladdin-ai.ru www.aladdin-ai.ru;
    
    # SSL сертификат
    ssl_certificate /etc/letsencrypt/live/aladdin-ai.ru/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/aladdin-ai.ru/privkey.pem;
    
    # Реферальные ссылки: /invite/{code}
    # Проксируем на Python backend
    location /invite/ {
        proxy_pass http://localhost:8000;  # Ваш Python backend
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Статические файлы (если есть)
    location /static/ {
        alias /var/www/aladdin-ai.ru/static/;
    }
}
```

---

## ✅ ФИНАЛЬНЫЙ ЧЕКЛИСТ

### База данных:
- [ ] Создана таблица `referral_codes`
- [ ] Создана таблица `referrals`
- [ ] Созданы индексы для быстрого поиска
- [ ] Настроены внешние ключи (foreign keys)

### API Endpoints:
- [ ] GET `/api/referral/code` - работает
- [ ] GET `/api/referral/stats` - работает
- [ ] GET `/api/referral/history` - работает
- [ ] GET `/api/referral/rewards` - работает
- [ ] Все endpoints требуют авторизацию (токен)
- [ ] Все endpoints возвращают правильный JSON формат

### Landing страница:
- [ ] Создана страница `/invite/{code}`
- [ ] Страница красиво оформлена
- [ ] Страница адаптивная (работает на мобильных)
- [ ] Кнопка "Зарегистрироваться" ведет на `/register?ref={code}`
- [ ] Страница проверяет, что код существует

### Регистрация:
- [ ] Страница `/register` обрабатывает параметр `?ref=ABC123`
- [ ] Реферальный код сохраняется при регистрации
- [ ] Создается запись в таблице `referrals` со `status='pending'`
- [ ] Пользователь видит сообщение о реферальном коде

### Оплата:
- [ ] При оплате подписки проверяется реферальная запись
- [ ] Статус обновляется на `completed`
- [ ] Устанавливается `converted_at`
- [ ] Начисляется награда рефереру
- [ ] Применяется скидка приглашенному пользователю

### Тестирование:
- [ ] Реферальная ссылка работает: `https://aladdin-ai.ru/invite/ABC123`
- [ ] Landing страница открывается
- [ ] Регистрация с реферальным кодом работает
- [ ] Оплата засчитывает реферала
- [ ] API endpoints возвращают правильные данные
- [ ] Мобильное приложение получает данные из API

---

## 🎯 ИТОГОВЫЙ ПЛАН ДЕЙСТВИЙ

### Этап 1: База данных (1-2 часа)
1. Создать таблицы `referral_codes` и `referrals`
2. Создать индексы
3. Настроить внешние ключи

### Этап 2: API Endpoints (4-6 часов)
1. Реализовать GET `/api/referral/code`
2. Реализовать GET `/api/referral/stats`
3. Реализовать GET `/api/referral/history`
4. Реализовать GET `/api/referral/rewards`
5. Протестировать все endpoints

### Этап 3: Landing страница (2-3 часа)
1. Создать HTML шаблон для `/invite/{code}`
2. Стилизовать страницу
3. Добавить логику проверки кода
4. Настроить редирект на `/register?ref={code}`

### Этап 4: Регистрация (1-2 часа)
1. Добавить обработку параметра `?ref=ABC123` на странице регистрации
2. Сохранить код в localStorage/сессии
3. При регистрации создать запись в `referrals` со `status='pending'`

### Этап 5: Оплата (2-3 часа)
1. При оплате подписки проверить реферальную запись
2. Обновить статус на `completed`
3. Начислить награду рефереру
4. Применить скидку приглашенному

### Этап 6: Тестирование (1 день)
1. Протестировать все сценарии
2. Проверить работу на мобильных устройствах
3. Проверить интеграцию с мобильным приложением

---

## 💡 ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **Реферал засчитывается при ОПЛАТЕ, не при регистрации!**
   - Регистрация → `status='pending'`
   - Оплата → `status='completed'` + награда

2. **Оба пользователя должны получить выгоду:**
   - Реферер получает награду (бонус на счет)
   - Приглашенный получает скидку (20% на первый месяц)

3. **Код должен быть уникальным:**
   - Проверка при создании
   - Формат: буквы и цифры (например: `ABC123`, `XYZ789`)

4. **Авторизация обязательна:**
   - Все API endpoints требуют токен в заголовке
   - Проверка токена перед обработкой запроса

---

## ✅ ПОДТВЕРЖДЕНИЕ: ВСЕ УЧТЕНО!

✅ База данных - структура таблиц готова  
✅ API endpoints - все 4 endpoints описаны  
✅ Landing страница - красивый вариант описан  
✅ Регистрация - обработка реферального кода учтена  
✅ Оплата - логика засчитывания реферала при оплате учтена  
✅ Тестирование - план тестирования готов  

**Больше ничего не нужно делать с реферальной программой на стороне мобильного приложения!**  
Все готово, осталось только реализовать на сервере согласно этому чеклисту.

---

**Последнее обновление:** 21 ноября 2024  
**Статус:** ✅ Финальный чеклист готов, все учтено

