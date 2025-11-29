# 🔄 Алгоритм получения кода активации после оплаты

**Дата:** 17 ноября 2025  
**Статус:** ✅ Реализовано

---

## 📋 Общая схема

```
1. Пользователь заполняет форму на лендинге (alias + PIN + тариф)
   ↓
2. POST /api/payments/create → создаётся запись Payment (status=created)
   ↓
3. Пользователь переходит на страницу оплаты банка (redirectUrl)
   ↓
4. Пользователь оплачивает на стороне банка
   ↓
5. Банк отправляет webhook POST /api/payments/confirm
   ↓
6. Backend генерирует код активации (ALDN-XXXX-XXXX-XXXX)
   ↓
7. Банк редиректит пользователя на success.html?paymentId=xxx
   ↓
8. Страница success.html проверяет статус через GET /api/payments/status/:paymentId
   ↓
9. Если код готов → показываем код пользователю
   Если код ещё не готов → polling каждые 3 секунды
```

---

## 🔧 Технические детали

### 1. Генерация кода активации

**Файл:** `payment_service/app/utils.py`

```python
def generate_activation_code() -> str:
    alphabet = string.ascii_uppercase + string.digits
    body = "-".join(
        "".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(3)
    )
    return f"ALDN-{body}"
```

**Формат:** `ALDN-XXXX-XXXX-XXXX` (например: `ALDN-8K3Q-2PS5-9LM4`)

**Когда генерируется:**
- В webhook `/api/payments/confirm` при `status=paid`
- Код сохраняется в таблицу `activation_codes` со статусом `active`
- Срок действия: 30 дней

---

### 2. Webhook обработка

**Файл:** `payment_service/main.py` → `confirm_payment()`

**Алгоритм:**
1. Проверка подписи webhook (HMAC-SHA256)
2. Проверка idempotency (по `pspTxnId`)
3. Если `status=paid` и код ещё не создан:
   - Генерируем код через `generate_activation_code()`
   - Создаём запись в `activation_codes`
   - Статус кода: `active`
4. Обновляем статус платежа: `payment.status = "paid"`

---

### 3. Отображение кода пользователю

**Файл:** `landing/success.html`

**Сценарии:**

#### Сценарий A: Есть `paymentId` в URL
- Страница автоматически проверяет статус через `GET /api/payments/status/:paymentId`
- Если код готов → показываем код
- Если код ещё не готов → показываем "Ожидаем подтверждение" + polling каждые 3 секунды

#### Сценарий B: Нет `paymentId`, но есть `alias` и `pin` в URL
- Сразу вызываем `POST /api/activation/retrieve` с alias+PIN
- Показываем код, если он найден

#### Сценарий C: Нет параметров
- Показываем форму для ввода alias+PIN
- После ввода → вызываем `POST /api/activation/retrieve`

---

### 4. API Endpoints

#### `GET /api/payments/status/:paymentId`
**Назначение:** Проверить статус платежа и получить код активации (если готов)

**Ответ:**
```json
{
  "paymentId": "pay_123",
  "status": "paid",
  "amount": 49000,
  "tariffId": "family",
  "activationCode": "ALDN-8K3Q-2PS5-9LM4",  // если код готов
  "codeStatus": "active",
  "codeExpiresAt": "2026-01-01T00:00:00Z"
}
```

#### `POST /api/activation/retrieve`
**Назначение:** Получить код активации по alias+PIN (восстановление)

**Запрос:**
```json
{
  "userAlias": "familySmith",
  "pin": "1234"
}
```

**Ответ:**
```json
{
  "activationCode": "ALDN-8K3Q-2PS5-9LM4",
  "status": "active",
  "expiresAt": "2026-01-01T00:00:00Z"
}
```

**Защита:** Rate limiting (5 запросов/минуту на комбинацию `alias:IP`)

---

## 🔐 Безопасность

1. **PIN хэшируется** через `bcrypt` перед сохранением
2. **Webhook подписи** проверяются через HMAC-SHA256
3. **Idempotency** для webhook (повторные запросы игнорируются)
4. **Rate limiting** на `/activation/retrieve` (защита от брутфорса)
5. **Код активации** генерируется криптографически стойким способом (`secrets.choice`)

---

## 📱 Интеграция с iOS приложением

После получения кода на странице `success.html`:

1. Пользователь копирует код (кнопка "📋 Копировать код")
2. Нажимает "📱 Открыть приложение" → открывается `aladdinaf://activate?code=ALDN-XXXX-XXXX-XXXX`
3. В приложении:
   - Вызывается `POST /api/activation/verify` (проверка кода)
   - Вызывается `POST /api/activation/activate` (активация с `familyId` и `deviceId`)
   - Код помечается как `redeemed` в базе

---

## ⚠️ Важные моменты

### Настройка банков

**Критично:** При настройке банковских интеграций нужно указать **success_url** в кабинете банка:

```
https://aladdin.family/success.html?paymentId={paymentId}
```

Банк должен редиректить пользователя на этот URL после успешной оплаты.

### Для ручного перевода (`manual_transfer`)

- Платёж создаётся со статусом `awaiting_manual_payment`
- Пользователь сразу редиректится на `success.html?paymentId=xxx`
- Код генерируется только после ручного подтверждения через админ-панель:
  - `POST /api/admin/confirm-manual-payment` (требует `X-Admin-Key`)

---

## ✅ Что реализовано

- ✅ Генерация кода активации (`ALDN-XXXX-XXXX-XXXX`)
- ✅ Webhook обработка с генерацией кода
- ✅ Endpoint `/api/payments/status/:paymentId`
- ✅ Страница `success.html` с автоматическим polling
- ✅ Форма восстановления кода по alias+PIN
- ✅ Копирование кода в буфер обмена
- ✅ Кнопка открытия приложения с кодом
- ✅ Rate limiting на `/activation/retrieve`
- ✅ Защита webhook подписями

---

## 🔄 Что осталось

- ⏳ Подключить реальные банковские интеграции (требуются API ключи)
- ⏳ Настроить success_url в кабинетах банков
- ⏳ Протестировать end-to-end с реальными платежами
- ⏳ Добавить админ-панель для ручного подтверждения переводов

---

## 📝 Примеры использования

### Тестовая проверка статуса

```bash
curl -X GET "http://localhost:8000/api/payments/status/pay_123" \
  -H "X-API-Key: PUBLIC_CLIENT_KEY"
```

### Восстановление кода

```bash
curl -X POST "http://localhost:8000/api/activation/retrieve" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: PUBLIC_CLIENT_KEY" \
  -d '{"userAlias": "familySmith", "pin": "1234"}'
```

---

**Последнее обновление:** 17 ноября 2025



