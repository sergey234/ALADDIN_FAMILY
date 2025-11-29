# 🚀 ПОЛНЫЙ ПЛАН РЕАЛИЗАЦИИ РЕФЕРАЛЬНОЙ ПРОГРАММЫ (ОБНОВЛЕННЫЙ)

**Дата обновления:** 22 ноября 2024  
**Сервер:** 149.154.65.180  
**Сайт:** https://aladdin-ai.ru/  
**Реферальные ссылки:** https://aladdin-ai.ru/invite/{code}

---

## ✅ ЧТО УЖЕ РЕАЛИЗОВАНО (Клиентская часть)

### 1. iOS приложение
- ✅ API интеграция (4 endpoints в APIService)
- ✅ Модели данных (ReferralOverviewResponse, ReferralStatsResponse, etc.)
- ✅ UI/UX исправлен (кнопки кликабельны, скролл работает)
- ✅ URL схемы настроены (WhatsApp, Telegram, VK в Info.plist)
- ✅ Fallback механизмы работают
- ✅ Локализация обновлена

### 2. Лендинг (клиентская часть)
- ✅ Страница `invite.html` создана
- ✅ Обработка реферального кода из URL (`?ref=CODE` или `#pay?ref=CODE`)
- ✅ Автоматическое применение скидки -20% для приглашенного
- ✅ Баннер со скидкой при наличии реферального кода
- ✅ Передача `referralCode` при оплате на сервер
- ✅ Автопрокрутка к форме оплаты при переходе на `#pay`
- ✅ Обновленный `index.html` с логикой реферальной программы

---

## ⚠️ ЧТО НУЖНО РЕАЛИЗОВАТЬ (Серверная часть)

### 🎁 НОВАЯ ЛОГИКА СКИДОК

#### Для приглашенного пользователя:
- ✅ **УЖЕ РАБОТАЕТ** — скидка -20% применяется сразу при оплате на клиенте
- ⚠️ **НУЖНО НА СЕРВЕРЕ** — подтверждение и учет скидки

#### Для реферера (тот, кто пригласил):
- ⚠️ **ТРЕБУЕТСЯ РЕАЛИЗАЦИЯ** — скидка -20% на следующий месяц после того, как друг оплатит

---

## 📋 ДЕТАЛЬНЫЙ ПЛАН РЕАЛИЗАЦИИ НА СЕРВЕРЕ

### 🟢 ЭТАП 1: База данных (1-2 часа)

#### Задача 1.1: Создать таблицы
- [ ] Выполнить SQL скрипт `REFERRAL_DB_SETUP.sql`
- [ ] Создать таблицу `referral_codes`
  - `user_id` (UNIQUE) — один код на пользователя
  - `code` (UNIQUE) — уникальный реферальный код
- [ ] Создать таблицу `referrals`
  - `referrer_id` — кто пригласил
  - `invited_user_id` — кого пригласили
  - `status` — 'pending' / 'completed' / 'cancelled'
  - `discount_applied` — размер скидки для приглашенного
  - `reward_amount` — награда рефереру
- [ ] Создать индексы для быстрого поиска
- [ ] Настроить внешние ключи (foreign keys)

#### Задача 1.2: Создать таблицу для скидок реферера (НОВОЕ)
- [ ] Создать таблицу `referral_discounts`:
```sql
CREATE TABLE referral_discounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    discount_percent DECIMAL(5,2) NOT NULL DEFAULT 20.0,
    discount_type VARCHAR(50) NOT NULL DEFAULT 'referral_reward',
    valid_from TIMESTAMP NOT NULL,
    valid_until TIMESTAMP NOT NULL,
    used_at TIMESTAMP NULL,
    referral_id INTEGER REFERENCES referrals(id),
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_referral_discounts_user_id ON referral_discounts(user_id);
CREATE INDEX idx_referral_discounts_valid ON referral_discounts(valid_until, used_at);
```

**Логика:**
- Хранит активные скидки для рефереров
- `valid_from` / `valid_until` — период действия скидки
- `used_at` — когда скидка была использована (NULL = не использована)
- `referral_id` — связь с записью в `referrals`

---

### 🟡 ЭТАП 2: API Endpoints (4-6 часов)

#### Задача 2.1: GET `/api/referral/code`
- [ ] Проверка авторизации (токен)
- [ ] Получение или создание реферального кода для пользователя
- [ ] Подсчет статистики (количество приглашенных, заработанный бонус)
- [ ] Возврат JSON с кодом и ссылкой

**Файл:** `docs/server/REFERRAL_API_ENDPOINTS.py` (уже создан, нужно интегрировать)

---

#### Задача 2.2: GET `/api/referral/stats`
- [ ] Подсчет общей статистики
- [ ] Конверсия (pending → completed)
- [ ] Уровни (bronze, silver, gold)

---

#### Задача 2.3: GET `/api/referral/history`
- [ ] Список всех приглашенных пользователей
- [ ] Статусы и даты
- [ ] Награды и скидки

---

#### Задача 2.4: GET `/api/referral/rewards`
- [ ] Список наград
- [ ] Статусы разблокировки
- [ ] Прогресс до следующей награды

---

### 🟡 ЭТАП 3: Обработка реферального кода при оплате (КРИТИЧНО!)

#### Задача 3.1: Модификация `/api/payments/create` (НОВОЕ)

**Что нужно добавить:**

```python
@router.post("/api/payments/create")
async def create_payment(payment_data: PaymentCreate):
    # 1. Создать платеж (существующая логика)
    payment = create_payment_in_db(
        tariff_id=payment_data.tariffId,
        user_alias=payment_data.userAlias,
        pin=payment_data.pin,
        payment_method=payment_data.paymentMethod,
        period_months=payment_data.periodMonths,
        amount=payment_data.amount,  # Уже со скидкой -20% от клиента
        referral_code=payment_data.referralCode  # ✅ НОВОЕ: Принимаем код
    )
    
    # 2. ✅ НОВОЕ: Если есть referralCode, создать запись в referrals
    if payment_data.referralCode:
        referral_code_obj = db.get_referral_code(payment_data.referralCode)
        if referral_code_obj:
            # Вычислить оригинальную цену (до скидки)
            original_price = payment_data.amount / 0.8  # Если скидка 20%
            discount_applied = original_price - payment_data.amount
            
            # Создать запись о реферале
            db.create_referral(
                referrer_id=referral_code_obj.user_id,
                invited_user_id=payment.user_id,  # ID нового пользователя (после регистрации)
                referral_code=payment_data.referralCode,
                status="pending",  # Пока не оплатил
                discount_applied=discount_applied  # Размер скидки
            )
    
    return {"paymentId": payment.id, ...}
```

**Файл:** `docs/server/REFERRAL_PAYMENT_HANDLER.py` (уже создан, нужно интегрировать)

---

#### Задача 3.2: Модификация `/api/payments/status/{payment_id}` (НОВОЕ)

**Что нужно добавить:**

```python
@router.get("/api/payments/status/{payment_id}")
async def check_payment_status(payment_id: str):
    payment = get_payment(payment_id)
    
    # Существующая логика проверки статуса...
    
    # ✅ НОВОЕ: Если платеж подтвержден, обработать реферальную программу
    if payment.status == 'paid':
        # 1. Найти реферальную запись для этого пользователя
        referral = db.get_referral_by_invited_user(payment.user_id)
        
        if referral and referral.status == "pending":
            # 2. Вычислить награду рефереру (20% от оригинальной цены)
            original_price = payment.amount / 0.8  # Восстанавливаем оригинальную цену
            reward_amount = original_price * 0.2  # 20% награда
            
            # 3. Обновить статус реферала на "completed"
            db.update_referral(
                referral_id=referral.id,
                status="completed",
                converted_at=datetime.now(),
                discount_applied=referral.discount_applied,  # Уже сохранено при создании
                reward_amount=reward_amount
            )
            
            # 4. ✅ НОВОЕ: Начислить скидку -20% рефереру на следующий месяц
            next_month_start = calculate_next_month_start()
            next_month_end = calculate_next_month_end()
            
            db.create_referral_discount(
                user_id=referral.referrer_id,
                discount_percent=20.0,
                discount_type="referral_reward",
                valid_from=next_month_start,
                valid_until=next_month_end,
                referral_id=referral.id
            )
            
            # 5. Опционально: Отправить уведомление рефереру о начислении скидки
    
    return {"status": payment.status, ...}
```

**Файл:** `docs/server/REFERRAL_PAYMENT_HANDLER.py` (уже создан, нужно интегрировать)

---

#### Задача 3.3: Применение скидки рефереру при следующей оплате (НОВОЕ)

**Что нужно добавить:**

```python
def apply_referral_discount(user_id: int, original_price: float) -> float:
    """
    Применяет реферальную скидку -20% к цене для реферера
    Вызывается при создании платежа для реферера
    """
    # Проверить, есть ли активная скидка от реферальной программы
    discount = db.get_active_referral_discount(
        user_id=user_id,
        current_date=datetime.now()
    )
    
    if discount:
        discount_amount = original_price * (discount.discount_percent / 100)
        final_price = original_price - discount_amount
        
        # Пометить скидку как использованную
        db.mark_discount_as_used(discount.id, used_at=datetime.now())
        
        return final_price
    
    return original_price

# Использование в /api/payments/create:
@router.post("/api/payments/create")
async def create_payment(payment_data: PaymentCreate):
    # ... существующая логика ...
    
    # ✅ НОВОЕ: Если пользователь - реферер, проверить активную скидку
    if not payment_data.referralCode:  # Если это не приглашенный, а реферер
        final_amount = apply_referral_discount(
            user_id=current_user.id,
            original_price=calculated_price
        )
        payment_data.amount = final_amount
    
    # ... остальная логика ...
```

**Где добавить:**
- В существующий endpoint `/api/payments/create`
- Перед созданием платежа в БД

---

### 🟡 ЭТАП 4: Landing страница `/invite/{code}` (2-3 часа)

#### Задача 4.1: Развернуть страницу на сервере
- [ ] Загрузить `landing/invite.html` на сервер
- [ ] Настроить Nginx для обработки `/invite/{code}`
- [ ] Проверить работу ссылок

**Файл:** `landing/invite.html` (уже создан и готов)

**Nginx конфигурация:**
```nginx
location /invite/ {
    # Вариант 1: Статический файл
    try_files $uri $uri/ /invite.html?code=$1;
    
    # Вариант 2: Прокси на Python backend
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
}
```

**Файл:** `docs/server/NGINX_CONFIG.conf` (уже создан)

---

### 🟡 ЭТАП 5: Регистрация с реферальным кодом (1-2 часа)

#### Задача 5.1: Обработка `?ref=CODE` на странице регистрации
- [ ] JavaScript на фронтенде извлекает код из URL
- [ ] Сохранение кода в localStorage/сессии
- [ ] Передача кода при регистрации на сервер

**Примечание:** На лендинге уже реализовано:
- ✅ `invite.html` → переход на `index.html#pay?ref=CODE`
- ✅ `index.html` → обработка `?ref=CODE` и применение скидки
- ✅ Код передается при оплате: `referralCode: "ABC123"`

**Что нужно на сервере:**
- Принять `referralCode` в `/api/payments/create` (уже описано в Этапе 3)

---

### 🟡 ЭТАП 6: Тестирование (1 день)

#### Задача 6.1: Тестирование полного цикла
- [ ] Реферер получает код через `/api/referral/code`
- [ ] Реферер приглашает друга по ссылке
- [ ] Друг переходит по ссылке `aladdin-ai.ru/invite/ABC123`
- [ ] Друг видит скидку -20% на форме оплаты
- [ ] Друг оплачивает подписку (800₽ вместо 1000₽)
- [ ] Сервер создает запись в `referrals` (status: pending)
- [ ] При подтверждении оплаты статус обновляется на `completed`
- [ ] Рефереру начисляется скидка -20% на следующий месяц
- [ ] При следующей оплате реферер платит 800₽ вместо 1000₽

#### Задача 6.2: Тестирование API endpoints
- [ ] GET `/api/referral/code` — возвращает код
- [ ] GET `/api/referral/stats` — возвращает статистику
- [ ] GET `/api/referral/history` — возвращает историю
- [ ] GET `/api/referral/rewards` — возвращает награды

#### Задача 6.3: Тестирование на реальных устройствах
- [ ] Мобильное приложение iOS
- [ ] Все способы приглашения (WhatsApp, Telegram, VK, Share Sheet)
- [ ] Реферальные ссылки работают

---

## 📊 СХЕМА РАБОТЫ РЕФЕРАЛЬНОЙ ПРОГРАММЫ

```
┌─────────────────────────────────────────────────────────────┐
│ 1. РЕФЕРЕР (тот, кто пригласил)                             │
│    - Получает код через /api/referral/code                  │
│    - Код: ABC123                                            │
│    - Приглашает друга по ссылке                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. ПРИГЛАШЕННЫЙ (тот, кого пригласили)                      │
│    - Переходит: aladdin-ai.ru/invite/ABC123                 │
│    - Видит приглашение и код                                │
│    - Нажимает "Получить скидку -20%"                        │
│    - Переходит на index.html#pay?ref=ABC123                 │
│    - Видит баннер: "🎁 У вас применена скидка -20%!"        │
│    - Цена автоматически уменьшена: 800₽ (было 1000₽)        │
│    - Оплачивает подписку                                    │
│    - referralCode передается на сервер                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. СЕРВЕР: /api/payments/create                             │
│    - Принимает referralCode: "ABC123"                       │
│    - Находит реферера по коду                               │
│    - Создает запись в referrals (status: pending)          │
│    - Сохраняет discount_applied = 200₽                      │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. СЕРВЕР: /api/payments/status/{payment_id}               │
│    - Платеж подтвержден: status = 'paid'                    │
│    - Обновляет referrals: status = 'completed'              │
│    - Устанавливает converted_at = NOW()                     │
│    - Вычисляет reward_amount = 200₽ (20% от 1000₽)         │
│    - Создает запись в referral_discounts для реферера       │
│    - Скидка -20% на следующий месяц для реферера            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. РЕФЕРЕР: Следующая оплата                                │
│    - При оплате следующего месяца                           │
│    - Сервер проверяет активную скидку в referral_discounts │
│    - Применяет скидку -20% автоматически                    │
│    - Реферер платит 800₽ вместо 1000₽                       │
│    - Скидка помечается как использованная                   │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ ИТОГОВЫЙ TODO ЛИСТ

### 🟢 КРИТИЧНО (Базовые функции)

#### База данных
- [ ] Выполнить `REFERRAL_DB_SETUP.sql` на сервере
- [ ] Создать таблицу `referral_codes`
- [ ] Создать таблицу `referrals`
- [ ] **НОВОЕ:** Создать таблицу `referral_discounts`
- [ ] Проверить индексы и внешние ключи

#### API Endpoints
- [ ] Интегрировать GET `/api/referral/code`
- [ ] Интегрировать GET `/api/referral/stats`
- [ ] Интегрировать GET `/api/referral/history`
- [ ] Интегрировать GET `/api/referral/rewards`

#### Обработка реферального кода при оплате
- [ ] **НОВОЕ:** Модифицировать `/api/payments/create` — принимать `referralCode`
- [ ] **НОВОЕ:** Создавать запись в `referrals` при оплате (status: pending)
- [ ] **НОВОЕ:** Модифицировать `/api/payments/status/{payment_id}` — обновлять статус на `completed`
- [ ] **НОВОЕ:** Начислять скидку рефереру при подтверждении оплаты
- [ ] **НОВОЕ:** Создать функцию `apply_referral_discount()` для реферера

---

### 🟡 ВАЖНО (UX и функциональность)

#### Landing страница
- [ ] Загрузить `invite.html` на сервер
- [ ] Настроить Nginx для `/invite/{code}`
- [ ] Проверить работу ссылок

#### Тестирование
- [ ] Протестировать полный цикл (реферер → приглашенный → оплата → скидка рефереру)
- [ ] Протестировать API endpoints
- [ ] Протестировать на реальных устройствах

---

### 🟢 ЖЕЛАТЕЛЬНО (Улучшения)

- [ ] Добавить уведомления рефереру о начислении скидки
- [ ] Добавить счетчик переходов по реферальным ссылкам
- [ ] Добавить аналитику реферальной программы

---

## 📝 ФАЙЛЫ ДЛЯ ИНТЕГРАЦИИ

### Уже созданы и готовы:
1. ✅ `docs/server/REFERRAL_DB_SETUP.sql` — SQL схема (нужно дополнить таблицей `referral_discounts`)
2. ✅ `docs/server/REFERRAL_API_ENDPOINTS.py` — 4 API endpoints
3. ✅ `docs/server/REFERRAL_PAYMENT_HANDLER.py` — обработка оплаты (нужно дополнить)
4. ✅ `docs/server/REFERRAL_REGISTRATION_HANDLER.py` — обработка регистрации
5. ✅ `docs/server/NGINX_CONFIG.conf` — конфигурация Nginx
6. ✅ `landing/invite.html` — реферальная страница
7. ✅ `landing/index.html` — обновленный лендинг с логикой скидок

### Нужно создать:
1. ⚠️ Дополнить `REFERRAL_DB_SETUP.sql` — добавить таблицу `referral_discounts`
2. ⚠️ Дополнить `REFERRAL_PAYMENT_HANDLER.py` — логика начисления скидки рефереру
3. ⚠️ Создать функцию `apply_referral_discount()` — применение скидки при оплате реферера

---

## 🎯 ПРИОРИТЕТЫ

1. **Критично:** База данных + обработка `referralCode` при оплате
2. **Важно:** Начисление скидки рефереру + применение скидки при следующей оплате
3. **Важно:** API endpoints для мобильного приложения
4. **Желательно:** Landing страница и тестирование

---

## 📊 ОЦЕНКА ВРЕМЕНИ

- **Этап 1 (База данных):** 1-2 часа
- **Этап 2 (API Endpoints):** 4-6 часов
- **Этап 3 (Обработка оплаты):** 3-4 часа ⚠️ **НОВОЕ**
- **Этап 4 (Landing страница):** 2-3 часа
- **Этап 5 (Регистрация):** 1-2 часа
- **Этап 6 (Тестирование):** 1 день

**Итого:** 2-3 дня работы

---

## ✅ СТАТУС ГОТОВНОСТИ

### Клиентская часть: ✅ 100%
- iOS приложение: ✅ Готово
- Лендинг: ✅ Готово
- Логика скидок для приглашенного: ✅ Работает

### Серверная часть: ⚠️ 0%
- База данных: ⚠️ Требуется создание
- API endpoints: ⚠️ Требуется интеграция
- Обработка оплаты: ⚠️ Требуется реализация
- Логика скидок для реферера: ⚠️ Требуется реализация

---

**Последнее обновление:** 22 ноября 2024  
**Статус:** ✅ План обновлен с учетом новой логики скидок


