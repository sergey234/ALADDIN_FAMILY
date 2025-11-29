# 🔍 РУКОВОДСТВО ПО ТЕСТИРОВАНИЮ BACKEND ДЛЯ QR КОДА

## 📋 ОБЩАЯ ИНФОРМАЦИЯ

**Endpoint для создания QR платежа:**
- **URL:** `POST /api/payments/qr/create`
- **Base URL:** `https://api.aladdin.family/api` (или ваш URL)
- **Полный URL:** `https://api.aladdin.family/api/api/payments/qr/create`

**Примечание:** Обратите внимание на двойной `/api/api/` - это из-за того что `apiBaseURL` уже содержит `/api`, а endpoint начинается с `/api/`.

---

## 📤 ЗАПРОС (Request)

### Структура данных (iOS Swift):

```swift
struct CreateQRPaymentRequest: Codable {
    let amount: Double        // Сумма платежа (например: 590.0)
    let currency: String      // Валюта (например: "RUB")
    let description: String   // Описание (например: "СЕМЕЙНЫЙ")
    let tariffId: String?     // ID тарифа (опционально, может быть nil)
}
```

### Пример запроса из iOS:

```swift
// Когда пользователь выбирает тариф "Семейный" (590 ₽)
let request = CreateQRPaymentRequest(
    amount: 590.0,
    currency: "RUB",
    description: "СЕМЕЙНЫЙ",
    tariffId: "family"  // или nil
)
```

### JSON формат (что отправляется на сервер):

```json
{
    "amount": 590.0,
    "currency": "RUB",
    "description": "СЕМЕЙНЫЙ",
    "tariffId": "family"
}
```

Или если `tariffId` отсутствует:
```json
{
    "amount": 590.0,
    "currency": "RUB",
    "description": "СЕМЕЙНЫЙ",
    "tariffId": null
}
```

### HTTP Headers:

```
Content-Type: application/json
```

**Примечание:** iOS также может отправлять:
- Authorization token (если пользователь авторизован)
- User-Agent
- Другие стандартные заголовки

---

## 📥 ОТВЕТ (Response)

### Ожидаемая структура ответа от backend:

```swift
struct CreateQRPaymentResponse: Codable {
    let paymentId: String     // Уникальный ID платежа (обязательно, не пустой)
    let qrCode: String        // QR код (URL или base64) (обязательно, не пустой)
    let amount: Double        // Сумма платежа
    let currency: String      // Валюта
    let expiresAt: Date       // Дата истечения платежа (ISO 8601 формат)
    let status: String        // Статус платежа (обычно "pending")
}
```

### Пример успешного ответа:

```json
{
    "paymentId": "pay_abc123xyz",
    "qrCode": "https://qr.sbp.ru/payment?token=abc123xyz",
    "amount": 590.0,
    "currency": "RUB",
    "expiresAt": "2024-01-20T15:30:00Z",
    "status": "pending"
}
```

Или если QR код в формате base64:

```json
{
    "paymentId": "pay_abc123xyz",
    "qrCode": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "amount": 590.0,
    "currency": "RUB",
    "expiresAt": "2024-01-20T15:30:00Z",
    "status": "pending"
}
```

### Формат даты expiresAt:

iOS ожидает дату в формате **ISO 8601**:
- `"2024-01-20T15:30:00Z"` - UTC время
- `"2024-01-20T15:30:00+03:00"` - с timezone

**Важно:** Swift `Date` автоматически парсит ISO 8601 формат.

---

## 🧪 СПОСОБЫ ТЕСТИРОВАНИЯ НА BACKEND

### Способ 1: Использование curl (в терминале)

```bash
curl -X POST "https://api.aladdin.family/api/api/payments/qr/create" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 590.0,
    "currency": "RUB",
    "description": "СЕМЕЙНЫЙ",
    "tariffId": "family"
  }'
```

**Для localhost (если backend запущен локально):**

```bash
curl -X POST "http://localhost:8000/api/payments/qr/create" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 590.0,
    "currency": "RUB",
    "description": "СЕМЕЙНЫЙ",
    "tariffId": "family"
  }'
```

**Ожидаемый ответ:**
```json
{
    "paymentId": "pay_...",
    "qrCode": "https://...",
    "amount": 590.0,
    "currency": "RUB",
    "expiresAt": "2024-01-20T15:30:00Z",
    "status": "pending"
}
```

---

### Способ 2: Python скрипт для тестирования

Создайте файл `test_qr_payment.py`:

```python
import requests
import json
from datetime import datetime, timedelta

# Конфигурация
BASE_URL = "https://api.aladdin.family/api"  # Замените на ваш URL
ENDPOINT = "/api/payments/qr/create"
FULL_URL = f"{BASE_URL}{ENDPOINT}"

# Данные запроса (как в iOS)
request_data = {
    "amount": 590.0,
    "currency": "RUB",
    "description": "СЕМЕЙНЫЙ",
    "tariffId": "family"
}

print(f"🔍 Тестирование создания QR платежа")
print(f"   URL: {FULL_URL}")
print(f"   Request: {json.dumps(request_data, indent=2)}")
print()

try:
    # Отправляем запрос
    response = requests.post(
        FULL_URL,
        json=request_data,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"📥 Status Code: {response.status_code}")
    print(f"📥 Headers: {dict(response.headers)}")
    print()
    
    if response.status_code == 200:
        # Успешный ответ
        data = response.json()
        print("✅ УСПЕШНЫЙ ОТВЕТ:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print()
        
        # Проверка обязательных полей
        required_fields = ["paymentId", "qrCode", "amount", "currency", "expiresAt", "status"]
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print(f"⚠️ ОТСУТСТВУЮТ ПОЛЯ: {missing_fields}")
        else:
            print("✅ Все обязательные поля присутствуют")
        
        # Проверка что qrCode не пустой
        if not data.get("qrCode") or len(data["qrCode"]) == 0:
            print("❌ ОШИБКА: qrCode пустой!")
        else:
            print(f"✅ qrCode получен (длина: {len(data['qrCode'])} символов)")
            if data["qrCode"].startswith("http"):
                print(f"   Тип: URL")
                print(f"   Значение: {data['qrCode'][:100]}...")
            elif data["qrCode"].startswith("data:image/"):
                print(f"   Тип: Base64 image")
                print(f"   Первые 100 символов: {data['qrCode'][:100]}...")
            else:
                print(f"   Тип: Неизвестный формат")
                print(f"   Первые 100 символов: {data['qrCode'][:100]}...")
        
        # Проверка что paymentId не пустой
        if not data.get("paymentId") or len(data["paymentId"]) == 0:
            print("❌ ОШИБКА: paymentId пустой!")
        else:
            print(f"✅ paymentId получен: {data['paymentId']}")
            
    else:
        # Ошибка
        print(f"❌ ОШИБКА:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"❌ ОШИБКА ЗАПРОСА: {e}")
except json.JSONDecodeError as e:
    print(f"❌ ОШИБКА ПАРСИНГА JSON: {e}")
    print(f"   Response text: {response.text[:500]}")
except Exception as e:
    print(f"❌ НЕИЗВЕСТНАЯ ОШИБКА: {e}")
```

**Запуск:**
```bash
python3 test_qr_payment.py
```

---

### Способ 3: Использование Postman

1. **Создайте новый POST запрос:**
   - URL: `https://api.aladdin.family/api/api/payments/qr/create`

2. **Вкладка Headers:**
   - `Content-Type: application/json`

3. **Вкладка Body (выберите raw JSON):**
   ```json
   {
       "amount": 590.0,
       "currency": "RUB",
       "description": "СЕМЕЙНЫЙ",
       "tariffId": "family"
   }
   ```

4. **Нажмите Send**

5. **Проверьте ответ:**
   - Должен быть статус 200 OK
   - В ответе должны быть поля: `paymentId`, `qrCode`, `amount`, `currency`, `expiresAt`, `status`
   - `qrCode` не должен быть пустым

---

### Способ 4: Проверка логов на сервере

**Что проверить в логах backend:**

1. **Лог входящего запроса:**
   ```
   POST /api/payments/qr/create
   Body: {"amount": 590.0, "currency": "RUB", ...}
   ```

2. **Лог создания платежа:**
   ```
   Creating payment: amount=590.0, currency=RUB, tariffId=family
   Generated paymentId: pay_abc123xyz
   ```

3. **Лог генерации QR кода:**
   ```
   Generating QR code for payment: pay_abc123xyz
   QR code generated: https://... или data:image/...
   ```

4. **Лог отправки ответа:**
   ```
   Sending response: paymentId=pay_abc123xyz, qrCode length=500
   ```

**Если в логах нет запросов:**
- iOS запрос не доходит до сервера
- Проблема с URL или сетью
- Проверить что сервер доступен

**Если запрос есть, но ответ неправильный:**
- Проверить логику генерации QR кода на backend
- Проверить что все поля заполняются
- Проверить формат даты `expiresAt`

---

## 🔍 ЧТО ПРОВЕРИТЬ НА BACKEND

### 1. Эндпоинт должен принимать POST запрос

**Проверка:**
```python
# Пример для Python Flask/FastAPI
@app.post("/api/payments/qr/create")
async def create_qr_payment(request: CreateQRPaymentRequest):
    # Обработка запроса
    pass
```

### 2. Эндпоинт должен валидировать входные данные

**Проверка:**
- `amount` > 0
- `currency` не пустой
- `description` не пустой (можно опционально)
- `tariffId` может быть None/null

### 3. Backend должен генерировать paymentId

**Что должно быть:**
- Уникальный ID для каждого платежа
- Формат может быть любой (например: `pay_abc123`, `payment-123`, UUID и т.д.)
- Должен сохраняться в базе данных для последующей проверки статуса

### 4. Backend должен генерировать QR код

**Процесс генерации:**
1. Создать платеж в платежной системе (СБП, банк)
2. Получить от платежной системы QR код
3. QR код может быть:
   - **URL** (например: `https://qr.sbp.ru/payment?token=...`)
   - **Base64 изображение** (например: `data:image/png;base64,iVBORw0KG...`)

**Важно:** QR код НЕ должен быть пустым! iOS проверяет это и покажет ошибку если пустой.

### 5. Backend должен возвращать правильный формат даты

**Формат:** ISO 8601
- `"2024-01-20T15:30:00Z"` - UTC
- `"2024-01-20T15:30:00+03:00"` - с timezone

**Проверка в Python:**
```python
from datetime import datetime
expires_at = datetime.now() + timedelta(hours=1)
expires_at.isoformat() + "Z"  # "2024-01-20T15:30:00Z"
```

### 6. Backend должен возвращать все обязательные поля

**Обязательные поля в ответе:**
- `paymentId` (String, не пустой)
- `qrCode` (String, не пустой)
- `amount` (Double)
- `currency` (String)
- `expiresAt` (Date/ISO 8601 string)
- `status` (String, обычно "pending")

---

## 🐛 ЧАСТЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ

### Проблема 1: "404 Not Found"

**Причина:** Неправильный URL endpoint

**Решение:**
- Проверить что endpoint: `/api/payments/qr/create`
- Проверить что base URL правильный
- Проверить что нет двойного `/api/api/` в URL

### Проблема 2: "400 Bad Request"

**Причина:** Неправильный формат запроса

**Решение:**
- Проверить что все поля отправляются
- Проверить типы данных (amount должен быть Double, не String)
- Проверить что JSON валидный

### Проблема 3: "500 Internal Server Error"

**Причина:** Ошибка на сервере при генерации QR кода

**Решение:**
- Проверить логи сервера
- Проверить подключение к платежной системе
- Проверить что все сервисы запущены

### Проблема 4: QR код пустой в ответе

**Причина:** Backend не генерирует QR код или возвращает пустую строку

**Решение:**
- Проверить логи генерации QR кода
- Проверить подключение к платежной системе (СБП API)
- Убедиться что QR код создается до отправки ответа

### Проблема 5: paymentId пустой в ответе

**Причина:** Backend не создает paymentId

**Решение:**
- Проверить логи создания платежа
- Убедиться что paymentId генерируется
- Проверить что paymentId сохраняется в базе данных

---

## 📝 ПРИМЕР ТЕСТОВОГО ЗАПРОСА

### Вариант 1: Тариф "Семейный" (590 ₽)

```json
{
    "amount": 590.0,
    "currency": "RUB",
    "description": "СЕМЕЙНЫЙ",
    "tariffId": "family"
}
```

### Вариант 2: Тариф "Личный" (290 ₽)

```json
{
    "amount": 290.0,
    "currency": "RUB",
    "description": "ЛИЧНЫЙ",
    "tariffId": "personal"
}
```

### Вариант 3: Без tariffId

```json
{
    "amount": 100.0,
    "currency": "RUB",
    "description": "Тестовый платеж"
}
```

---

## 🔗 ПРОВЕРКА СТАТУСА ПЛАТЕЖА

После создания платежа, можно проверить его статус:

**Endpoint:** `GET /api/payments/qr/status/{paymentId}`

**Пример:**
```bash
curl "https://api.aladdin.family/api/api/payments/qr/status/pay_abc123xyz"
```

**Ожидаемый ответ:**
```json
{
    "paymentId": "pay_abc123xyz",
    "status": "pending",  // или "completed", "expired", "cancelled"
    "amount": 590.0,
    "currency": "RUB",
    "completedAt": null  // или дата если completed
}
```

---

## ✅ ЧЕКЛИСТ ДЛЯ ПРОВЕРКИ BACKEND

- [ ] Эндпоинт `/api/payments/qr/create` существует и работает
- [ ] Принимает POST запрос с JSON body
- [ ] Валидирует входные данные (amount > 0, currency не пустой)
- [ ] Создает платеж в платежной системе
- [ ] Генерирует уникальный `paymentId`
- [ ] Генерирует QR код (не пустой!)
- [ ] Возвращает все обязательные поля в ответе
- [ ] `expiresAt` в правильном формате (ISO 8601)
- [ ] Логирует все этапы для отладки
- [ ] Обрабатывает ошибки и возвращает понятные сообщения

---

## 📊 МОНИТОРИНГ И ЛОГИРОВАНИЕ

### Рекомендуемые логи на backend:

```python
logger.info(f"Received QR payment request: amount={request.amount}, currency={request.currency}, tariffId={request.tariffId}")

# После создания платежа
logger.info(f"Created payment: paymentId={payment_id}")

# После генерации QR кода
logger.info(f"Generated QR code: paymentId={payment_id}, qrCode_length={len(qr_code)}")

# Перед отправкой ответа
logger.info(f"Sending response: paymentId={payment_id}, qrCode_length={len(qr_code)}, expiresAt={expires_at}")
```

---

## 🎯 ИТОГОВАЯ ИНСТРУКЦИЯ

**Для проверки на backend сервере:**

1. **Запустите тестовый запрос** (curl, Python, Postman)
2. **Проверьте логи сервера** - должны быть все этапы
3. **Проверьте ответ** - должен содержать все поля
4. **Проверьте что qrCode не пустой**
5. **Проверьте что paymentId не пустой**
6. **Проверьте формат даты expiresAt**

**Если все правильно:**
- iOS должно получить ответ
- QR код должен появиться на экране
- paymentId должен сохраниться
- Кнопка "Проверить статус" должна стать активной

**Если что-то не так:**
- Проверьте логи backend
- Проверьте подключение к платежной системе
- Проверьте формат ответа
- Убедитесь что все поля заполняются правильно

