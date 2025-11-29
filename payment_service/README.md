# Aladdin Payment Service (FastAPI)

Минимальный backend для задач `todo_payment_site`: создаёт платежи по alias+PIN, обрабатывает webhook и генерирует коды активации.

## Стек
- Python 3.11+
- FastAPI + Uvicorn
- SQLAlchemy + SQLite (async)
- bcrypt для PIN

## Быстрый старт
```bash
cd payment_service
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

База создаётся автоматически (`payments.db`).

## ⚠️ Настройка Manual Transfer (Оплата на карту через СБП)

**ВАЖНО:** Для работы метода "Оплата на карту через СБП" нужно настроить переменные окружения:

### Вариант 1: Создать .env файл (рекомендуется)

1. Создайте файл `.env` в папке `payment_service/`:
```bash
cd payment_service
touch .env
```

2. Добавьте в `.env`:
```env
PAYMENT_CARD_NUMBER=2202 2083 0881 3410
# Если нужно скрыть ФИО — оставьте значение пустым
PAYMENT_CARD_HOLDER_NAME=
```

3. Перезапустите backend.

### Вариант 2: Установить переменные окружения

**macOS/Linux:**
```bash
export PAYMENT_CARD_NUMBER="2202 2083 0881 3410"
# Оставьте пустым, если не хотите показывать ФИО
export PAYMENT_CARD_HOLDER_NAME=""
```

**Windows (PowerShell):**
```powershell
$env:PAYMENT_CARD_NUMBER="2202 2083 0881 3410"
$env:PAYMENT_CARD_HOLDER_NAME=""
```

**Подробная инструкция:** см. `SETUP_MANUAL_TRANSFER.md`

## Переменные окружения
используют префикс `PAYMENT_`:

| var | по умолчанию | описание |
| --- | --- | --- |
| `PAYMENT_DATABASE_URL` | `sqlite+aiosqlite:///./payments.db` | URL БД |
| `PAYMENT_API_KEY_PUBLIC` | `PUBLIC_CLIENT_KEY` | проверка `X-API-Key` с лендинга |
| `PAYMENT_PSP_MOCK_REDIRECT_URL` | `https://pay.aladdin.family/mock-checkout` | заглушка checkout |
| `PAYMENT_WEBHOOK_SECRET` | `WEBHOOK_SECRET_KEY_CHANGE_IN_PRODUCTION` | секрет для проверки подписи вебхуков |
| `PAYMENT_ADMIN_KEY` | `ADMIN_SECRET_KEY_CHANGE_IN_PRODUCTION` | ключ для админ-эндпоинтов (ручное подтверждение платежей) |
| `PAYMENT_RATE_LIMIT_RETRIEVE_MAX` | `5` | максимум запросов на `/activation/retrieve` |
| `PAYMENT_RATE_LIMIT_RETRIEVE_WINDOW` | `60` | окно rate limit в секундах |
| `PAYMENT_CARD_NUMBER` | `""` | номер карты для приёма платежей через СБП (формат: `1234 5678 9012 3456`) |
| `PAYMENT_CARD_HOLDER_NAME` | `""` | имя держателя карты (например: `ИВАНОВ ИВАН ИВАНОВИЧ`) |

## Эндпоинты

### GET `/api/payment-methods`
Возвращает список всех доступных методов (QR/СБП, карты конкретных банков, SberPay/Tinkoff Pay, прямой перевод). Лендинг может использовать этот список вместо `cms/methods.json`.

### GET `/api/manual-transfer/info`
Возвращает номер карты и имя держателя из конфигурации (`PAYMENT_CARD_NUMBER`, `PAYMENT_CARD_HOLDER_NAME`). Используется лендингом как fallback, если данные не сохранились в `localStorage`.

### POST `/api/payments/create`
Создаёт платёж, ожидает `X-API-Key`.
```json
{
  "tariffId": "family",
  "userAlias": "familySmith",
  "pin": "1234",
  "paymentMethod": "qr_sbp"
}
```
Ответ содержит `paymentId`, `redirectUrl`/`qrData`, `expiresAt`.

### POST `/api/payments/confirm`
Webhook банков с проверкой подписи `X-Signature` (HMAC-SHA256). При `status=paid` генерирует код `ALDN-XXXX-XXXX` и сохраняет в `activation_codes`. Поддерживает idempotency (повторные вебхуки с одним `pspTxnId` игнорируются).

### POST `/api/activation/retrieve`
Alias+PIN → возвращает активный код и срок действия. Защищён rate limiting (5 запросов/минуту на `alias:IP`).

### POST `/api/activation/verify`
Проверка кода (мобильное приложение или сайт) без погашения.

### POST `/api/activation/activate`
Погашение кода: меняет статус на `redeemed`, фиксирует время активации.

### POST `/api/admin/payments/confirm-manual` (Admin)
Ручное подтверждение прямого банковского перевода. Требует `X-Admin-Key`. После проверки платежа поддержка подтверждает платёж, система генерирует код активации.
```json
{
  "paymentId": "pay_123",
  "pspTxnId": "optional_transaction_id"
}
```
Ответ содержит `activationCode` для выдачи пользователю.

## Безопасность

### Защита вебхуков
- Проверка подписи `X-Signature` через HMAC-SHA256 (настраивается через `PAYMENT_WEBHOOK_SECRET`).
- Idempotency: повторные вебхуки с одним `pspTxnId` игнорируются.

### Rate Limiting
- `/api/activation/retrieve`: ограничение 5 запросов в минуту на комбинацию `alias:IP` (настраивается через `PAYMENT_RATE_LIMIT_RETRIEVE_MAX` и `PAYMENT_RATE_LIMIT_RETRIEVE_WINDOW`).
- Заголовки ответа: `X-RateLimit-Remaining`.

## Способы оплаты

### ✅ Оплата на карту через СБП (без договора)
- **Метод**: `manual_transfer`
- **Как работает**: Пользователь выбирает "Оплата на карту через СБП" → видит номер вашей карты → переводит деньги через СБП в приложении банка → поддержка проверяет поступление и подтверждает через `/api/admin/payments/confirm-manual` → система генерирует код активации.
- **Настройка**: Установите переменные окружения `PAYMENT_CARD_NUMBER` и `PAYMENT_CARD_HOLDER_NAME` (см. таблицу выше).
- **Преимущества**: Не требует договора с банком, можно использовать сразу. Мгновенное зачисление через СБП.
- **Недостатки**: Ручная обработка поддержкой (не автоматически).

### 🔄 Автоматические методы (требуют договоры)
- **QR/СБП**: Требует договор с банком или СБП для API доступа.
- **Банковские карты**: Требует договор эквайринга с каждым банком.
- **SberPay/Tinkoff Pay**: Требуют договор с банком для SDK/API.

## TODO (дальше по плану)
- ✅ Защита вебхуков (подписи) и idempotency — реализовано.
- ✅ Rate limiting на `/activation/retrieve` — реализовано.
- ✅ Прямой банковский перевод (без договора) — реализовано.
- Подключить реальные QR/СБП и карточные шлюзы конкретных банков (Сбербанк, Тинькофф, Альфа, ВТБ и т.д.), а также кнопки SberPay/Tinkoff Pay (требуются API ключи и договоры).
- Добавить админ-панель/CLI для поддержки (поиск по alias, статусы).
- Синхронизировать лендинг с `GET /api/payment-methods` (вместо статичных JSON) после деплоя backend.

