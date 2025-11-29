# 💰 ПЛАН РЕАЛИЗАЦИИ: Скидки за предоплату на 3/6/12 месяцев

**Дата:** 15 ноября 2025  
**Статус:** 🚀 **В РАБОТЕ**

---

## 📋 ОБЩИЙ ПЛАН

### Скидки:
- **3 месяца:** скидка 10%
- **6 месяцев:** скидка 15%
- **12 месяцев:** скидка 20%

### Примеры цен (BASIC - 290₽/месяц):
- **1 месяц:** 290₽ (без скидки)
- **3 месяца:** 783₽ (экономия 87₽, -10%)
- **6 месяцев:** 1479₽ (экономия 261₽, -15%)
- **12 месяцев:** 2784₽ (экономия 696₽, -20%)

---

## 🔧 BACKEND (Python)

### Задача 1: Обновить структуру `SubscriptionPlan`

**Файл:** `/Users/sergejhlystov/ALADDIN_NEW/security/managers/subscription_manager.py`

**Изменения:**
```python
@dataclass
class SubscriptionPlan:
    tier: SubscriptionTier
    name: str
    price: Decimal
    currency: str = "RUB"
    billing_period: str = "monthly"  # monthly, 3months, 6months, 12months, yearly
    period_months: int = 1  # 1, 3, 6, 12
    discount_percent: Optional[int] = None  # Процент скидки
    original_price: Optional[Decimal] = None  # Цена без скидки
    trial_days: int = 0
    max_devices: int = 1
    features: Set[Features] = field(default_factory=set)
    description: str = ""
    is_active: bool = True
    
    @property
    def monthly_price(self) -> Decimal:
        """Цена за месяц (для сравнения)"""
        return self.price / Decimal(self.period_months)
    
    @property
    def savings(self) -> Optional[Decimal]:
        """Экономия при долгосрочной подписке"""
        if self.original_price:
            return self.original_price - self.price
        return None
```

### Задача 2: Добавить тарифы на 3/6/12 месяцев

**Добавить в `_initialize_plans()`:**

```python
# BASIC 3 месяца (скидка 10%)
self.plans[SubscriptionTier.BASIC_3M] = SubscriptionPlan(
    tier=SubscriptionTier.BASIC_3M,
    name="Basic 3 месяца",
    price=Decimal("783"),  # 290 * 3 * 0.9
    period_months=3,
    discount_percent=10,
    original_price=Decimal("870"),  # 290 * 3
    billing_period="3months",
    # ... остальные поля как в BASIC
)

# BASIC 6 месяцев (скидка 15%)
self.plans[SubscriptionTier.BASIC_6M] = SubscriptionPlan(
    tier=SubscriptionTier.BASIC_6M,
    name="Basic 6 месяцев",
    price=Decimal("1479"),  # 290 * 6 * 0.85
    period_months=6,
    discount_percent=15,
    original_price=Decimal("1740"),  # 290 * 6
    billing_period="6months",
    # ... остальные поля
)

# BASIC 12 месяцев (скидка 20%)
self.plans[SubscriptionTier.BASIC_12M] = SubscriptionPlan(
    tier=SubscriptionTier.BASIC_12M,
    name="Basic 12 месяцев",
    price=Decimal("2784"),  # 290 * 12 * 0.8
    period_months=12,
    discount_percent=20,
    original_price=Decimal("3480"),  # 290 * 12
    billing_period="12months",
    # ... остальные поля
)

# Аналогично для FAMILY и PREMIUM
```

### Задача 3: Обновить `SubscriptionTier` enum

**Добавить новые типы:**
```python
class SubscriptionTier(Enum):
    FREEMIUM = "freemium"
    BASIC = "basic"
    BASIC_3M = "basic_3m"
    BASIC_6M = "basic_6m"
    BASIC_12M = "basic_12m"
    FAMILY = "family"
    FAMILY_3M = "family_3m"
    FAMILY_6M = "family_6m"
    FAMILY_12M = "family_12m"
    PREMIUM = "premium"
    PREMIUM_3M = "premium_3m"
    PREMIUM_6M = "premium_6m"
    PREMIUM_12M = "premium_12m"
    CUSTOM = "custom"
```

### Задача 4: Обновить `create_subscription()` для поддержки периодов

**Добавить параметр `period_months`:**
```python
async def create_subscription(
    self, 
    family_id: str, 
    tier: SubscriptionTier,
    period_months: int = 1,  # НОВОЕ: период подписки
    trial_days: Optional[int] = None
) -> Dict[str, Any]:
    # ...
    # Определяем дату окончания с учетом периода
    end_date = now + timedelta(days=30 * period_months)
    # ...
```

---

## 📱 iOS (Swift)

### Задача 1: Обновить структуру `Tariff`

**Файл:** `ViewModels/TariffsViewModel.swift`

**Изменения:**
```swift
struct Tariff: Identifiable {
    let id: String
    let title: String
    let price: String
    let period: String
    let features: [String]
    let product: Product?
    var isPurchased: Bool
    
    // НОВЫЕ ПОЛЯ:
    let periodMonths: Int  // 1, 3, 6, 12
    let originalPrice: String?  // Цена без скидки
    let discountPercent: Int?  // Процент скидки
    let monthlyPrice: String  // Цена за месяц (для сравнения)
    let savings: String?  // Экономия
    
    init(
        id: String,
        title: String,
        price: String,
        period: String,
        features: [String],
        product: Product? = nil,
        isPurchased: Bool = false,
        periodMonths: Int = 1,
        originalPrice: String? = nil,
        discountPercent: Int? = nil,
        monthlyPrice: String? = nil,
        savings: String? = nil
    ) {
        self.id = id
        self.title = title
        self.price = price
        self.period = period
        self.features = features
        self.product = product
        self.isPurchased = isPurchased
        self.periodMonths = periodMonths
        self.originalPrice = originalPrice
        self.discountPercent = discountPercent
        self.monthlyPrice = monthlyPrice ?? price
        self.savings = savings
    }
}
```

### Задача 2: Добавить UI выбора периода в `TariffsScreen`

**Добавить:**
- Сегментированный контрол для выбора периода (1/3/6/12 месяцев)
- Отображение скидки и экономии
- Отображение цены за месяц для сравнения

### Задача 3: Обновить `PaymentQRScreen` для поддержки периода

**Добавить:**
- Выбор периода при QR-оплате
- Передача периода в API запрос

### Задача 4: Обновить API модели

**Файл:** `Core/Models/APIModels.swift`

**Обновить `TariffResponse`:**
```swift
struct TariffResponse: Codable, Identifiable {
    let id: String
    let name: String
    let price: Int
    let period: String
    let periodMonths: Int?  // НОВОЕ
    let discountPercent: Int?  // НОВОЕ
    let originalPrice: Int?  // НОВОЕ
    let features: [String]
    let isRecommended: Bool
}
```

---

## 📊 ПРИОРИТЕТЫ

1. **Backend:** Обновить структуру и добавить тарифы
2. **iOS:** Обновить модель данных
3. **iOS:** Добавить UI выбора периода
4. **iOS:** Обновить QR-оплату
5. **Тестирование:** Проверить все сценарии

---

**Дата создания:** 15 ноября 2025  
**Статус:** 🚀 **В РАБОТЕ**




