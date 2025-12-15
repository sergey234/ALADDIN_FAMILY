# 🧪 РУКОВОДСТВО ПО ПОЛНОМУ ТЕСТИРОВАНИЮ: Реферальная программа

**Дата:** 22 ноября 2024  
**Статус:** ✅ Готово к тестированию

---

## 📋 ОБЗОР

Это руководство описывает полное тестирование реферальной программы от начала до конца.

---

## 🎯 ТЕСТОВЫЕ ENDPOINTS

### 1. `/api/referral/test/payment/create`
**Метод:** POST  
**Описание:** Тест создания платежа с referralCode

**Запрос:**
```json
{
  "tariff_id": "premium",
  "period": 1,
  "amount": 800.0,
  "referralCode": "ABC123"
}
```

**Ответ:**
```json
{
  "success": true,
  "user_id": 1,
  "original_amount": 800.0,
  "final_amount": 800.0,
  "referral_id": 1,
  "referral_code": "ABC123",
  "message": "Платеж создан успешно (тест)"
}
```

### 2. `/api/referral/test/payment/confirm`
**Метод:** POST  
**Описание:** Тест подтверждения платежа

**Запрос:**
```json
{
  "payment_id": "test_payment_123",
  "user_id": 101,
  "amount": 800.0
}
```

**Ответ:**
```json
{
  "success": true,
  "payment_id": "test_payment_123",
  "user_id": 101,
  "amount": 800.0,
  "message": "Платеж подтвержден, реферальная программа обработана"
}
```

### 3. `/api/referral/test/discount/apply?original_price=1000.0`
**Метод:** GET  
**Описание:** Тест применения скидки рефереру

**Ответ:**
```json
{
  "success": true,
  "user_id": 1,
  "original_price": 1000.0,
  "final_price": 800.0,
  "discount_applied": 200.0,
  "discount_percent": 20.0,
  "has_active_discount": true
}
```

---

## 🔄 ПОЛНЫЙ ЦИКЛ ТЕСТИРОВАНИЯ

### Шаг 1: Создать тестовых пользователей

```sql
-- Пользователь 1 (реферер)
INSERT INTO users (id, email, password) VALUES (1, 'referrer@test.com', 'password') ON CONFLICT DO NOTHING;

-- Пользователь 2 (приглашенный)
INSERT INTO users (id, email, password) VALUES (101, 'invited@test.com', 'password') ON CONFLICT DO NOTHING;

-- Создать реферальный код для пользователя 1
SELECT get_or_create_referral_code(1);
-- Результат: например "ABC123"
```

### Шаг 2: Создать платеж с referralCode

```bash
# Получить токен для пользователя 101 (приглашенный)
TOKEN_INVITED="Bearer {token_for_user_101}"

# Создать платеж с referralCode
curl -X POST https://aladdin-ai.ru/api/referral/test/payment/create \
  -H "Authorization: $TOKEN_INVITED" \
  -H "Content-Type: application/json" \
  -d '{
    "tariff_id": "premium",
    "period": 1,
    "amount": 800.0,
    "referralCode": "ABC123"
  }'
```

**Ожидаемый результат:**
- Запись в `referrals` создана (status: `pending`)
- `referral_id` возвращен

### Шаг 3: Подтвердить платеж

```bash
curl -X POST https://aladdin-ai.ru/api/referral/test/payment/confirm \
  -H "Authorization: $TOKEN_INVITED" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_id": "test_payment_123",
    "user_id": 101,
    "amount": 800.0
  }'
```

**Ожидаемый результат:**
- Статус referral обновлен на `completed`
- Скидка -20% начислена рефереру (user_id: 1)
- Запись в `referral_discounts` создана

### Шаг 4: Проверить что скидка начислена

```sql
-- Проверить referral
SELECT * FROM referrals WHERE referrer_id = 1 AND invited_user_id = 101;
-- Статус должен быть 'completed'

-- Проверить скидку реферера
SELECT * FROM referral_discounts WHERE user_id = 1;
-- Должна быть активная скидка -20%
```

### Шаг 5: Применить скидку рефереру

```bash
# Получить токен для пользователя 1 (реферер)
TOKEN_REFERRER="Bearer {token_for_user_1}"

# Применить скидку
curl -X GET "https://aladdin-ai.ru/api/referral/test/discount/apply?original_price=1000.0" \
  -H "Authorization: $TOKEN_REFERRER"
```

**Ожидаемый результат:**
- Цена уменьшена с 1000.0 до 800.0
- Скидка применена (-20%)
- Скидка помечена как использованная

---

## ✅ ЧЕКЛИСТ ТЕСТИРОВАНИЯ

### Базовая функциональность
- [ ] Создание платежа с referralCode работает
- [ ] Подтверждение платежа обновляет статус referral
- [ ] Скидка начисляется рефереру
- [ ] Скидка применяется к цене реферера

### Граничные случаи
- [ ] Платеж без referralCode (не должно быть ошибки)
- [ ] Невалидный referralCode (игнорируется)
- [ ] Пользователь использует свой код (игнорируется)
- [ ] Подтверждение без pending referral (возвращает false)

### Интеграция
- [ ] API endpoints работают с авторизацией
- [ ] База данных обновляется корректно
- [ ] Транзакции работают правильно

---

## 🐛 ОТЛАДКА

### Проверка логов

```bash
# На сервере
tail -f /tmp/backend.log
```

### Проверка базы данных

```sql
-- Проверить все referral коды
SELECT * FROM referral_codes;

-- Проверить все referrals
SELECT * FROM referrals ORDER BY created_at DESC;

-- Проверить все скидки
SELECT * FROM referral_discounts ORDER BY created_at DESC;
```

---

## 📊 ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ

### После создания платежа:
- ✅ Запись в `referrals` (status: `pending`)
- ✅ `discount_applied` = 200.0 (20% от 1000.0)

### После подтверждения:
- ✅ Статус обновлен на `completed`
- ✅ `converted_at` установлен
- ✅ `reward_amount` = 200.0
- ✅ Запись в `referral_discounts` (user_id: 1, discount_percent: 20.0)

### После применения скидки:
- ✅ Цена уменьшена на 20%
- ✅ `used_at` установлен в `referral_discounts`

---

**Готово к тестированию!** 🎉


