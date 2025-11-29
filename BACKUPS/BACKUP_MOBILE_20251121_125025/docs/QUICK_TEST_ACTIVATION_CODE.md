# ⚡ БЫСТРЫЙ ТЕСТ КОДА АКТИВАЦИИ

## ✅ ГОТОВЫЙ ТЕСТОВЫЙ ПЛАТЕЖ

**Payment ID:** `PAY_20251123204343_9411EE3E`  
**Код активации:** `ALDN-D6W9-IUXN-QGJZ`  
**Статус:** ✅ Оплачен  
**Срок действия:** До 23.12.2025

---

## 🚀 БЫСТРЫЙ ТЕСТ (3 ШАГА)

### 1️⃣ Откройте страницу:
```
https://aladdin-ai.ru/success.html?paymentId=PAY_20251123204343_9411EE3E
```

**Что должно произойти:**
- Страница загрузится за 1-2 секунды
- Увидит, что платеж оплачен
- Покажет код: **ALDN-D6W9-IUXN-QGJZ**

---

### 2️⃣ Скопируйте код:
- Нажмите кнопку **"📋 Копировать код"**
- Код скопируется: `ALDN-D6W9-IUXN-QGJZ`

---

### 3️⃣ Активируйте в приложении:
1. Откройте приложение **ALADDIN AI**
2. Перейдите: **"Ввести код активации"**
3. Вставьте код: `ALDN-D6W9-IUXN-QGJZ`
4. Нажмите **"Активировать"**
5. ✅ Подписка активирована!

---

## ⏰ ПОЧЕМУ СТРАНИЦА ДОЛГО ГРУЗИТСЯ?

### Если страница грузится более 3 минут:

**Причина 1: Платеж не подтвержден**
- Статус: `pending`
- Решение: Подтвердить платеж

**Причина 2: Неправильный payment_id**
- Используется `YOUR_PAYMENT_ID` вместо реального
- Решение: Использовать правильный payment_id

**Причина 3: Проблема с CORS**
- Браузер блокирует запросы
- Решение: Проверить настройки CORS на сервере

---

## 🔧 СОЗДАНИЕ НОВОГО ТЕСТОВОГО ПЛАТЕЖА

### Команды (выполнить на сервере):

```bash
# 1. Создать платеж
PAYMENT_ID=$(curl -s -X POST http://localhost:8000/api/payments/create \
  -H "Content-Type: application/json" \
  -d '{
    "tariffId":"family",
    "userAlias":"testuser999",
    "pin":"9999",
    "paymentMethod":"qr_sbp",
    "periodMonths":1,
    "amount":800.0
  }' | python3 -c "import sys, json; print(json.load(sys.stdin)['paymentId'])")

echo "Payment ID: $PAYMENT_ID"

# 2. Подтвердить платеж
curl -X POST "http://localhost:8000/api/payments/confirm?payment_id=$PAYMENT_ID"

# 3. Получить код активации
curl "http://localhost:8000/api/payments/status/$PAYMENT_ID" | python3 -m json.tool

# 4. Открыть страницу
echo "https://aladdin-ai.ru/success.html?paymentId=$PAYMENT_ID"
```

---

## ✅ ПРОВЕРКА ТЕКУЩЕГО ПЛАТЕЖА

**Проверить статус:**
```bash
curl http://149.154.65.180:8000/api/payments/status/PAY_20251123204343_9411EE3E
```

**Ожидаемый ответ:**
```json
{
  "paymentId": "PAY_20251123204343_9411EE3E",
  "status": "paid",
  "activationCode": "ALDN-D6W9-IUXN-QGJZ",
  "codeExpiresAt": "2025-12-23T20:43:58.005387"
}
```

---

## 🎯 ИТОГ

**Для теста используйте:**
- URL: `https://aladdin-ai.ru/success.html?paymentId=PAY_20251123204343_9411EE3E`
- Код: `ALDN-D6W9-IUXN-QGJZ`

**Страница должна загрузиться за 1-2 секунды и показать код!**

Если страница долго грузится - проверьте:
1. Правильный ли payment_id в URL
2. Работает ли backend (порт 8000)
3. Нет ли проблем с CORS

