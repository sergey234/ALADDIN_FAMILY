# 🔧 РУКОВОДСТВО ПО ИНТЕГРАЦИИ: Реферальная программа в платежи

**Дата:** 22 ноября 2024  
**Статус:** ✅ Готово к интеграции

---

## 📋 ОБЗОР

Это руководство описывает как интегрировать реферальную программу в существующий код обработки платежей.

**Где находится код платежей:**
- Основной backend: `api-dev.aladdin.family` или `api.aladdin.family`
- Локальный backend (для тестирования): `149.154.65.180:8000`

---

## 🎯 ЧТО НУЖНО СДЕЛАТЬ

### 1. При создании платежа (`/api/payments/create`)
- ✅ Принять `referralCode` из запроса
- ✅ Создать запись в `referrals` (status: `pending`)
- ✅ Применить скидку -20% к приглашенному пользователю

### 2. При подтверждении оплаты (`/api/payments/status` или webhook)
- ✅ Обновить статус referral на `completed`
- ✅ Начислить скидку -20% рефереру на следующий месяц

### 3. При создании платежа для реферера
- ✅ Проверить наличие активной скидки
- ✅ Применить скидку -20% к цене

---

## 📁 ФАЙЛЫ ДЛЯ ИНТЕГРАЦИИ

### 1. `referral_payment_functions.py`
Готовые функции для интеграции:
- `process_referral_code_on_payment()` - обработка кода при создании платежа
- `process_referral_on_payment_confirmation()` - обработка при подтверждении
- `apply_referral_discount()` - применение скидки рефереру

**Расположение:** `docs/server/referral_payment_functions.py`

---

## 🔧 ШАГ 1: ИНТЕГРАЦИЯ В СОЗДАНИЕ ПЛАТЕЖА

### Найти файл обработки платежей

Обычно это:
- `app/routers/payments.py`
- `app/api/payments.py`
- `routes/payment.py`

### Добавить обработку referralCode

```python
from app.referral_payment_functions import process_referral_code_on_payment, apply_referral_discount

@router.post("/api/payments/create")
async def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # ... существующая логика расчета цены ...
    calculated_price = calculate_price(payment_data.tariff_id, payment_data.period)
    
    # ✅ ДОБАВИТЬ: Применить скидку рефереру (если есть активная скидка)
    final_price = apply_referral_discount(db, current_user["id"], calculated_price)
    
    # ✅ ДОБАВИТЬ: Обработка реферального кода (если приглашенный пользователь)
    referral_id = None
    if payment_data.referralCode:
        referral_id = process_referral_code_on_payment(
            db, 
            payment_data.referralCode, 
            current_user["id"], 
            final_price
        )
        # Если код применен, скидка -20% уже учтена в final_price
        # (скидка применяется на клиенте в index.html)
    
    # ... существующая логика создания платежа ...
    payment = create_payment_record(db, {
        "user_id": current_user["id"],
        "amount": final_price,
        "tariff_id": payment_data.tariff_id,
        "referral_id": referral_id  # Сохранить для связи
    })
    
    return {"paymentId": payment.id, "amount": final_price, ...}
```

### Обновить модель PaymentCreate

```python
from pydantic import BaseModel

class PaymentCreate(BaseModel):
    tariff_id: str
    period: int  # месяцев
    referralCode: Optional[str] = None  # ✅ ДОБАВИТЬ это поле
    # ... другие поля ...
```

---

## 🔧 ШАГ 2: ИНТЕГРАЦИЯ В ПОДТВЕРЖДЕНИЕ ОПЛАТЫ

### Найти обработчик подтверждения платежа

Обычно это:
- `@router.post("/api/payments/confirm")`
- `@router.get("/api/payments/status/{payment_id}")`
- Webhook от платежной системы

### Добавить обработку реферальной программы

```python
from app.referral_payment_functions import process_referral_on_payment_confirmation

@router.post("/api/payments/confirm")
async def confirm_payment(
    payment_id: str,
    db: Session = Depends(get_db)
):
    # ... существующая логика получения платежа ...
    payment = get_payment(payment_id, db)
    
    if payment.status == 'paid' or payment.status == 'completed':
        # ✅ ДОБАВИТЬ: Обработка реферальной программы
        process_referral_on_payment_confirmation(
            db, 
            payment.user_id, 
            payment.amount
        )
        
        # ... остальная логика ...
    
    return {"status": payment.status, ...}
```

---

## 🔧 ШАГ 3: КОПИРОВАНИЕ ФАЙЛА НА СЕРВЕР

### Вариант 1: Если код платежей на 149.154.65.180

```bash
# Скопировать функции
scp docs/server/referral_payment_functions.py root@149.154.65.180:/opt/aladdin-backend/app/referral_payment_functions.py

# Или создать модуль
mkdir -p /opt/aladdin-backend/app/referral
scp docs/server/referral_payment_functions.py root@149.154.65.180:/opt/aladdin-backend/app/referral/payment_functions.py
```

### Вариант 2: Если код платежей на api-dev.aladdin.family

Нужно скопировать файл на тот сервер (требуется доступ).

---

## ✅ ПРОВЕРКА ИНТЕГРАЦИИ

### Тест 1: Создание платежа с referralCode

```bash
curl -X POST https://api.aladdin.family/api/payments/create \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "tariff_id": "premium",
    "period": 1,
    "referralCode": "ABC123"
  }'
```

**Ожидаемый результат:**
- Платеж создан
- Запись в `referrals` создана (status: `pending`)
- Скидка -20% применена к цене

### Тест 2: Подтверждение оплаты

```bash
curl -X POST https://api.aladdin.family/api/payments/confirm \
  -H "Authorization: Bearer {token}" \
  -d '{"payment_id": "payment_123"}'
```

**Ожидаемый результат:**
- Статус referral обновлен на `completed`
- Скидка -20% начислена рефереру на следующий месяц
- Запись в `referral_discounts` создана

### Тест 3: Оплата реферера со скидкой

```bash
curl -X POST https://api.aladdin.family/api/payments/create \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "tariff_id": "premium",
    "period": 1
  }'
```

**Ожидаемый результат:**
- Если у реферера есть активная скидка, она применена
- Цена уменьшена на 20%
- Скидка помечена как использованная

---

## 📊 СХЕМА РАБОТЫ

```
1. Приглашенный пользователь создает платеж:
   ├─ referralCode передается в запросе
   ├─ process_referral_code_on_payment() создает запись (status: pending)
   └─ Скидка -20% уже применена на клиенте (index.html)

2. Платеж подтвержден:
   ├─ process_referral_on_payment_confirmation() вызывается
   ├─ Статус обновлен на completed
   └─ Скидка -20% начислена рефереру на следующий месяц

3. Реферер создает платеж (следующий месяц):
   ├─ apply_referral_discount() проверяет активную скидку
   ├─ Скидка -20% применена к цене
   └─ Скидка помечена как использованная
```

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **Скидка для приглашенного:**
   - Применяется на клиенте (в `index.html`)
   - Сервер получает уже уменьшенную цену
   - Не нужно применять скидку на сервере для приглашенного

2. **Скидка для реферера:**
   - Применяется на сервере при создании платежа
   - Используется функция `apply_referral_discount()`

3. **Обработка ошибок:**
   - Все функции возвращают безопасные значения при ошибках
   - Ошибки логируются, но не прерывают процесс оплаты

4. **Транзакции:**
   - Все операции выполняются в транзакциях
   - При ошибке выполняется rollback

---

## 🚀 БЫСТРЫЙ СТАРТ

1. Скопировать `referral_payment_functions.py` в проект
2. Импортировать функции в файл обработки платежей
3. Добавить вызовы функций в нужных местах
4. Обновить модель `PaymentCreate` (добавить `referralCode`)
5. Протестировать

---

**Готово к интеграции!** 🎉

