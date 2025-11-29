# 💰 СТАТУС СКИДОК ЗА 3/6/12 МЕСЯЦЕВ

**Дата:** 15 ноября 2025  
**Статус:** ❌ **НЕ РЕАЛИЗОВАНО**

---

## 📋 ЧТО БЫЛО ПЛАНИРОВАНО

### Скидки за предоплату:

1. **3 месяца:**
   - Скидка: **10%**
   - Пример: 290₽ × 3 = 870₽ → **783₽** (экономия 87₽)

2. **6 месяцев:**
   - Скидка: **15%**
   - Пример: 290₽ × 6 = 1740₽ → **1479₽** (экономия 261₽)

3. **12 месяцев:**
   - Скидка: **20%**
   - Пример: 290₽ × 12 = 3480₽ → **2784₽** (экономия 696₽)

---

## ❌ ТЕКУЩИЙ СТАТУС

### iOS (Мобильное приложение):

**Файлы:**
- `ViewModels/TariffsViewModel.swift`
- `Screens/10_TariffsScreen.swift`
- `Core/Models/APIModels.swift`

**Что ЕСТЬ:**
- ✅ Тарифы: FREE, PERSONAL (290₽), FAMILY (490₽), PREMIUM (990₽)
- ✅ Период только "в месяц" (`period: String`)
- ✅ Базовая структура `Tariff`

**Что ОТСУТСТВУЕТ:**
- ❌ НЕТ тарифов на 3/6/12 месяцев
- ❌ НЕТ системы скидок
- ❌ НЕТ полей `discount`, `originalPrice`, `discountPercent`
- ❌ НЕТ выбора периода подписки в UI
- ❌ НЕТ полей `periodMonths`, `monthlyPrice`, `savings`

**Готовность:** ❌ **0%** (не реализовано)

---

### Backend (Python):

**Файл:** `security/managers/subscription_manager.py`

**Что ЕСТЬ:**
- ✅ Структура `SubscriptionPlan` с полем `billing_period: str = "monthly"`
- ✅ Поддержка `billing_period` (monthly, yearly)
- ✅ Тарифы: FREEMIUM, BASIC (290₽), FAMILY (490₽), PREMIUM (900₽)

**Что ОТСУТСТВУЕТ:**
- ❌ НЕТ тарифов на 3/6/12 месяцев (только monthly, yearly)
- ❌ НЕТ системы скидок
- ❌ НЕТ полей `discount_percent`, `original_price`, `monthly_price`
- ❌ НЕТ логики расчета цены с учетом скидки

**Готовность:** ⚠️ **20%** (структура поддерживает yearly, но нет 3/6/12 месяцев и скидок)

---

## 📄 ГДЕ БЫЛО ПЛАНИРОВАНО

### Документ: `docs/COMPLETE_SUBSCRIPTION_FEATURES_ANALYSIS.md`

**Дата:** 14 ноября 2025

**План реализации:**
- ✅ Детальный план был подготовлен
- ✅ Примеры кода были написаны
- ❌ НО: Реализация НЕ была выполнена

**Примеры кода (из плана):**

**Backend:**
```python
# BASIC 3 месяца (скидка 10%)
self.plans[SubscriptionTier.BASIC_3M] = SubscriptionPlan(
    tier=SubscriptionTier.BASIC_3M,
    name="Basic 3 месяца",
    price=Decimal("783"),  # 290 * 3 * 0.9
    period_months=3,
    discount_percent=10,
    original_price=Decimal("870"),  # 290 * 3
    # ...
)

# BASIC 6 месяцев (скидка 15%)
self.plans[SubscriptionTier.BASIC_6M] = SubscriptionPlan(
    tier=SubscriptionTier.BASIC_6M,
    name="Basic 6 месяцев",
    price=Decimal("1479"),  # 290 * 6 * 0.85
    period_months=6,
    discount_percent=15,
    original_price=Decimal("1740"),  # 290 * 6
    # ...
)

# BASIC 12 месяцев (скидка 20%)
self.plans[SubscriptionTier.BASIC_12M] = SubscriptionPlan(
    tier=SubscriptionTier.BASIC_12M,
    name="Basic 12 месяцев",
    price=Decimal("2784"),  # 290 * 12 * 0.8
    period_months=12,
    discount_percent=20,
    original_price=Decimal("3480"),  # 290 * 12
    # ...
)
```

**iOS:**
```swift
struct Tariff: Identifiable {
    let id: String
    let title: String
    let price: String
    let period: String
    let features: [String]
    let product: Product?
    var isPurchased: Bool
    
    // НОВЫЕ ПОЛЯ (планировались):
    let periodMonths: Int  // 1, 3, 6, 12
    let originalPrice: String?  // Цена без скидки
    let discountPercent: Int?  // Процент скидки
    let monthlyPrice: String  // Цена за месяц (для сравнения)
    let savings: String?  // Экономия
}
```

---

## 🎯 ВЫВОД

### ❌ Реализация НЕ была выполнена

**Причины:**
1. План был подготовлен, но реализация была отложена
2. Приоритет был отдан умным уведомлениям (которые были реализованы)
3. Предоплата на несколько месяцев была помечена как "Приоритет 2" (низкий)

**Текущее состояние:**
- ❌ Скидки за 3/6/12 месяцев **НЕ реализованы**
- ❌ Система скидок **НЕ реализована**
- ❌ UI для выбора периода **НЕ реализован**

---

## 📋 ЧТО НУЖНО СДЕЛАТЬ (если нужно реализовать)

### Backend (Python):

1. Обновить `SubscriptionPlan`:
   - Добавить поля: `period_months`, `discount_percent`, `original_price`
   - Добавить метод `monthly_price` и `savings`

2. Добавить тарифы:
   - BASIC_3M, BASIC_6M, BASIC_12M
   - FAMILY_3M, FAMILY_6M, FAMILY_12M
   - PREMIUM_3M, PREMIUM_6M, PREMIUM_12M

3. Обновить API:
   - Добавить endpoint для получения тарифов с разными периодами
   - Обновить `create_subscription()` для поддержки периодов

### iOS (Swift):

1. Обновить структуру `Tariff`:
   - Добавить поля: `periodMonths`, `originalPrice`, `discountPercent`, `monthlyPrice`, `savings`

2. Обновить UI:
   - Добавить выбор периода (1/3/6/12 месяцев)
   - Отображать скидку и экономию
   - Показывать цену за месяц для сравнения

3. Обновить `TariffsViewModel`:
   - Загружать тарифы с разными периодами
   - Обрабатывать скидки

---

**Дата проверки:** 15 ноября 2025  
**Статус:** ❌ **НЕ РЕАЛИЗОВАНО**  
**План:** ✅ **БЫЛ ПОДГОТОВЛЕН, НО НЕ ВЫПОЛНЕН**




