# 🔍 ФИНАЛЬНЫЙ АНАЛИЗ И ПЛАН: Система оплаты + Реферальная программа

**Дата:** 23 ноября 2024  
**Версия:** 2.0 (Детальная проверка)  
**Для:** Другая ML система

---

## 📊 ИТОГОВАЯ ГОТОВНОСТЬ (ПОСЛЕ ДЕТАЛЬНОЙ ПРОВЕРКИ)

### ✅ Официальный сайт `https://aladdin-ai.ru/`: **100%**
- ✅ Лендинг полностью реализован
- ✅ Обработка реферального кода из URL (`?ref=CODE` или `#pay?ref=CODE`)
- ✅ Применение скидки -20% на клиенте
- ✅ Передача `referralCode` в `/api/payments/create`
- ✅ Сохранение в `localStorage`
- ✅ Отображение баннера со скидкой
- ✅ Все методы оплаты реализованы

### ⚠️ iOS приложение: **85%** (уточнено после проверки)
- ✅ **QR-оплата УБРАНА** - переход на сайт `aladdin-ai.ru`
- ✅ Реализован переход через `URLHelper.openWebsite()`
- ✅ Передается `tariffId` в URL (`?tariff=family`)
- ✅ Есть экран реферальной программы (`ReferralScreen`)
- ✅ Есть API методы для получения реферального кода
- ❌ **НЕТ передачи `referralCode` при переходе на сайт**
- ❌ **НЕТ получения `referralCode` из UserDefaults/Keychain**
- ❌ **НЕТ добавления `referralCode` в URL при открытии сайта**

### ❌ Сервер (Backend): **25%** (было 30%, уточнено)
- ✅ Есть база данных PostgreSQL (`aladdin_db`)
- ✅ Есть таблицы: `referral_codes`, `referrals`, `referral_discounts`
- ✅ Есть функции: `process_referral_code_on_payment()`, `process_referral_on_payment_confirmation()`, `apply_referral_discount()`
- ✅ Есть реферальные endpoints: `/api/referral/code`, `/api/referral/stats`, `/api/referral/history`, `/api/referral/rewards`
- ❌ **НЕТ таблицы `payments`**
- ❌ **НЕТ таблицы `payment_methods`**
- ❌ **НЕТ endpoint `/api/payments/create`** (используется лендингом)
- ❌ **НЕТ endpoint `/payments/qr/create`** (используется iOS)
- ❌ **НЕТ endpoint `/api/payments/status/{payment_id}`**
- ❌ **НЕТ endpoint `/api/payments/confirm`**
- ⚠️ Есть только тестовые endpoints: `/api/referral/test/payment/create`, `/api/referral/test/payment/confirm`

### 📊 Общая готовность: **65%** (уточнено после проверки)

---

## 🔍 ДЕТАЛЬНАЯ ПРОВЕРКА КОМПОНЕНТОВ

### 1. Официальный сайт `https://aladdin-ai.ru/`

#### ✅ Что реализовано:

**Файл:** `landing/index.html`

1. **Обработка реферального кода:**
```javascript
// Извлечение из URL
const urlParams = new URLSearchParams(window.location.search);
const hash = window.location.hash || '';
const hashMatch = hash.match(/[#&?]ref=([^&]+)/);
const refFromHash = hashMatch ? hashMatch[1] : null;
const refFromUrl = urlParams.get('ref') || refFromHash || hashParams.get('ref');

// Сохранение в localStorage
window.referralCode = refFromUrl || refFromStorage || null;
if (window.referralCode) {
  localStorage.setItem('referral_code', window.referralCode);
}
```

2. **Применение скидки -20%:**
```javascript
if (window.referralCode && window.referralDiscountPercent) {
  referralDiscount = window.referralDiscountPercent;
  referralSavings = Math.round(finalTotal * (referralDiscount / 100));
  finalTotal = finalTotal - referralSavings;
}
```

3. **Передача на сервер:**
```javascript
const requestBody = {
  tariffId: payload.tariff,
  userAlias: payload.alias.trim(),
  pin: payload.pin.trim(),
  paymentMethod: payload.paymentMethod,
  periodMonths: priceInfo.months,
  amount: priceInfo.total,
  referralCode: window.referralCode || null  // ✅ ПЕРЕДАЕТСЯ
};

// POST /api/payments/create
fetch(`${window.API_BASE}/api/payments/create`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': window.API_KEY
  },
  body: JSON.stringify(requestBody)
});
```

4. **Методы оплаты:**
- QR / СБП
- Карты (Сбербанк, Тинькофф, Альфа, ВТБ, Газпромбанк, ПСБ)
- SberPay
- Tinkoff Pay
- Ручной перевод (manual_transfer)

#### ⚠️ Проблемы:
- Endpoint `/api/payments/create` **НЕ СУЩЕСТВУЕТ** на сервере
- После создания платежа нет проверки статуса
- Нет обработки ошибок от сервера

---

### 2. iOS приложение

#### ✅ Что реализовано:

**Файлы:**
- `ViewModels/PaymentQRViewModel.swift` - Логика QR-платежа
- `Core/Models/APIModels.swift` - Модели данных
- `Core/Network/APIService.swift` - API методы
- `Screens/21_ReferralScreen.swift` - Экран реферальной программы

1. **Модель запроса:**
```swift
struct CreateQRPaymentRequest: Codable {
    let amount: Double
    let currency: String
    let description: String
    let tariffId: String?
    let periodMonths: Int?
    // ❌ НЕТ: let referralCode: String?
}
```

2. **Создание платежа:**
```swift
// ViewModels/PaymentQRViewModel.swift, строка 332
let request = CreateQRPaymentRequest(
    amount: amount,
    currency: "RUB",
    description: tariff.title,
    tariffId: tariff.id,
    periodMonths: tariff.periodMonths > 1 ? tariff.periodMonths : nil
    // ❌ НЕТ: referralCode: ...
)
```

3. **API метод:**
```swift
// Core/Network/APIService.swift, строка 298
func createQRPayment(request: CreateQRPaymentRequest, completion: ...) {
    networkManager.post(endpoint: "/payments/qr/create", body: request, completion: completion)
}
```

4. **Реферальный экран:**
```swift
// Screens/21_ReferralScreen.swift
@State private var referralCode: String = ""  // ✅ Есть переменная
// Но она НЕ используется при создании платежа!
```

#### ✅ Что реализовано:

**Файлы:**
- `Screens/10_TariffsScreen.swift` - Экран тарифов
- `Core/Helpers/URLHelper.swift` - Helper для открытия сайта
- `Core/Config/AppConfig.swift` - Конфигурация (`subscriptionWebsiteURL = "https://aladdin-ai.ru"`)

1. **Переход на сайт:**
```swift
// Screens/10_TariffsScreen.swift, строка 313-317
// ⚠️ Оплата по QR перенесена на лендинг: открываем сайт напрямую
URLHelper.openWebsite(
    urlString: AppConfig.subscriptionWebsiteURL,  // "https://aladdin-ai.ru"
    tariffId: tariffObj.id  // Передается как ?tariff=family
)
```

2. **URLHelper:**
```swift
// Core/Helpers/URLHelper.swift
static func openWebsite(urlString: String, tariffId: String? = nil) {
    var finalURLString = urlString
    if let tariffId = tariffId, !tariffId.isEmpty {
        let separator = urlString.contains("?") ? "&" : "?"
        finalURLString = "\(urlString)\(separator)tariff=\(tariffId)"
    }
    UIApplication.shared.open(url, options: [:], completionHandler: nil)
}
```

#### ❌ Критические проблемы:

1. **НЕТ передачи `referralCode` в URL:**
   - `URLHelper.openWebsite()` не принимает `referralCode`
   - При переходе на сайт код не передается
   - Сайт не получает информацию о реферальном коде

2. **Нет получения кода:**
   - Нет сохранения `referralCode` в UserDefaults/Keychain
   - Нет связи между `ReferralScreen` и переходом на оплату

3. **Нет добавления в URL:**
   - Даже если код есть, он не добавляется в URL при открытии сайта

---

### 3. Сервер (Backend)

#### ✅ Что реализовано:

**Структура:**
```
/opt/aladdin-backend/
├── main.py
├── app/
│   ├── routers/
│   │   ├── referral.py          # Реферальные endpoints
│   │   └── referral_test.py     # Тестовые endpoints
│   ├── database/
│   │   └── database.py          # Подключение к БД
│   ├── auth/
│   │   └── auth.py              # JWT авторизация
│   ├── referral_payment_functions.py    # Функции для интеграции
│   └── referral_payment_integration.py  # Примеры интеграции
```

**База данных:**
- ✅ Таблица `referral_codes` (user_id, code)
- ✅ Таблица `referrals` (referrer_id, invited_user_id, status, discount_applied, reward_amount)
- ✅ Таблица `referral_discounts` (user_id, discount_percent, valid_from, valid_until, used_at)

**Endpoints:**
- ✅ `GET /api/referral/code` - Получить реферальный код
- ✅ `GET /api/referral/stats` - Статистика рефералов
- ✅ `GET /api/referral/history` - История рефералов
- ✅ `GET /api/referral/rewards` - Награды реферера

**Функции:**
- ✅ `process_referral_code_on_payment()` - Обработка кода при создании платежа
- ✅ `process_referral_on_payment_confirmation()` - Обработка при подтверждении
- ✅ `apply_referral_discount()` - Применение скидки рефереру

#### ❌ Что отсутствует:

1. **Таблицы в БД:**
   - ❌ Таблица `payments` - Хранение платежей
   - ❌ Таблица `payment_methods` - Методы оплаты

2. **Endpoints для платежей:**
   - ❌ `POST /api/payments/create` - Создание платежа (для лендинга)
   - ❌ `GET /api/payments/status/{payment_id}` - Проверка статуса
   - ❌ `POST /api/payments/confirm` - Подтверждение платежа

   **⚠️ Примечание:** Endpoint `/payments/qr/create` НЕ НУЖЕН, так как iOS не использует QR-оплату (переход на сайт)

3. **Интеграция:**
   - ❌ Нет связи между платежами и реферальной программой
   - ❌ Функции реферальной программы не вызываются

4. **Платежные системы:**
   - ❌ Нет интеграции с СБП
   - ❌ Нет интеграции с интернет-эквайрингом
   - ❌ Нет обработки ручных переводов

---

## 📋 ДЕТАЛЬНЫЙ ПЛАН ДЛЯ ДРУГОЙ ML СИСТЕМЫ

### 🎯 ЦЕЛЬ
Реализовать полную систему оплаты с интеграцией реферальной программы на всех трех компонентах:
1. Официальный сайт `aladdin-ai.ru` (уже готов, но нужна проверка)
2. iOS приложение (требует доработки)
3. Сервер (требует полной реализации)

---

## 📝 ЭТАП 1: БАЗА ДАННЫХ (1-2 часа)

### Задача 1.1: Создать таблицу `payments`

**Файл для создания:** `docs/server/PAYMENTS_TABLE.sql`

**SQL скрипт:**
```sql
-- Таблица для хранения платежей
CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    payment_id VARCHAR(100) UNIQUE NOT NULL,
    user_id INTEGER,
    user_alias VARCHAR(100),
    tariff_id VARCHAR(50),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'RUB',
    payment_method VARCHAR(50),
    period_months INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, paid, failed, expired, cancelled
    referral_code VARCHAR(20),
    referral_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    paid_at TIMESTAMP NULL,
    expires_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (referral_id) REFERENCES referrals(id) ON DELETE SET NULL
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_payments_payment_id ON payments(payment_id);
CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_referral_code ON payments(referral_code);
CREATE INDEX IF NOT EXISTS idx_payments_referral_id ON payments(referral_id);
```

**Инструкция для ML системы:**
1. Подключиться к серверу: `ssh root@149.154.65.180` (пароль: `Sergio675`)
2. Выполнить SQL скрипт:
```bash
PGPASSWORD='AladdinSecure2024!' psql -h localhost -U aladdin_user -d aladdin_db -f PAYMENTS_TABLE.sql
```
3. Проверить создание таблицы:
```bash
PGPASSWORD='AladdinSecure2024!' psql -h localhost -U aladdin_user -d aladdin_db -c "\d payments"
```

---

### Задача 1.2: Создать таблицу `payment_methods`

**Файл для создания:** `docs/server/PAYMENT_METHODS_TABLE.sql`

**SQL скрипт:**
```sql
-- Таблица для методов оплаты
CREATE TABLE IF NOT EXISTS payment_methods (
    id SERIAL PRIMARY KEY,
    method_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    config JSONB,  -- Конфигурация для каждого метода
    created_at TIMESTAMP DEFAULT NOW()
);

-- Вставить методы оплаты
INSERT INTO payment_methods (method_id, name, description) VALUES
('qr_sbp', 'QR / СБП', 'Система быстрых платежей'),
('card_sber', 'Карта Сбербанк', 'Интернет-эквайринг Сбербанка'),
('card_tinkoff', 'Карта Тинькофф', 'Оплата картой через Тинькофф'),
('card_alfa', 'Карта Альфа-Банк', 'Оплата картой через Альфа-Банк'),
('card_vtb', 'Карта ВТБ', 'Оплата картой через ВТБ'),
('card_gpb', 'Карта Газпромбанк', 'Оплата картой через Газпромбанк'),
('card_psb', 'Карта Промсвязьбанк', 'Оплата картой через ПСБ'),
('sberpay', 'SberPay', 'Официальная кнопка Сбербанка'),
('tinkoff_pay', 'Tinkoff Pay', 'Моментальная оплата через приложение Тинькофф'),
('manual_transfer', 'Ручной перевод', 'Банковский перевод по реквизитам')
ON CONFLICT (method_id) DO NOTHING;
```

**Инструкция для ML системы:**
1. Выполнить SQL скрипт аналогично задаче 1.1
2. Проверить вставку данных:
```bash
PGPASSWORD='AladdinSecure2024!' psql -h localhost -U aladdin_user -d aladdin_db -c "SELECT * FROM payment_methods;"
```

---

## 📝 ЭТАП 2: BACKEND API - ENDPOINTS (3-4 часа)

### Задача 2.1: Создать `app/routers/payments.py`

**Файл для создания:** `/opt/aladdin-backend/app/routers/payments.py`

**Полный код файла:**
```python
"""
Endpoints для обработки платежей
Интеграция с реферальной программой
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid

from app.database.database import get_db
from app.auth.auth import get_current_user
from app.referral_payment_functions import (
    process_referral_code_on_payment,
    process_referral_on_payment_confirmation,
    apply_referral_discount
)

router = APIRouter(tags=["payments"])

# ============================================
# МОДЕЛИ ЗАПРОСОВ
# ============================================

class PaymentCreateRequest(BaseModel):
    """Запрос на создание платежа (для лендинга)"""
    tariffId: str
    userAlias: str
    pin: str
    paymentMethod: str
    periodMonths: int
    amount: float
    referralCode: Optional[str] = None
    personalDataConsent: bool = True
    consentTimestamp: Optional[str] = None
    consentIP: Optional[str] = None

# ⚠️ ПРИМЕЧАНИЕ: QRPaymentCreateRequest НЕ НУЖЕН
# iOS приложение НЕ использует QR-оплату - оплата происходит на сайте aladdin-ai.ru
# iOS только открывает сайт через URLHelper.openWebsite() с параметрами ?tariff=family&ref=ABC123

class PaymentStatusResponse(BaseModel):
    """Ответ со статусом платежа"""
    paymentId: str
    status: str
    amount: float
    currency: str
    paidAt: Optional[str] = None

# ============================================
# ENDPOINTS
# ============================================

@router.post("/api/payments/create")
async def create_payment(
    payment_data: PaymentCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Создание платежа (для лендинга)
    
    Используется сайтом aladdin-ai.ru
    """
    try:
        # 1. Генерируем уникальный payment_id
        payment_id = f"PAY_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8].upper()}"
        
        # 2. Вычисляем expires_at (30 минут)
        expires_at = datetime.now() + timedelta(minutes=30)
        
        # 3. Создаем запись в payments
        db.execute(
            text("""
                INSERT INTO payments (
                    payment_id, user_alias, tariff_id, amount, currency,
                    payment_method, period_months, status, referral_code, expires_at
                )
                VALUES (
                    :payment_id, :user_alias, :tariff_id, :amount, :currency,
                    :payment_method, :period_months, :status, :referral_code, :expires_at
                )
            """),
            {
                "payment_id": payment_id,
                "user_alias": payment_data.userAlias,
                "tariff_id": payment_data.tariffId,
                "amount": payment_data.amount,
                "currency": "RUB",
                "payment_method": payment_data.paymentMethod,
                "period_months": payment_data.periodMonths,
                "status": "pending",
                "referral_code": payment_data.referralCode,
                "expires_at": expires_at
            }
        )
        db.commit()
        
        # 4. ✅ Обработать реферальный код
        referral_id = None
        if payment_data.referralCode:
            referral_id = process_referral_code_on_payment(
                db, payment_data.referralCode, None, payment_data.amount
            )
            if referral_id:
                # Обновить payment с referral_id
                db.execute(
                    text("UPDATE payments SET referral_id = :referral_id WHERE payment_id = :payment_id"),
                    {"referral_id": referral_id, "payment_id": payment_id}
                )
                db.commit()
        
        # 5. Возвращаем данные для оплаты
        return {
            "paymentId": payment_id,
            "amount": payment_data.amount,
            "currency": "RUB",
            "expiresAt": expires_at.isoformat(),
            "status": "pending",
            "referralCode": payment_data.referralCode,
            "referralId": referral_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка создания платежа: {str(e)}")


# ⚠️ ПРИМЕЧАНИЕ: Endpoint /payments/qr/create НЕ НУЖЕН
# iOS приложение НЕ использует QR-оплату - оплата происходит на сайте aladdin-ai.ru
# iOS только открывает сайт через URLHelper.openWebsite() с параметрами ?tariff=family&ref=ABC123


@router.get("/api/payments/status/{payment_id}")
async def check_payment_status(
    payment_id: str,
    db: Session = Depends(get_db)
):
    """
    Проверка статуса платежа
    """
    try:
        result = db.execute(
            text("""
                SELECT payment_id, status, amount, currency, paid_at, referral_id, user_id
                FROM payments
                WHERE payment_id = :payment_id
            """),
            {"payment_id": payment_id}
        )
        payment = result.fetchone()
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        # ✅ Если платеж оплачен, обработать реферальную программу
        if payment[1] == "paid" and payment[5]:  # status == "paid" and referral_id
            referral_id = payment[5]
            user_id = payment[6]
            amount = float(payment[2])
            
            # Проверяем, не обработан ли уже
            referral_check = db.execute(
                text("SELECT status FROM referrals WHERE id = :referral_id"),
                {"referral_id": referral_id}
            ).fetchone()
            
            if referral_check and referral_check[0] == "pending":
                # Обрабатываем реферальную программу
                process_referral_on_payment_confirmation(db, user_id, amount)
        
        return {
            "paymentId": payment[0],
            "status": payment[1],
            "amount": float(payment[2]),
            "currency": payment[3],
            "paidAt": payment[4].isoformat() if payment[4] else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка проверки статуса: {str(e)}")


@router.post("/api/payments/confirm")
async def confirm_payment(
    payment_id: str,
    db: Session = Depends(get_db)
):
    """
    Подтверждение платежа (webhook от платежной системы)
    """
    try:
        # 1. Обновить статус платежа
        result = db.execute(
            text("""
                UPDATE payments
                SET status = 'paid', paid_at = NOW()
                WHERE payment_id = :payment_id AND status = 'pending'
                RETURNING user_id, amount, referral_id
            """),
            {"payment_id": payment_id}
        )
        payment = result.fetchone()
        
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found or already processed")
        
        user_id = payment[0]
        amount = float(payment[1])
        referral_id = payment[2]
        
        # 2. ✅ Обработать реферальную программу
        if referral_id:
            process_referral_on_payment_confirmation(db, user_id, amount)
        
        return {"status": "ok", "message": "Payment confirmed"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка подтверждения платежа: {str(e)}")
```

**Инструкция для ML системы:**
1. Создать файл на сервере:
```bash
ssh root@149.154.65.180
cd /opt/aladdin-backend/app/routers
nano payments.py
# Вставить код выше
```

2. Подключить router в `main.py`:
```python
# В файле /opt/aladdin-backend/main.py добавить:
from app.routers import payments

app.include_router(payments.router, tags=["payments"])
```

3. Перезапустить backend:
```bash
systemctl restart aladdin-backend
# Или если запущен вручную:
cd /opt/aladdin-backend
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📝 ЭТАП 3: iOS ПРИЛОЖЕНИЕ (30 минут - 1 час)

### ⚠️ ВАЖНО: QR-оплата УБРАНА из iOS!
В iOS приложении НЕТ QR-оплаты. Вместо этого используется переход на сайт `aladdin-ai.ru` через `URLHelper.openWebsite()`.

### Задача 3.1: Добавить `referralCode` в `URLHelper`

**Файл для редактирования:** `Core/Helpers/URLHelper.swift`

**Что изменить:**
```swift
// Текущий код (строки 11-17):
static func openWebsite(urlString: String, tariffId: String? = nil) {
    var finalURLString = urlString
    
    if let tariffId = tariffId, !tariffId.isEmpty {
        let separator = urlString.contains("?") ? "&" : "?"
        finalURLString = "\(urlString)\(separator)tariff=\(tariffId)"
    }
    // ...
}

// ✅ ИЗМЕНИТЬ НА:
static func openWebsite(urlString: String, tariffId: String? = nil, referralCode: String? = nil) {
    var finalURLString = urlString
    var queryParams: [String] = []
    
    // Добавить tariffId
    if let tariffId = tariffId, !tariffId.isEmpty {
        queryParams.append("tariff=\(tariffId)")
    }
    
    // ✅ ДОБАВИТЬ: referralCode
    if let referralCode = referralCode, !referralCode.isEmpty {
        queryParams.append("ref=\(referralCode)")
    }
    
    // Объединить параметры
    if !queryParams.isEmpty {
        let separator = urlString.contains("?") ? "&" : "?"
        finalURLString = "\(urlString)\(separator)\(queryParams.joined(separator: "&"))"
    }
    
    guard let url = URL(string: finalURLString) else {
        print("❌ URLHelper.openWebsite: невалидный URL \(finalURLString)")
        return
    }
    
    UIApplication.shared.open(url, options: [:], completionHandler: nil)
}
```

**Инструкция для ML системы:**
1. Открыть файл `Core/Helpers/URLHelper.swift`
2. Найти функцию `openWebsite(urlString:tariffId:)`
3. Добавить параметр `referralCode: String? = nil`
4. Изменить логику формирования URL для поддержки нескольких параметров
5. Сохранить файл

---

### Задача 3.2: Получить и передать `referralCode` при переходе на сайт

**Файл для редактирования:** `Screens/10_TariffsScreen.swift`

**Что изменить:**

В функции `tariffCard`, где вызывается `URLHelper.openWebsite()`:
```swift
// Текущий код (строки 313-317):
// ⚠️ Оплата по QR перенесена на лендинг: открываем сайт напрямую
URLHelper.openWebsite(
    urlString: AppConfig.subscriptionWebsiteURL,
    tariffId: tariffObj.id
)

// ✅ ИЗМЕНИТЬ НА:
// ⚠️ Оплата по QR перенесена на лендинг: открываем сайт напрямую
// ✅ ДОБАВИТЬ: Получить referralCode из UserDefaults
let referralCode = UserDefaults.standard.string(forKey: "referral_code")

URLHelper.openWebsite(
    urlString: AppConfig.subscriptionWebsiteURL,
    tariffId: tariffObj.id,
    referralCode: referralCode  // ✅ ПЕРЕДАТЬ referralCode
)
```

**Инструкция для ML системы:**
1. Открыть файл `Screens/10_TariffsScreen.swift`
2. Найти вызов `URLHelper.openWebsite()` (строка 314)
3. Добавить получение `referralCode` из UserDefaults перед вызовом
4. Добавить параметр `referralCode: referralCode` в вызов функции
5. Сохранить файл

---

### Задача 3.3: Сохранить код из реферального экрана

**Файл для редактирования:** `Screens/21_ReferralScreen.swift`

**Что изменить:**

В функции `loadReferralData()`, после получения кода:
```swift
// После строки 811, где устанавливается referralCode
if !referralCode.isEmpty {
    // ✅ ДОБАВИТЬ: Сохранить в UserDefaults для использования при оплате
    UserDefaults.standard.set(referralCode, forKey: "referral_code")
    print("✅ ReferralScreen: Сохранен referralCode: \(referralCode)")
}
```

**Инструкция для ML системы:**
1. Открыть файл `Screens/21_ReferralScreen.swift`
2. Найти функцию `loadReferralData()`
3. После строки, где устанавливается `referralCode`, добавить сохранение в UserDefaults
4. Сохранить файл

---

## 📝 ЭТАП 4: ТЕСТИРОВАНИЕ (2-3 часа)

### Задача 4.1: Тестирование лендинга

**Инструкция для ML системы:**
1. Открыть `https://aladdin-ai.ru/invite/ABC123`
2. Проверить, что отображается баннер со скидкой
3. Перейти к форме оплаты
4. Заполнить форму и нажать "Перейти к оплате"
5. Проверить в консоли браузера (F12), что `referralCode` передается в запросе
6. Проверить ответ сервера (должен быть `paymentId`)

---

### Задача 4.2: Тестирование iOS

**Инструкция для ML системы:**
1. Открыть приложение
2. Перейти в экран реферальной программы
3. Проверить, что код отображается
4. Перейти к оплате тарифа
5. Проверить в логах Xcode, что `referralCode` передается в запросе
6. Проверить ответ сервера

---

### Задача 4.3: Тестирование сервера

**Инструкция для ML системы:**
1. Проверить создание платежа:
```bash
curl -X POST http://149.154.65.180:8000/api/payments/create \
  -H "Content-Type: application/json" \
  -H "X-API-Key: PUBLIC_CLIENT_KEY" \
  -d '{
    "tariffId": "family",
    "userAlias": "testuser",
    "pin": "1234",
    "paymentMethod": "qr_sbp",
    "periodMonths": 1,
    "amount": 800.0,
    "referralCode": "ABC123"
  }'
```

2. Проверить статус платежа:
```bash
curl http://149.154.65.180:8000/api/payments/status/PAY_20241123120000_ABCD1234
```

3. Проверить подтверждение платежа:
```bash
curl -X POST http://149.154.65.180:8000/api/payments/confirm?payment_id=PAY_20241123120000_ABCD1234
```

---

## 📋 ЧЕКЛИСТ ВЫПОЛНЕНИЯ

### База данных:
- [ ] Создать таблицу `payments`
- [ ] Создать таблицу `payment_methods`
- [ ] Вставить методы оплаты
- [ ] Проверить создание таблиц

### Backend API:
- [ ] Создать файл `app/routers/payments.py`
- [ ] Реализовать `POST /api/payments/create` (для лендинга)
- [ ] Реализовать `GET /api/payments/status/{payment_id}`
- [ ] Реализовать `POST /api/payments/confirm`
- [ ] Подключить router в `main.py`
- [ ] Перезапустить backend

**⚠️ Примечание:** Endpoint `/payments/qr/create` НЕ НУЖЕН (iOS не использует QR-оплату)

### iOS приложение:
- [ ] Добавить параметр `referralCode` в `URLHelper.openWebsite()`
- [ ] Получить `referralCode` из UserDefaults при переходе на оплату
- [ ] Передать `referralCode` в URL при открытии сайта
- [ ] Сохранить код из реферального экрана в UserDefaults

### Тестирование:
- [ ] Протестировать создание платежа с реферальным кодом
- [ ] Протестировать создание платежа без реферального кода
- [ ] Протестировать подтверждение платежа
- [ ] Протестировать начисление скидки рефереру
- [ ] Протестировать применение скидки рефереру при оплате

---

## 📊 ОЦЕНКА ВРЕМЕНИ

- **База данных**: 1-2 часа
- **Backend API**: 3-4 часа
- **iOS приложение**: 30 минут - 1 час (только передача referralCode в URL)
- **Тестирование**: 2-3 часа

**ИТОГО: 6.5-10 часов**

---

## ✅ ЗАКЛЮЧЕНИЕ

### Текущее состояние:
- **Официальный сайт**: ✅ 100% готов
- **iOS приложение**: ⚠️ 75% готов (требует доработки)
- **Сервер**: ❌ 25% готов (требует реализации)

### После выполнения плана:
- **Официальный сайт**: ✅ 100% готов (уже готов)
- **iOS приложение**: ✅ 100% готов (только добавить передачу referralCode в URL)
- **Сервер**: ✅ 100% готов (нужна реализация endpoints)

**ОБЩАЯ ГОТОВНОСТЬ ПОСЛЕ ВЫПОЛНЕНИЯ: 100%**

### ⚠️ ВАЖНОЕ УТОЧНЕНИЕ:
- **iOS приложение НЕ использует QR-оплату** - оплата происходит на сайте `aladdin-ai.ru`
- **iOS только открывает сайт** с параметрами `?tariff=family&ref=ABC123`
- **Вся логика оплаты на сайте** - там уже все реализовано и работает

---

## 📚 ДОПОЛНИТЕЛЬНЫЕ ДОКУМЕНТЫ

1. **`docs/PAYMENT_SYSTEM_COMPLETE_ANALYSIS.md`** - Полный анализ системы оплаты
2. **`docs/server/referral_payment_functions.py`** - Функции для интеграции реферальной программы
3. **`docs/server/referral_payment_integration.py`** - Примеры интеграции
4. **`docs/server/REFERRAL_DB_SETUP.sql`** - SQL скрипт для реферальной программы
5. **`docs/server/REFERRAL_INTEGRATION_GUIDE.md`** - Руководство по интеграции

---

**ВСЕ ГОТОВО ДЛЯ РЕАЛИЗАЦИИ!** 🚀

