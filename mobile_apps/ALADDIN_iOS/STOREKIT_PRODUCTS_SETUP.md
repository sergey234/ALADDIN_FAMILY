# 💰 StoreKit Products Setup

## 📋 Настройка продуктов в App Store Connect

### ✅ ШАГ 1: Создать продукты в App Store Connect

1. Перейдите: https://appstoreconnect.apple.com
2. Выберите ваше приложение
3. **Features → In-App Purchases**
4. Нажмите **+** (Create)

---

### ✅ ШАГ 2: Создать 4 подписки

#### 1️⃣ БАЗОВЫЙ ТАРИФ (FREE)

- **Product ID**: `family.aladdin.ios.subscription.basic`
- **Reference Name**: ALADDIN Basic Subscription
- **Subscription Group**: ALADDIN Subscriptions
- **Duration**: 1 Month (Auto-Renewable)
- **Price**: **₽0** (Free Trial / Freemium)

**Localization (Russian):**
- Display Name: `Базовый`
- Description: `1 устройство, базовая защита, ограниченная аналитика`

---

#### 2️⃣ ИНДИВИДУАЛЬНЫЙ ТАРИФ

- **Product ID**: `family.aladdin.ios.subscription.individual`
- **Reference Name**: ALADDIN Individual Subscription
- **Subscription Group**: ALADDIN Subscriptions
- **Duration**: 1 Month (Auto-Renewable)
- **Price**: **₽199/месяц**

**Localization (Russian):**
- Display Name: `Индивидуальный`
- Description: `1 устройство, полная защита, расширенная аналитика, AI помощник`

---

#### 3️⃣ СЕМЕЙНЫЙ ТАРИФ (РЕКОМЕНДУЕТСЯ)

- **Product ID**: `family.aladdin.ios.subscription.family`
- **Reference Name**: ALADDIN Family Subscription
- **Subscription Group**: ALADDIN Subscriptions
- **Duration**: 1 Month (Auto-Renewable)
- **Price**: **₽499/месяц**

**Localization (Russian):**
- Display Name: `Семейный`
- Description: `До 5 устройств, полная защита, AI помощник, родительский контроль`

**Tags**: `RECOMMENDED` ⭐

---

#### 4️⃣ ПРЕМИУМ ТАРИФ

- **Product ID**: `family.aladdin.ios.subscription.premium`
- **Reference Name**: ALADDIN Premium Subscription
- **Subscription Group**: ALADDIN Subscriptions
- **Duration**: 1 Month (Auto-Renewable)
- **Price**: **₽999/месяц**

**Localization (Russian):**
- Display Name: `Премиум`
- Description: `До 10 устройств, все функции, приоритетная поддержка, эксклюзивные возможности`

---

### ✅ ШАГ 3: Настроить Subscription Group

1. **Group Name**: ALADDIN Subscriptions
2. **Level Ranking**:
   - Level 1: Basic (₽0)
   - Level 2: Individual (₽199)
   - Level 3: Family (₽499) ⭐
   - Level 4: Premium (₽999)

---

### ✅ ШАГ 4: Добавить Free Trial (опционально)

Для каждой подписки (кроме Basic):
- **Introductory Offer**: 7 days free trial
- **Promotional Offer**: 50% off first month

---

### ✅ ШАГ 5: Создать StoreKit Configuration (для тестирования)

1. В Xcode: **File → New → File → StoreKit Configuration File**
2. Назовите: `ALADDIN_StoreKit_Config.storekit`
3. Добавьте все 4 продукта с теми же Product IDs
4. Используйте для тестирования БЕЗ подключения к App Store Connect

---

## 🔧 Интеграция в код (УЖЕ ГОТОВА!)

✅ **StoreManager.swift** - управление покупками  
✅ **TariffsViewModel.swift** - интеграция с UI  
✅ **TariffsScreen.swift** - отображение тарифов  

**Всё готово! Нужно только создать продукты в App Store Connect!**

---

## 🧪 Тестирование

### Локальное тестирование (без App Store Connect):

1. В Xcode выберите: **Product → Scheme → Edit Scheme**
2. **Run → Options → StoreKit Configuration**
3. Выберите: `ALADDIN_StoreKit_Config.storekit`
4. Запустите приложение
5. Покупки будут работать локально! ✅

### Тестирование в Sandbox:

1. Создайте Sandbox Tester в App Store Connect
2. **Users and Access → Sandbox Testers → +**
3. Email: `sandbox-tester@aladdin.family`
4. На устройстве: Settings → App Store → Sandbox Account
5. Войдите под тестовым аккаунтом
6. Покупки будут бесплатны! ✅

---

## 📊 Метрики покупок

StoreManager автоматически отслеживает:
- ✅ Какие продукты куплены
- ✅ Активные подписки
- ✅ Истёкшие подписки
- ✅ Восстановление покупок
- ✅ Обновления транзакций

**Готово к production!** 🚀



