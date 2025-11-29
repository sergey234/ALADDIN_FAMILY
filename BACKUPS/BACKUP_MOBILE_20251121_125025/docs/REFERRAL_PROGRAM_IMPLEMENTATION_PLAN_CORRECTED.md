# 🚀 План реализации реферальной программы (ИСПРАВЛЕННЫЙ)

**Дата:** 21 ноября 2024  
**Сервер:** 149.154.65.180  
**Сайт:** https://aladdin-ai.ru/  
**Реферальные ссылки:** https://aladdin-ai.ru/invite/{code}

---

## ✅ ИСПРАВЛЕНИЕ: Используем существующий домен!

**Не нужно покупать новый домен!** Используем ваш существующий `aladdin-ai.ru`.

**Реферальные ссылки будут:**
- `https://aladdin-ai.ru/invite/ABC123` ✅

**Вместо:**
- `https://aladdin.family/invite/ABC123` ❌ (не нужно)

---

## 📋 Содержание

1. [Реализация бэкенд API endpoints (4 endpoints)](#1-реализация-бэкенд-api-endpoints)
2. [Настройка реферальных ссылок на aladdin-ai.ru](#2-настройка-реферальных-ссылок-на-aladdin-airu)
3. [Тестирование на реальных устройствах](#3-тестирование-на-реальных-устройствах)

---

## 1. Реализация бэкенд API endpoints

### 📌 Что это такое?

Мобильное приложение должно получать данные о реферальной программе с вашего сервера. Для этого нужно создать 4 API endpoints (точки входа), которые будут возвращать информацию в формате JSON.

### 🔧 Что нужно сделать:

#### Endpoint 1: GET `/api/referral/code`

**Что делает:** Возвращает реферальный код пользователя и ссылку для приглашения.

**Что нужно реализовать на сервере:**
1. Проверить авторизацию пользователя (токен из заголовка `Authorization: Bearer {token}`)
2. Найти или создать реферальный код для этого пользователя
3. Сгенерировать реферальную ссылку
4. Вернуть данные в формате JSON

**Формат ответа (JSON):**
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

**Как реализовать (Python пример):**
```python
@app.get("/api/referral/code")
async def get_referral_code(request: Request):
    # 1. Проверить токен авторизации
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = verify_token(token)  # Ваша функция проверки токена
    
    # 2. Найти или создать реферальный код
    referral = db.get_or_create_referral_code(user.id)
    
    # 3. Сформировать ответ
    return {
        "referral_code": referral.code,
        "referral_url": f"https://aladdin-ai.ru/invite/{referral.code}",
        "invitations_count": db.count_invitations(user.id),
        "earned_bonus": db.calculate_earned_bonus(user.id),
        "invited_friends": db.get_invited_friends(user.id)
    }
```

**Где хранить данные:**
- Таблица `referral_codes`: `user_id`, `code`, `created_at`
- Код должен быть уникальным (например: `ABC123`, `XYZ789`)
- Можно генерировать случайно или использовать user_id + хеш

---

#### Endpoint 2: GET `/api/referral/stats`

**Что делает:** Возвращает статистику реферальной программы пользователя.

**Формат ответа (JSON):**
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

---

#### Endpoint 3: GET `/api/referral/history`

**Что делает:** Возвращает историю всех приглашенных пользователей.

**Формат ответа (JSON):**
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

---

#### Endpoint 4: GET `/api/referral/rewards`

**Что делает:** Возвращает информацию о наградах и достижениях.

**Формат ответа (JSON):**
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

---

## 2. Настройка реферальных ссылок на aladdin-ai.ru

### 📌 Что это такое?

Нужно настроить на вашем сайте `aladdin-ai.ru`, чтобы ссылки вида `https://aladdin-ai.ru/invite/ABC123` работали и открывали страницу регистрации с автоматическим применением реферального кода.

### 🔧 Что нужно сделать:

#### Вариант 1: Простой путь (РЕКОМЕНДУЕТСЯ)

**Настроить на сайте aladdin-ai.ru:**

**URL:** `https://aladdin-ai.ru/invite/ABC123`

**Что должно происходить:**

1. **Пользователь переходит по ссылке** `https://aladdin-ai.ru/invite/ABC123`
2. **Сервер извлекает код** `ABC123` из URL
3. **Редирект на страницу регистрации** с параметром: `https://aladdin-ai.ru/register?ref=ABC123`
4. **Или сразу показать страницу регистрации** с уже примененным кодом

**Как реализовать (nginx):**
```nginx
# На вашем сервере 149.154.65.180
server {
    listen 443 ssl http2;
    server_name aladdin-ai.ru www.aladdin-ai.ru;
    
    # Реферальные ссылки: /invite/{code}
    location ~ ^/invite/([A-Z0-9-]+)$ {
        # Перенаправляем на страницу регистрации с кодом
        return 301 https://aladdin-ai.ru/register?ref=$1;
    }
    
    # Или если у вас Python backend:
    location /invite/ {
        proxy_pass http://localhost:8000;  # Ваш Python backend
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Или в Python (FastAPI/Flask):**
```python
@app.get("/invite/{code}")
async def referral_invite(code: str):
    # Редирект на страницу регистрации с кодом
    return RedirectResponse(url=f"/register?ref={code}", status_code=301)

# Или показать красивую landing страницу
@app.get("/invite/{code}")
async def referral_invite(code: str):
    return templates.TemplateResponse("referral_landing.html", {
        "request": request,
        "referral_code": code,
        "register_url": f"/register?ref={code}"
    })
```

---

#### Вариант 2: Красивая landing страница (лучше UX)

**Создать отдельную страницу для реферальных ссылок:**

**URL:** `https://aladdin-ai.ru/invite/ABC123`

**Что должно быть на странице:**
- Красивый дизайн с информацией о реферальной программе
- Текст: "Вы приглашены по коду ABC123! Вы оба получите скидку -20%!"
- Кнопка "Зарегистрироваться" → ведет на `/register?ref=ABC123`
- Можно добавить счетчик: "Уже 5 человек присоединились по этому коду!"

**Пример HTML:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Приглашение в ALADDIN</title>
</head>
<body>
    <h1>🎁 Вы приглашены в ALADDIN!</h1>
    <p>Ваш друг пригласил вас по коду: <strong>ABC123</strong></p>
    <p>Вы оба получите скидку -20% на 1 месяц!</p>
    <a href="/register?ref=ABC123">Зарегистрироваться</a>
</body>
</html>
```

---

#### Шаг 3: Обработка реферального кода на странице регистрации

**На странице регистрации (`/register`):**

**Что должно происходить:**

1. **Проверить параметр `ref` в URL** (`?ref=ABC123`)
2. **Сохранить реферальный код** в сессии/cookie/localStorage
3. **Показать форму регистрации**
4. **При регистрации автоматически применить реферальный код**

**Пример (JavaScript на фронтенде):**
```javascript
// На странице регистрации
const urlParams = new URLSearchParams(window.location.search);
const referralCode = urlParams.get('ref');

if (referralCode) {
    // Сохранить код в localStorage
    localStorage.setItem('referral_code', referralCode);
    
    // Показать сообщение пользователю
    showMessage(`Вы приглашены по коду: ${referralCode}. Вы оба получите скидку!`);
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
        body: JSON.stringify(formData)
    });
}
```

**На бэкенде (Python):**
```python
@app.post("/api/register")
async def register_user(user_data: UserRegistration):
    # Создать пользователя
    new_user = create_user(user_data)
    
    # Если есть реферальный код, создать запись в referrals
    if user_data.referral_code:
        referral = db.get_referral_code(user_data.referral_code)
        if referral:
            db.create_referral(
                referrer_id=referral.user_id,
                invited_user_id=new_user.id,
                referral_code=user_data.referral_code,
                status="pending"
            )
    
    return {"success": True, "user_id": new_user.id}
```

---

### 🎯 Рекомендации

**Вариант 1: Простой редирект (быстро, 30 минут)**
- `aladdin-ai.ru/invite/ABC123` → редирект на `aladdin-ai.ru/register?ref=ABC123`
- Минимум настроек, работает сразу
- ✅ **Рекомендуется для начала**

**Вариант 2: Красивая landing страница (лучше UX, 2-3 часа)**
- `aladdin-ai.ru/invite/ABC123` → красивая страница с информацией
- Кнопка "Зарегистрироваться" ведет на `aladdin-ai.ru/register?ref=ABC123`
- Можно добавить счетчик переходов
- ✅ **Рекомендуется после запуска**

**Рекомендация:** Начать с Варианта 1 (простой редирект), потом перейти на Вариант 2 для лучшего UX.

---

## 3. Тестирование на реальных устройствах

### 📱 Что проверить:

1. **Реферальная ссылка работает:**
   - [ ] Перейти по ссылке `https://aladdin-ai.ru/invite/ABC123`
   - [ ] Открывается страница регистрации
   - [ ] Реферальный код автоматически применяется

2. **Все способы приглашения:**
   - [ ] WhatsApp (с приложением и без)
   - [ ] Telegram (с приложением и без)
   - [ ] VK (с приложением и без)
   - [ ] Системный Share Sheet
   - [ ] Копирование кода и ссылки

3. **API endpoints:**
   - [ ] Реферальный код загружается
   - [ ] Статистика отображается
   - [ ] История загружается
   - [ ] Награды отображаются

---

## 🎯 Итоговый план действий

### ✅ Что уже сделано:
- Код в приложении исправлен: теперь использует `aladdin-ai.ru/invite/{code}`
- Локализация обновлена: текст шаблона использует правильный домен

### 📋 Что нужно сделать на сервере:

#### 1. Реализовать 4 API endpoints (1-2 дня)
- `/api/referral/code` - получение кода
- `/api/referral/stats` - статистика
- `/api/referral/history` - история
- `/api/referral/rewards` - награды

#### 2. Настроить реферальные ссылки на сайте (30 минут - 2 часа)
- **Вариант 1 (быстро):** Редирект `/invite/{code}` → `/register?ref={code}`
- **Вариант 2 (лучше):** Красивая landing страница `/invite/{code}`

#### 3. Обработать реферальный код при регистрации (1 час)
- На странице `/register` проверить параметр `?ref=ABC123`
- Сохранить код и применить при регистрации
- Создать запись в таблице `referrals`

#### 4. Протестировать (1 день)
- На реальных устройствах
- Все способы приглашения
- Реферальные ссылки

---

## 💡 Преимущества использования aladdin-ai.ru

✅ **Не нужно покупать новый домен** - экономия $10-30/год  
✅ **Проще настроить** - один домен, одна конфигурация  
✅ **Единый бренд** - все ссылки ведут на ваш сайт  
✅ **Меньше DNS настроек** - не нужно настраивать новый домен  

---

**Последнее обновление:** 21 ноября 2024  
**Статус:** ✅ Код исправлен, использует aladdin-ai.ru

