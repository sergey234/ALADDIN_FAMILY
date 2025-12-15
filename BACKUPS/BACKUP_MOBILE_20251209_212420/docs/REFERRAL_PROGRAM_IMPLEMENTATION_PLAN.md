# 🚀 План реализации реферальной программы для продакшна

**Дата:** 21 ноября 2024  
**Сервер:** 149.154.65.180  
**Сайт:** https://aladdin-ai.ru/  
**Домен для рефералов:** aladdin.family (требуется настройка)

---

## 📋 Содержание

1. [Реализация бэкенд API endpoints (4 endpoints)](#1-реализация-бэкенд-api-endpoints)
2. [Настройка домена aladdin.family для реферальных ссылок](#2-настройка-домена-aladdinfamily)
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
  "referral_url": "https://aladdin.family/invite/ABC123",
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
        "referral_url": f"https://aladdin.family/invite/{referral.code}",
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

**Что нужно реализовать на сервере:**
1. Проверить авторизацию
2. Посчитать общее количество приглашенных
3. Посчитать количество оплативших (конвертированных)
4. Посчитать количество ожидающих (pending)
5. Посчитать общую сумму наград
6. Вычислить процент конверсии
7. Определить уровень (tier) пользователя

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

**Как реализовать (Python пример):**
```python
@app.get("/api/referral/stats")
async def get_referral_stats(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = verify_token(token)
    
    stats = db.get_referral_stats(user.id)
    
    return {
        "total_referrals": stats.total,
        "converted_referrals": stats.converted,
        "pending_referrals": stats.pending,
        "total_rewards": stats.total_rewards,
        "conversion_rate": (stats.converted / stats.total * 100) if stats.total > 0 else 0,
        "referral_tier": calculate_tier(stats.converted),  # bronze, silver, gold
        "active_links": stats.active_links
    }
```

**Где хранить данные:**
- Таблица `referrals`: `referrer_id`, `invited_user_id`, `status` (pending/completed/cancelled), `created_at`, `converted_at`
- Статистика вычисляется на основе записей в таблице `referrals`

---

#### Endpoint 3: GET `/api/referral/history`

**Что делает:** Возвращает историю всех приглашенных пользователей.

**Что нужно реализовать на сервере:**
1. Проверить авторизацию
2. Получить список всех рефералов пользователя
3. Отсортировать по дате создания (новые первыми)
4. Вернуть с информацией о статусе и наградах

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
  },
  {
    "referral_id": "ref_124",
    "friend_id": "user_789",
    "status": "pending",
    "created_at": "2024-11-20T12:00:00Z",
    "converted_at": null,
    "referral_code": "ABC123",
    "discount_applied": null,
    "reward_amount": null
  }
]
```

**Как реализовать (Python пример):**
```python
@app.get("/api/referral/history")
async def get_referral_history(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = verify_token(token)
    
    referrals = db.get_referral_history(user.id)
    
    return [
        {
            "referral_id": ref.id,
            "friend_id": ref.invited_user_id,
            "status": ref.status,
            "created_at": ref.created_at.isoformat(),
            "converted_at": ref.converted_at.isoformat() if ref.converted_at else None,
            "referral_code": ref.code,
            "discount_applied": ref.discount_applied,
            "reward_amount": ref.reward_amount
        }
        for ref in referrals
    ]
```

**Где хранить данные:**
- Таблица `referrals` (та же, что для статистики)
- Статусы: `pending` (ожидает оплаты), `completed` (оплатил), `cancelled` (отменил)

---

#### Endpoint 4: GET `/api/referral/rewards`

**Что делает:** Возвращает информацию о наградах и достижениях.

**Что нужно реализовать на сервере:**
1. Проверить авторизацию
2. Получить количество конвертированных рефералов
3. Определить, какие награды разблокированы
4. Вернуть список всех наград с их статусом

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
    },
    {
      "reward_id": "reward_3",
      "title_key": "referral_reward_3_title",
      "subtitle_key": "referral_reward_3_subtitle",
      "amount_key": "referral_reward_3_amount",
      "reward_value": "30%",
      "icon": "crown.fill",
      "required_converted": 3,
      "status": "unlocked",
      "remaining": 0,
      "unlocked_at": "2024-11-21T15:00:00Z"
    },
    {
      "reward_id": "reward_10",
      "title_key": "referral_reward_10_title",
      "subtitle_key": "referral_reward_10_subtitle",
      "amount_key": "referral_reward_10_amount",
      "reward_value": "1 месяц бесплатно",
      "icon": "star.fill",
      "required_converted": 10,
      "status": "locked",
      "remaining": 7,
      "unlocked_at": null
    }
  ]
}
```

**Как реализовать (Python пример):**
```python
@app.get("/api/referral/rewards")
async def get_referral_rewards(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = verify_token(token)
    
    converted_count = db.count_converted_referrals(user.id)
    
    # Определяем награды
    rewards = [
        {
            "reward_id": "reward_1",
            "required_converted": 1,
            "status": "unlocked" if converted_count >= 1 else "locked",
            "remaining": max(0, 1 - converted_count),
            "unlocked_at": db.get_unlock_date(user.id, 1) if converted_count >= 1 else None
        },
        {
            "reward_id": "reward_3",
            "required_converted": 3,
            "status": "unlocked" if converted_count >= 3 else "locked",
            "remaining": max(0, 3 - converted_count),
            "unlocked_at": db.get_unlock_date(user.id, 3) if converted_count >= 3 else None
        },
        {
            "reward_id": "reward_10",
            "required_converted": 10,
            "status": "unlocked" if converted_count >= 10 else "locked",
            "remaining": max(0, 10 - converted_count),
            "unlocked_at": db.get_unlock_date(user.id, 10) if converted_count >= 10 else None
        }
    ]
    
    return {
        "total_converted": converted_count,
        "rewards": rewards
    }
```

**Где хранить данные:**
- Награды можно хранить в конфигурации (hardcoded) или в таблице `referral_rewards`
- Статус разблокировки вычисляется на основе `converted_count`

---

### 📊 Структура базы данных

**Рекомендуемые таблицы:**

```sql
-- Реферальные коды пользователей
CREATE TABLE referral_codes (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_code (code)
);

-- Рефералы (приглашенные пользователи)
CREATE TABLE referrals (
    id SERIAL PRIMARY KEY,
    referral_id VARCHAR(50) UNIQUE NOT NULL,
    referrer_id INTEGER NOT NULL,  -- Кто пригласил
    invited_user_id INTEGER,       -- Кого пригласили (может быть NULL до регистрации)
    referral_code VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, completed, cancelled
    created_at TIMESTAMP DEFAULT NOW(),
    converted_at TIMESTAMP NULL,
    discount_applied DECIMAL(10,2) NULL,
    reward_amount DECIMAL(10,2) NULL,
    INDEX idx_referrer_id (referrer_id),
    INDEX idx_invited_user_id (invited_user_id),
    INDEX idx_code (referral_code),
    INDEX idx_status (status)
);

-- История разблокировки наград (опционально)
CREATE TABLE referral_reward_unlocks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    reward_id VARCHAR(50) NOT NULL,
    unlocked_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_id (user_id)
);
```

---

### 🔐 Авторизация

**Как проверить токен:**
- Токен приходит в заголовке: `Authorization: Bearer {token}`
- Нужно декодировать JWT токен и получить `user_id`
- Проверить, что токен не истек
- Проверить, что пользователь существует и активен

**Пример проверки (Python):**
```python
import jwt
from datetime import datetime

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        # Проверить в базе данных, что пользователь существует
        user = db.get_user(user_id)
        if not user or not user.is_active:
            raise Exception("User not found or inactive")
        return user
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
```

---

### 🎯 Логика работы реферальной программы

**Как работает приглашение:**

1. **Пользователь A получает реферальный код** (например: `ABC123`)
2. **Пользователь A делится ссылкой** `https://aladdin.family/invite/ABC123`
3. **Пользователь B переходит по ссылке** → открывается страница регистрации
4. **Пользователь B регистрируется** → в базе создается запись:
   - `referrer_id` = ID пользователя A
   - `referral_code` = "ABC123"
   - `status` = "pending"
5. **Пользователь B оплачивает подписку** → статус меняется на "completed"
6. **Пользователь A получает награду** → обновляется статистика

**Когда засчитывается реферал:**
- Когда приглашенный пользователь **оплачивает подписку** (не просто регистрируется)
- Статус меняется с `pending` на `completed`
- Записывается `converted_at` = текущая дата
- Начисляется награда рефереру

---

## 2. Настройка домена aladdin.family для реферальных ссылок

### 📌 Что это такое?

Нужно настроить домен `aladdin.family`, чтобы ссылки вида `https://aladdin.family/invite/ABC123` работали и открывали страницу регистрации с автоматическим применением реферального кода.

### 🔧 Что нужно сделать:

#### Шаг 1: Купить домен aladdin.family

**Где купить:**
- [Namecheap](https://www.namecheap.com/)
- [GoDaddy](https://www.godaddy.com/)
- [Reg.ru](https://www.reg.ru/) (для России)
- [Timeweb](https://timeweb.com/) (для России)

**Стоимость:** ~$10-30/год

**Что нужно:**
- Зарегистрировать домен `aladdin.family`
- Получить доступ к DNS настройкам

---

#### Шаг 2: Настроить DNS записи

**Вариант A: Поддомен (рекомендуется)**

Настроить `aladdin.family` как поддомен вашего основного сайта:

```
A запись:
aladdin.family → 149.154.65.180

Или CNAME:
aladdin.family → aladdin-ai.ru
```

**Вариант B: Отдельный сервер**

Если хотите отдельный сервер для реферальных ссылок:
- Настроить веб-сервер (nginx/apache) на 149.154.65.180
- Настроить DNS: `aladdin.family → 149.154.65.180`

---

#### Шаг 3: Настроить веб-сервер (nginx)

**Конфигурация nginx для aladdin.family:**

```nginx
server {
    listen 80;
    server_name aladdin.family www.aladdin.family;
    
    # Редирект на HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name aladdin.family www.aladdin.family;
    
    # SSL сертификат (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/aladdin.family/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/aladdin.family/privkey.pem;
    
    # Реферальные ссылки: /invite/{code}
    location ~ ^/invite/([A-Z0-9-]+)$ {
        # Перенаправляем на страницу регистрации с кодом
        return 301 https://aladdin-ai.ru/register?ref=$1;
    }
    
    # Или проксировать на ваш бэкенд
    location / {
        proxy_pass http://localhost:8000;  # Ваш Python backend
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

#### Шаг 4: Создать страницу регистрации с обработкой реферального кода

**На сайте aladdin-ai.ru:**

**URL:** `https://aladdin-ai.ru/register?ref=ABC123`

**Что должно происходить:**

1. **Проверить параметр `ref` в URL**
2. **Сохранить реферальный код в сессии/cookie**
3. **Показать форму регистрации**
4. **При регистрации автоматически применить реферальный код**

**Пример (JavaScript):**
```javascript
// На странице регистрации
const urlParams = new URLSearchParams(window.location.search);
const referralCode = urlParams.get('ref');

if (referralCode) {
    // Сохранить код в localStorage или отправить на сервер
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

#### Шаг 5: Установить SSL сертификат (Let's Encrypt)

**Для HTTPS обязательно нужен SSL сертификат:**

```bash
# Установить certbot
sudo apt install certbot python3-certbot-nginx

# Получить сертификат
sudo certbot --nginx -d aladdin.family -d www.aladdin.family

# Автоматическое обновление
sudo certbot renew --dry-run
```

---

### 🎯 Рекомендации по настройке

**Вариант 1: Простой редирект (быстро)**
- `aladdin.family/invite/ABC123` → редирект на `aladdin-ai.ru/register?ref=ABC123`
- Минимум настроек, работает сразу

**Вариант 2: Отдельная страница (лучше UX)**
- `aladdin.family/invite/ABC123` → красивая landing страница с информацией о реферальной программе
- Кнопка "Зарегистрироваться" ведет на `aladdin-ai.ru/register?ref=ABC123`
- Можно добавить счетчик: "Уже 5 человек присоединились по этому коду!"

**Вариант 3: Прокси на бэкенд (гибко)**
- `aladdin.family/invite/ABC123` → прокси на ваш Python backend
- Backend генерирует HTML страницу с реферальным кодом
- Полный контроль над контентом

**Рекомендация:** Начать с Варианта 1 (простой редирект), потом перейти на Вариант 2 для лучшего UX.

---

## 3. Тестирование на реальных устройствах

### 📌 Что это такое?

Проверка, что все функции реферальной программы работают на реальных iPhone/iPad с реальными приложениями (WhatsApp, Telegram, VK).

### 🔧 Что нужно проверить:

#### Тест 1: Загрузка реферального кода из API

**Что проверить:**
- [ ] Открыть приложение → Профиль → "Пригласить друзей"
- [ ] Реферальный код загружается и отображается
- [ ] Если API возвращает ошибку, показывается сообщение об ошибке
- [ ] Если код пустой, показывается fallback "ALADDIN"

**Как проверить:**
1. Запустить приложение на реальном iPhone
2. Войти в аккаунт
3. Перейти в Профиль → "Пригласить друзей"
4. Проверить, что код появился

**Что должно быть:**
- Код отображается (например: "ABC123")
- Кнопка копирования работает
- Haptic feedback при копировании

---

#### Тест 2: WhatsApp приглашение

**Сценарий A: WhatsApp установлен**
- [ ] Нажать "Пригласить через WhatsApp"
- [ ] Открывается WhatsApp
- [ ] Текст с реферальным кодом и ссылкой вставляется автоматически
- [ ] Можно выбрать контакт и отправить

**Сценарий B: WhatsApp не установлен**
- [ ] Нажать "Пригласить через WhatsApp"
- [ ] Открывается WhatsApp Web (`https://wa.me/?text=...`)
- [ ] Или открывается системный Share Sheet

**Как проверить:**
1. Установить WhatsApp на тестовый iPhone
2. Нажать кнопку WhatsApp в приложении
3. Проверить, что WhatsApp открылся с текстом
4. Удалить WhatsApp
5. Повторить → должен открыться Share Sheet

---

#### Тест 3: Telegram приглашение

**Сценарий A: Telegram установлен**
- [ ] Нажать "Пригласить через Telegram"
- [ ] Открывается Telegram
- [ ] Текст с реферальным кодом и ссылкой готов к отправке

**Сценарий B: Telegram не установлен**
- [ ] Нажать "Пригласить через Telegram"
- [ ] Открывается Telegram Web или Share Sheet

**Как проверить:**
1. Установить Telegram на тестовый iPhone
2. Нажать кнопку Telegram в приложении
3. Проверить, что Telegram открылся
4. Удалить Telegram
5. Повторить → должен открыться Share Sheet

---

#### Тест 4: VK приглашение

**Сценарий A: VK установлен**
- [ ] Нажать "Пригласить через VK"
- [ ] Открывается VK
- [ ] Открывается окно "Поделиться" с ссылкой

**Сценарий B: VK не установлен**
- [ ] Нажать "Пригласить через VK"
- [ ] Открывается VK Web или Share Sheet

**Как проверить:**
1. Установить VK на тестовый iPhone
2. Нажать кнопку VK в приложении
3. Проверить, что VK открылся
4. Удалить VK
5. Повторить → должен открыться Share Sheet

---

#### Тест 5: Системный Share Sheet

**Что проверить:**
- [ ] Нажать "Поделиться еще"
- [ ] Открывается системный Share Sheet
- [ ] Можно выбрать любой способ отправки (SMS, Email, другие приложения)
- [ ] Текст корректно передается

**Как проверить:**
1. Нажать кнопку "Поделиться еще"
2. Проверить, что открылся Share Sheet
3. Выбрать SMS → проверить, что текст вставился
4. Выбрать Email → проверить, что текст вставился

---

#### Тест 6: Копирование кода и ссылки

**Копирование кода:**
- [ ] Нажать кнопку "Копировать код"
- [ ] Код копируется в буфер обмена
- [ ] Haptic feedback срабатывает
- [ ] Можно вставить код в другое приложение

**Копирование ссылки:**
- [ ] Нажать кнопку "Копировать ссылку"
- [ ] Ссылка копируется в буфер обмена
- [ ] Haptic feedback срабатывает
- [ ] Можно вставить ссылку в другое приложение

**Как проверить:**
1. Нажать "Копировать код"
2. Открыть Notes → вставить → проверить, что код вставился
3. Нажать "Копировать ссылку"
4. Открыть Notes → вставить → проверить, что ссылка вставилась

---

#### Тест 7: QR-код

**Что проверить:**
- [ ] Нажать "Показать QR-код"
- [ ] Открывается модальное окно с QR-кодом
- [ ] QR-код отображается корректно
- [ ] Можно отсканировать QR-код другим устройством
- [ ] При сканировании открывается правильная ссылка

**Как проверить:**
1. Нажать "Показать QR-код"
2. Проверить, что QR-код отображается
3. Открыть камеру на другом iPhone
4. Навести на QR-код
5. Проверить, что открылась ссылка `https://aladdin.family/invite/ABC123`

---

#### Тест 8: Статистика и история

**Что проверить:**
- [ ] Статистика загружается из API
- [ ] Отображаются правильные числа (приглашенные, оплатившие, конверсия)
- [ ] История загружается
- [ ] Отображаются все приглашенные пользователи
- [ ] Статусы отображаются корректно (pending/completed)

**Как проверить:**
1. Пригласить тестового пользователя
2. Проверить, что статистика обновилась
3. Проверить, что в истории появилась новая запись
4. Оплатить подписку тестовым пользователем
5. Проверить, что статус изменился на "completed"

---

#### Тест 9: Награды

**Что проверить:**
- [ ] Награды загружаются из API
- [ ] Отображаются правильные награды (1 реферал, 3 реферала, 10 рефералов)
- [ ] Статус разблокировки корректный (unlocked/locked)
- [ ] Прогресс-бары отображаются правильно
- [ ] При достижении награды статус меняется на "unlocked"

**Как проверить:**
1. Проверить текущие награды
2. Пригласить 1 пользователя и проверить, что награда за 1 реферала разблокировалась
3. Пригласить еще 2 пользователей и проверить, что награда за 3 реферала разблокировалась

---

#### Тест 10: Реферальная ссылка

**Что проверить:**
- [ ] Перейти по ссылке `https://aladdin.family/invite/ABC123`
- [ ] Открывается страница регистрации
- [ ] Реферальный код автоматически применяется
- [ ] После регистрации реферал засчитывается

**Как проверить:**
1. Скопировать реферальную ссылку из приложения
2. Открыть ссылку в Safari на другом устройстве
3. Проверить, что открылась страница регистрации
4. Проверить, что в URL есть параметр `?ref=ABC123`
5. Зарегистрироваться
6. Проверить в приложении, что реферал появился в истории

---

### 📱 Устройства для тестирования

**Минимум:**
- iPhone с iOS 15.2+ (для симулятора)
- Реальный iPhone для тестирования мессенджеров

**Рекомендуется:**
- iPhone 11 Pro Max (6.5") - для скриншотов App Store
- iPhone 14 Pro Max (6.7") - для скриншотов App Store
- iPhone с установленными WhatsApp, Telegram, VK
- iPhone без этих приложений (для тестирования fallback)

---

### 🐛 Чеклист багов

**Если что-то не работает:**

1. **Код не загружается:**
   - Проверить, что API endpoint `/api/referral/code` работает
   - Проверить авторизацию (токен в заголовках)
   - Проверить логи сервера

2. **Мессенджер не открывается:**
   - Проверить, что URL схема правильная (`whatsapp://`, `tg://`, `vk://`)
   - Проверить, что приложение установлено
   - Проверить, что в Info.plist есть `LSApplicationQueriesSchemes`

3. **Ссылка не работает:**
   - Проверить DNS настройки домена `aladdin.family`
   - Проверить, что веб-сервер настроен правильно
   - Проверить SSL сертификат

4. **Реферал не засчитывается:**
   - Проверить, что при регистрации передается `referral_code`
   - Проверить, что на бэкенде создается запись в таблице `referrals`
   - Проверить, что при оплате статус меняется на "completed"

---

## 🎯 Приоритеты реализации

### Этап 1: Минимальная рабочая версия (1-2 дня)
1. ✅ Реализовать endpoint `/api/referral/code` (получение кода)
2. ✅ Настроить простой редирект `aladdin.family/invite/{code}` → `aladdin-ai.ru/register?ref={code}`
3. ✅ Протестировать копирование кода и ссылки

### Этап 2: Полная функциональность (3-5 дней)
1. ✅ Реализовать все 4 endpoints
2. ✅ Настроить страницу регистрации с обработкой реферального кода
3. ✅ Протестировать все способы приглашения

### Этап 3: Полировка (1-2 дня)
1. ✅ Улучшить UX реферальной страницы
2. ✅ Добавить аналитику (сколько переходов по ссылке)
3. ✅ Финальное тестирование

---

## 📞 Контакты для помощи

Если нужна помощь с реализацией:
- **Backend разработчик** - для реализации API endpoints
- **DevOps** - для настройки DNS и веб-сервера
- **QA тестировщик** - для тестирования на реальных устройствах

---

**Последнее обновление:** 21 ноября 2024


