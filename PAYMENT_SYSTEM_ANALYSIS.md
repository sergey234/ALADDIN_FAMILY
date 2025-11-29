# 💳 АНАЛИЗ СИСТЕМЫ ОПЛАТЫ В ПРИЛОЖЕНИИ ALADDIN

**Дата анализа:** 29 октября 2025

---

## 📋 ОБЗОР

В приложении ALADDIN реализована **двухрежимная система оплаты**:
1. **QR-оплата** (для России) - СБП, SberPay, банковские карты
2. **IAP (In-App Purchase)** (для других регионов) - через App Store

---

## 🗂️ СТРУКТУРА ФАЙЛОВ ОПЛАТЫ

### 📱 Экраны (Screens)

| Файл | Назначение | Статус |
|------|-----------|--------|
| **`10_TariffsScreen.swift`** | Главный экран выбора тарифов | ✅ Реализован |
| **`25_PaymentQRScreen.swift`** | Экран оплаты через QR-код | ✅ Реализован |

### 🧠 ViewModels (Логика)

| Файл | Назначение | Статус |
|------|-----------|--------|
| **`ViewModels/TariffsViewModel.swift`** | Логика экрана тарифов | ✅ Реализован |
| **`ViewModels/PaymentQRViewModel.swift`** | Логика QR-оплаты | ✅ Реализован |

### 💰 Менеджеры покупок

| Файл | Назначение | Статус |
|------|-----------|--------|
| **`Core/Store/StoreManager.swift`** | Менеджер покупок App Store (StoreKit 2) | ✅ Реализован |

### ⚙️ Конфигурация

| Файл | Назначение | Статус |
|------|-----------|--------|
| **`Core/Config/AppConfig.swift`** | Определение региона и способа оплаты | ✅ Реализован |
| **`Core/Network/APIService.swift`** | API для QR-оплаты | ✅ Реализован |

### 📦 Модели данных

| Файл | Назначение | Статус |
|------|-----------|--------|
| **`Core/Models/APIModels.swift`** | Модели для API оплаты | ✅ Реализован |

---

## 🔄 ПОТОК ОПЛАТЫ

### 1️⃣ Выбор тарифа (`10_TariffsScreen.swift`)

**Функция:** `tariffCard(_ tariff: TariffType)` → кнопка оплаты

**Логика:**
```swift
Button(action: {
    selectedTariff = tariff
    
    if AppConfig.useAlternativePayments {
        // Россия → QR оплата
        selectedTariffForPayment = tariffObj
        showPaymentQRScreen = true  // ← Открывает PaymentQRScreen
    } else {
        // За границей → IAP
        print("IAP purchase")
    }
})
```

**Навигация:**
- `@State private var showPaymentQRScreen = false`
- `.sheet(isPresented: $showPaymentQRScreen) { PaymentQRScreen(...) }`

---

### 2️⃣ QR-оплата (`25_PaymentQRScreen.swift`)

**Основные функции:**

#### `createPayment()`
- Вызывается при открытии экрана (`onAppear`)
- Создаёт запрос на backend
- Получает QR-коды для разных способов оплаты

#### `checkPaymentStatus()`
- Проверяет статус оплаты на сервере
- Запускается вручную или автоматически каждые 30 секунд

#### `startAutoCheck()`
- Автоматическая проверка каждые 30 секунд
- Останавливается при успешной оплате или истечении срока

**Методы оплаты:**
- СБП (Система быстрых платежей)
- СберPay
- Универсальный QR
- Банковская карта
- Apple Pay

---

### 3️⃣ IAP для других регионов (`StoreManager.swift`)

**Основные функции:**

#### `purchase(_ product: Product)`
- Покупка через App Store (StoreKit 2)
- Проверка подлинности транзакции
- Обновление статуса покупок

#### `restorePurchases()`
- Восстановление покупок из App Store
- Синхронизация с сервером Apple

**Product IDs:**
```swift
family.aladdin.ios.subscription.basic
family.aladdin.ios.subscription.individual
family.aladdin.ios.subscription.family
family.aladdin.ios.subscription.premium
```

---

## 🔀 ОПРЕДЕЛЕНИЕ СПОСОБА ОПЛАТЫ

**Файл:** `Core/Config/AppConfig.swift`

```swift
static var isRussianRegion: Bool {
    return Locale.current.regionCode == "RU"
}

static var useAlternativePayments: Bool {
    return isRussianRegion  // Россия → QR
}

static var useIAP: Bool {
    return !isRussianRegion  // Не Россия → IAP
}
```

**Логика:**
- 🇷🇺 **Россия** (`RU`) → QR-оплата через `PaymentQRScreen`
- 🌍 **Другие регионы** → IAP через `StoreManager`

---

## 🌐 API ENDPOINTS

**Файл:** `Core/Network/APIService.swift`

### Создание QR-платежа
```swift
POST /api/payments/qr/create
Request: CreateQRPaymentRequest
Response: CreateQRPaymentResponse
```

### Проверка статуса оплаты
```swift
GET /api/payments/qr/status/{paymentId}
Response: CheckQRPaymentStatusResponse
```

---

## 📦 МОДЕЛИ ДАННЫХ

### `CreateQRPaymentRequest`
```swift
{
    amount: Double,
    currency: String,  // "RUB"
    description: String,
    tariffId: String
}
```

### `CreateQRPaymentResponse`
```swift
{
    paymentId: String,
    qrCode: String,  // URL изображения QR-кода
    expiresAt: Date
}
```

### `CheckQRPaymentStatusResponse`
```swift
{
    status: String,  // "pending", "completed", "expired"
    amount: Double,
    currency: String
}
```

---

## 🎯 КЛЮЧЕВЫЕ ФУНКЦИИ

### `TariffsViewModel.swift`

| Функция | Назначение |
|---------|-----------|
| `loadProducts()` | Загрузить продукты из App Store |
| `selectTariff(_:)` | Выбрать тариф |
| `purchaseSelectedTariff()` | **Купить выбранный тариф** (главная функция!) |
| `shouldUseQRPayment()` | Проверить, нужен ли QR |
| `restorePurchases()` | Восстановить покупки |

### `PaymentQRViewModel.swift`

| Функция | Назначение |
|---------|-----------|
| `createPayment()` | **Создать платеж и получить QR-коды** |
| `checkPaymentStatus()` | **Проверить статус оплаты** |
| `startAutoCheck()` | Автоматическая проверка каждые 30 сек |
| `stopAutoCheck()` | Остановить автоматическую проверку |

### `StoreManager.swift`

| Функция | Назначение |
|---------|-----------|
| `loadProducts()` | Загрузить продукты App Store |
| `purchase(_:)` | **Купить продукт через App Store** |
| `restorePurchases()` | Восстановить покупки |
| `isPurchased(_:)` | Проверить куплен ли продукт |

---

## 🔗 СВЯЗЬ МЕЖДУ КОМПОНЕНТАМИ

```
10_TariffsScreen.swift
    ↓ (пользователь выбирает тариф)
    ↓ (кнопка "ОПЛАТИТЬ ЧЕРЕЗ QR")
    ↓
25_PaymentQRScreen.swift
    ↓ (использует)
PaymentQRViewModel.swift
    ↓ (вызывает)
APIService.createQRPayment()
    ↓ (POST /api/payments/qr/create)
    ↓
Backend API
```

```
10_TariffsScreen.swift
    ↓ (пользователь выбирает тариф)
    ↓ (для не-России)
    ↓
TariffsViewModel.purchaseSelectedTariff()
    ↓ (использует)
StoreManager.purchase()
    ↓ (StoreKit 2)
    ↓
App Store
```

---

## 📊 СТАТУСЫ ОПЛАТЫ

| Статус | Описание |
|--------|----------|
| `pending` | Ожидает оплаты |
| `completed` | Оплачено успешно ✅ |
| `expired` | Истёк срок оплаты ❌ |
| `cancelled` | Отменено пользователем ❌ |

---

## ✅ ИТОГОВАЯ СВОДКА

### Главная страница оплаты:
**`10_TariffsScreen.swift`** — экран выбора тарифов

### Главная функция оплаты:
**`TariffsViewModel.purchaseSelectedTariff()`** — определяет способ оплаты и запускает процесс

### Способ оплаты (регион):
- 🇷🇺 **Россия:** `25_PaymentQRScreen.swift` → `PaymentQRViewModel.createPayment()`
- 🌍 **Другие:** `StoreManager.purchase()` → IAP через App Store

### Проверка статуса:
- **QR:** `PaymentQRViewModel.checkPaymentStatus()` — каждые 30 сек
- **IAP:** Автоматически через StoreKit 2

---

## 🎯 КЛЮЧЕВЫЕ ТОЧКИ ВХОДА

1. **Выбор тарифа:** `10_TariffsScreen.swift`, строка 204
2. **Создание QR-платежа:** `25_PaymentQRScreen.swift`, строка 73 → `PaymentQRViewModel.createPayment()`
3. **Покупка через IAP:** `TariffsViewModel.purchaseSelectedTariff()`, строка 138 → `StoreManager.purchase()`
4. **Проверка статуса:** `PaymentQRViewModel.checkPaymentStatus()`, строка 201

---

**Статус:** ✅ **ВСЁ РЕАЛИЗОВАНО И ГОТОВО К ИСПОЛЬЗОВАНИЮ!**
