# 💳 Платёжный сайт ALADDIN — реализация alias+PIN

Дата: 17 ноября 2025  
Статус: подготовлен план внедрения `todo_payment_site`

---

## 1. Общая архитектура

```
Пользователь → Лендос (landing/index.html) → /api/payments/create → Платёжный провайдер
                                                   ↓
                                          Webhook /confirm
                                                   ↓
                                       Генерация кода + alias/PIN
                                                   ↓
                                /api/activation/verify + /activate (моб. приложение)
```

**Основные компоненты**
- **Frontend (landing)** — уже готов: форма alias+PIN, CTA, CMS данные, вызов `/api/payments/create`.
- **Payment Site API** — Node.js/FastAPI/Go (любая), отвечает за:
  - создание платежей;
  - обработку webhook’ов;
  - генерацию/хранение кодов;
  - выдачу кода по alias+PIN (`/activation/retrieve`);
  - валидацию/активацию кода для iOS.
- **Payment Provider** — собственные интеграции топ‑банков РФ (Сбербанк, Тинькофф, Альфа-Банк, ВТБ, Газпромбанк, Россельхозбанк, Совкомбанк, Уралсиб, Райффайзен RU, МКБ, Почта Банк, Промсвязьбанк, Росбанк, Ситибанк RU, Хоум Кредит, МТС Банк, Открытие, Ренессанс Кредит, Русский Стандарт, Синара, Траст). Каждый банк выдаёт QR/СБП и ссылку на оплату картой.

---

## 2. Таблицы данных (пример Postgres)

### payments
| поле | тип | описание |
| --- | --- | --- |
| id | uuid | внутренний ID |
| alias | text | псевдоним пользователя |
| pin_hash | text | `bcrypt` PIN |
| tariff_id | text | `free/personal/family/premium` |
| amount | integer | сумма в копейках |
| status | text | `created/awaiting_payment/paid/failed/refunded` |
| psp_id | text | ID платежа в провайдере |
| created_at / updated_at | timestamptz | даты |

### activation_codes
| поле | тип | описание |
| code | text | ALDN-XXXX-XXXX |
| alias | text | связь с платежом |
| tariff_id | text | тариф |
| status | text | `pending/active/redeemed/expired` |
| expires_at | timestamptz | срок действия |
| redeemed_at | timestamptz | дата активации |

---

## 3. API эндпоинты

### 3.1 `/api/payment-methods` (GET)
Возвращает список доступных способов оплаты (QR/СБП, карты конкретных банков, SberPay/Tinkoff Pay, прямой перевод). Используется лендингом и мобильным приложением для показа селектора и валидации `paymentMethod`.

### 3.2 `/api/payments/create` (POST)
Вход:
```json
{
  "tariffId": "family",
  "userAlias": "familySmith",
  "pin": "1234",
  "paymentMethod": "qr_sbp"
}
```
Выход:
```json
{
  "paymentId": "pay_123",
  "redirectUrl": "https://psp.example/checkout?token=... (если карты)",
  "qrData": "base64..." (если QR/СБП),
  "expiresAt": "2025-11-20T12:00:00Z"
}
```
Действия:
1. Проверить `alias` (6+ символов, латиница/цифры) и `pin` (4–6 цифр).
2. Захэшировать PIN (`bcrypt`).
3. Создать запись `payments` (`status=created`).
4. Инициировать платёж в провайдере (SDK/API).
5. Вернуть `redirectUrl`/`qrData`.

### 3.2 `/api/payments/status/:paymentId` (GET, опционально)
Возвращает текущий статус и код (если сгенерирован) для лендинга, если нет вебхука.

### 3.4 Webhook `/api/payments/confirm` (POST)
```json
{
  "paymentId": "pay_123",
  "status": "paid",
  "amount": 49000,
  "currency": "RUB",
  "pspTxnId": "abc-456"
}
```
Действия:
1. Проверить idempotency (по `pspTxnId`).
2. Если `status=paid`:
   - обновить `payments.status = paid`, `psp_id = ...`;
   - сгенерировать код `ALDN-XXXX-XXXX` (см. раздел 4);
   - добавить запись в `activation_codes` (`status=active`, срок действия 30 дней).
3. Если `failed`/`refunded` — обновить статус, не создавать код.
4. Ответ `200 { "ok": true }`.

### 3.5 `/api/activation/retrieve` (POST, сайт)
Запрос:
```json
{ "userAlias": "familySmith", "pin": "1234" }
```
Ответ:
```json
{
  "activationCode": "ALDN-1234-5678",
  "status": "active",
  "expiresAt": "2026-01-01T00:00:00Z"
}
```
Ошибки: неверный PIN, нет кода, код активирован/истёк.

### 3.6 `/api/activation/verify` и `/api/activation/activate` (моб. приложение)
Спецификация взята из плана (раздел 18.5).

---

## 4. Генерация кода активации

```
prefix = "ALDN"
body = 12 символов (A-Z0-9), группировать по 4
пример: ALDN-8K3Q-2PS5-9LM4
```

Алгоритм:
```python
import secrets, string
alphabet = string.ascii_uppercase + string.digits
code = '-'.join(''.join(secrets.choice(alphabet) for _ in range(4)) for _ in range(3))
activation_code = f'ALDN-{code}'
```

Проверить уникальность в `activation_codes`.

---

## 5. Статусы и таймауты

| Сущность | Событие | Статус | Действие |
| --- | --- | --- | --- |
| Payment | создание | `created` | ожидание оплаты (15 мин) |
| Payment | платёж подтверждён | `paid` | генерируем код |
| Payment | платёж отклонён | `failed` | нет кода, алиас освобождать не нужно |
| Code | создан | `active` | доступен к выдаче и активации |
| Code | активирован | `redeemed` | сохранить `familyId`, `deviceId` |
| Code | срок истёк | `expired` | разрешить повторную покупку |

**Таймеры**
- Payment `created` → `awaiting_payment` (если QR): 5 минут на оплату.
- Activation code: срок действия 30 дней.

---

## 6. Безопасность

- ✅ `alias` и `pin` шифровать/хэшировать (`pin_hash`, `alias` можно хранить в явном виде для поиска) — реализовано.
- ✅ Ограничение запросов на `/activation/retrieve` (rate limit) — реализовано: 5 запросов/минуту на комбинацию `alias:IP`.
- ✅ Webhook проверять по `X-Signature` от провайдера (HMAC-SHA256) — реализовано.
- ✅ API защищать по `X-API-Key` (как на форме) — реализовано.
- ✅ Idempotency для вебхуков (повторные вебхуки с одним `pspTxnId` игнорируются) — реализовано.
- Логи событий отправлять в ClickHouse/Amplitude для аналитики (в планах).

---

## 7. План реализации

1. **Инфраструктура**
   - Репозиторий `payments-site`, язык Python FastAPI (или другой).
   - Docker (Postgres + приложение).
2. **База данных**
   - Миграции для таблиц `payments`, `activation_codes`.
3. **Интеграция с PSP**
- Настроить прямые интеграции/SDK банков (Сбербанк, Тинькофф, Альфа и т.д.).
   - Настроить API ключи, webhook URL.
4. **API**
   - `/api/payments/create`
   - `/api/payments/confirm`
   - `/api/activation/retrieve`
   - `/api/activation/verify`, `/activate`
5. **Админ/поддержка**
   - CLI/панель для просмотра платежей по alias/PIN.
6. **Тестирование**
   - Юнит тесты генерации кодов, валидации alias/PIN.
   - Интеграция с тестовой средой PSP.
7. **Деплой**
   - ENV: `DATABASE_URL`, `PSP_API_KEY`, `X_API_KEY_PUBLIC`.
   - Размещение на VPS или PaaS (Render, Fly.io).

---

## 8. Статус реализации

### ✅ Реализовано
1. ✅ Backend (FastAPI + SQLite) с `/api/payments/create`.
2. ✅ Webhook `/api/payments/confirm` с проверкой подписи и idempotency.
3. ✅ `/activation/retrieve` с rate limiting (5 запросов/минуту).
4. ✅ `/activation/verify` и `/activate`.
5. ✅ Защита вебхуков (HMAC-SHA256 подписи).
6. ✅ Rate limiting на `/activation/retrieve`.

### 🔄 В планах
1. Подключить реальные банковские шлюзы (требуются API ключи и договоры).
2. Добавить админ-панель/CLI для поддержки.
3. Протестировать end-to-end (платёж → код → активация) с реальными банками.

### 📋 Следующие шаги
После получения API ключей от банков — подключить реальные интеграции. Затем закрыть `todo_payment_site` и перейти к `todo_legal_publication` + финальные скриншоты. 

