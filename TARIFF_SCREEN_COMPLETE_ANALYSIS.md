# 💳 ДЕТАЛЬНЫЙ АНАЛИЗ СТРАНИЦЫ ТАРИФОВ В МОБИЛЬНОМ ПРИЛОЖЕНИИ ALADDIN iOS

**Дата анализа:** 2025-01-22  
**Версия приложения:** 1.0.0  
**Платформа:** iOS (SwiftUI)

---

## 📋 СОДЕРЖАНИЕ

1. [Обзор архитектуры](#обзор-архитектуры)
2. [Компоненты системы](#компоненты-системы)
3. [Потоки данных](#потоки-данных)
4. [Интеграции](#интеграции)
5. [Сценарии использования](#сценарии-использования)
6. [Технические детали](#технические-детали)
7. [Диаграммы взаимодействия](#диаграммы-взаимодействия)

---

## 🏗️ ОБЗОР АРХИТЕКТУРЫ

### Архитектурный паттерн

Приложение использует **MVVM (Model-View-ViewModel)** архитектуру с элементами **Clean Architecture**:

```
┌─────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ TariffsScreen│  │ TariffCardView│ │TariffFeatures│   │
│  │    (View)    │  │   (Component) │ │   Gallery    │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │           │
│         └─────────────────┼─────────────────┘           │
│                           │                             │
│                    ┌──────▼───────┐                      │
│                    │TariffsViewModel│                    │
│                    │   (ViewModel) │                     │
│                    └──────┬───────┘                     │
└────────────────────────────┼─────────────────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────┐
│                    BUSINESS LAYER                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │TariffManager │  │StoreManager  │  │ProtectionSet │  │
│  │              │  │              │  │tingsManager   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │          │
│         └─────────────────┼─────────────────┘          │
└───────────────────────────┼────────────────────────────┘
                             │
┌────────────────────────────┼─────────────────────────────┐
│                    DATA LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  UserDefaults │  │  StoreKit 2  │  │  APIService   │  │
│  │  (Local)      │  │  (IAP)       │  │  (Backend)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Принципы проектирования

1. **Separation of Concerns** - четкое разделение ответственности
2. **Dependency Injection** - зависимости передаются через инициализаторы
3. **Reactive Programming** - использование Combine для реактивности
4. **Singleton Pattern** - для менеджеров (TariffManager, StoreManager)
5. **Observer Pattern** - через NotificationCenter и Combine

---

## 🧩 КОМПОНЕНТЫ СИСТЕМЫ

### 1. TariffsScreen (View Layer)

**Файл:** `Screens/10_TariffsScreen.swift`  
**Строки:** 1-549  
**Ответственность:** UI представление экрана тарифов

#### Структура компонента:

```swift
struct TariffsScreen: View {
    // MARK: - State
    @EnvironmentObject private var navigationManager: NavigationManager
    @EnvironmentObject private var localizationManager: LocalizationManager
    @StateObject private var viewModel = TariffsViewModel()
    
    @State private var showPrivacyPolicy = false
    @State private var showTermsOfService = false
    @AppStorage("selected_tariff_type") private var selectedTariffRaw: String = "family"
}
```

#### Ключевые функции:

1. **Отображение тарифов** (строки 145-148)
   - 4 карточки тарифов: Free, Personal, Family, Premium
   - Каждая карточка создается через `tariffCard(_:)`

2. **Обработка выбора тарифа** (строки 291-377)
   - Проверка региона (Россия vs остальной мир)
   - Для России → открытие сайта с QR оплатой
   - Для остальных → IAP через App Store

3. **Активация кода подписки** (строки 486-536)
   - Кнопка активации (только для России)
   - Навигация на экран активации кода

4. **Галерея функций** (строка 157)
   - Компонент `TariffFeaturesGallery`
   - Показывает детали функций по тарифам

#### Enum TariffType (строки 29-114):

```swift
enum TariffType: String {
    case free = "free"
    case personal = "personal"
    case family = "family"
    case premium = "premium"
    
    // Методы:
    func title(localizationManager: LocalizationManager) -> String
    var price: String
    func period(localizationManager: LocalizationManager) -> String
    func features(localizationManager: LocalizationManager) -> [String]
    var color: Color
    var recommended: Bool
}
```

#### Lifecycle hooks:

- `.task` (строки 171-183) - загрузка продуктов при открытии экрана
- `.alert` (строки 188-210) - показ ошибок и успешных покупок

---

### 2. TariffsViewModel (ViewModel Layer)

**Файл:** `ViewModels/TariffsViewModel.swift`  
**Строки:** 1-665  
**Ответственность:** Бизнес-логика экрана тарифов

#### Структура класса:

```swift
@MainActor
class TariffsViewModel: ObservableObject {
    @Published var tariffs: [Tariff] = []
    @Published var selectedTariff: Tariff?
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var isPurchaseSuccessful: Bool = false
    
    private let storeManager: StoreManager
    private var cancellables = Set<AnyCancellable>()
}
```

#### Ключевые методы:

1. **loadProducts()** (строки 88-92)
   - Загружает продукты из App Store через StoreManager
   - Обновляет список тарифов

2. **updateTariffs(from:)** (строки 106-133)
   - Преобразует StoreKit Product в модель Tariff
   - Фильтрует только платные подписки
   - Обновляет статус покупки

3. **purchaseSelectedTariff(tariff:)** (строки 194-472)
   - Основная функция покупки тарифа
   - Проверяет валидность тарифа
   - Обрабатывает бесплатный тариф
   - Для IAP: вызывает StoreManager.purchase()
   - Автоматически активирует тариф через TariffManager

4. **findProductID(for:)** (строки 477-522)
   - Маппинг ID тарифа на ProductID из App Store
   - Поддерживает точное и частичное совпадение

5. **mapTariffToTariffType(_:)** (строки 529-567)
   - Преобразует модель Tariff в TariffType enum
   - Используется для активации тарифа

#### Обработка ошибок:

- Проверка симулятора (строка 252)
- Проверка загрузки продуктов (строки 267-299)
- Детальное логирование для диагностики (строки 240-248)

#### Интеграция с StoreKit:

```swift
// Подписка на изменения продуктов
storeManager.$products
    .sink { [weak self] products in
        self?.updateTariffs(from: products)
    }
    .store(in: &cancellables)

// Подписка на изменения покупок
storeManager.$purchasedProductIDs
    .sink { [weak self] _ in
        self?.updatePurchaseStatus()
    }
    .store(in: &cancellables)
```

---

### 3. TariffManager (Business Layer)

**Файл:** `Core/Managers/TariffManager.swift`  
**Строки:** 1-157  
**Ответственность:** Управление текущим тарифом и активация защиты

#### Паттерн: Singleton

```swift
@MainActor
class TariffManager: ObservableObject {
    static let shared = TariffManager()
    
    @Published var currentTariff: TariffType = .free
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
}
```

#### Ключевые методы:

1. **saveTariff(_:)** (строки 98-106)
   - Сохраняет тариф в UserDefaults
   - Автоматически активирует функции защиты через ProtectionSettingsManager
   - Логирует активацию

2. **observeTariffChanges()** (строки 36-64)
   - Подписывается на уведомления о покупке тарифа
   - Обрабатывает события:
     - `tariffPurchased` - покупка через IAP
     - `paymentQRSuccess` - успешная QR оплата

3. **isCategoryAvailable(_:)** (строки 111-113)
   - Проверяет доступность категории защиты для текущего тарифа
   - Делегирует проверку в ProtectionSettingsManager

4. **getNextAvailableTariff(for:)** (строки 135-145)
   - Определяет минимальный тариф для доступа к категории
   - Используется для предложения апгрейда

#### Интеграция с ProtectionSettingsManager:

```swift
// При сохранении тарифа автоматически включаются функции
func saveTariff(_ tariffType: TariffType) {
    currentTariff = tariffType
    userDefaults.set(tariffType.rawValue, forKey: tariffKey)
    
    // ✅ АВТОМАТИЧЕСКАЯ АКТИВАЦИЯ
    protectionSettingsManager.enableForTariff(tariffType)
}
```

---

### 4. StoreManager (Business Layer)

**Файл:** `Core/Store/StoreManager.swift`  
**Строки:** 1-566  
**Ответственность:** Управление покупками через StoreKit 2

#### Структура:

```swift
@MainActor
class StoreManager: ObservableObject {
    @Published var products: [Product] = []
    @Published var purchasedProductIDs: Set<String> = []
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
}
```

#### Product IDs:

```swift
enum ProductID: String, CaseIterable {
    case basic = "family.aladdin.ios.subscription.basic.v2"
    case individual = "family.aladdin.ios.subscription.individual.v2"
    case family = "family.aladdin.ios.subscription.family"
    case premium = "family.aladdin.ios.subscription.premium"
    
    static var paidSubscriptions: [ProductID] {
        return [.individual, .family, .premium]
    }
}
```

#### Ключевые методы:

1. **loadProducts()** (строки 117-223)
   - Загружает продукты из App Store через `Product.products(for:)`
   - Обрабатывает ошибки StoreKit
   - Детальное логирование для диагностики

2. **purchase(_:)** (строки 230-400)
   - Выполняет покупку через StoreKit 2
   - Проверяет транзакцию на подлинность
   - Обновляет список купленных продуктов
   - Завершает транзакцию после успешной покупки

3. **updatePurchasedProducts()** (строки 428-446)
   - Проверяет активные подписки через `Transaction.currentEntitlements`
   - Обновляет `purchasedProductIDs`

4. **listenForTransactions()** (строки 453-464)
   - Слушает обновления транзакций через `Transaction.updates`
   - Автоматически обновляет статус покупок

#### Обработка ошибок StoreKit:

```swift
// Специфические ошибки StoreKit
if nsError.domain == "SKErrorDomain" {
    switch nsError.code {
    case 0: // SKErrorUnknown
    case 1: // SKErrorClientInvalid
    case 2: // SKErrorPaymentCancelled
    case 3: // SKErrorPaymentInvalid
    case 4: // SKErrorPaymentNotAllowed
    case 5: // SKErrorStoreProductNotAvailable
    // ...
    }
}
```

---

### 5. ProtectionSettingsManager (Business Layer)

**Файл:** `Core/Managers/ProtectionSettingsManager.swift`  
**Ответственность:** Управление настройками защиты и автоматическая активация

#### Ключевой метод:

```swift
func enableForTariff(_ tariffType: TariffType) {
    var updated = false
    
    ThreatProtectionCategory.allCases.forEach { category in
        // Проверяем доступность категории для тарифа
        if isCategoryAvailable(category, in: tariffType) {
            // Включаем категорию, если она ещё не включена
            if !settings.isEnabled(category) {
                settings.setEnabled(category, true)
                updated = true
            }
        }
    }
    
    if updated {
        saveSettings()
    }
}
```

#### Логика доступности:

```swift
func isCategoryAvailable(_ category: ThreatProtectionCategory, in tariffType: TariffType) -> Bool {
    let requiredTariff = category.requiredTariff
    return tariffLevel(tariffType) >= tariffLevel(requiredTariff)
}

private func tariffLevel(_ tariffType: TariffType) -> Int {
    switch tariffType {
    case .free: return 0
    case .personal: return 1
    case .family: return 2
    case .premium: return 3
    }
}
```

---

### 6. TariffCard (Model)

**Файл:** `Shared/Models/TariffCard.swift`  
**Строки:** 1-121  
**Ответственность:** Модель карточки тарифа с функциями

#### Структура:

```swift
struct TariffCard: Identifiable {
    let id: String
    let tariffType: TariffType
    let price: String
    let devices: String
    let icon: String
    
    // Вычисляемые свойства:
    var protectionFeatures: [ThreatProtectionCategory]
    var parentalControlFeatures: [ParentalControlFeature]
    var additionalFeatures: [AdditionalFeature]
    var protectionCount: Int
    var parentalControlCount: Int
    var totalFeatures: Int
    var protectionPercentage: Int
    var parentalControlPercentage: Int
}
```

---

### 7. TariffCardView (Component)

**Файл:** `Components/TariffCardView.swift`  
**Строки:** 1-260  
**Ответственность:** UI компонент карточки тарифа с раскрытием

#### Особенности:

- Трехуровневое раскрытие:
  1. Заголовок карточки (всегда видимый)
  2. Секции (защита, родительский контроль, дополнительные функции)
  3. Детали категорий/модулей

- Анимации:
  - Spring анимации для раскрытия
  - Haptic feedback при взаимодействии

---

### 8. TariffFeaturesGallery (Component)

**Файл:** `Components/TariffFeaturesGallery.swift`  
**Строки:** 1-61  
**Ответственность:** Галерея карточек тарифов с функциями

#### Структура:

```swift
struct TariffFeaturesGallery: View {
    private var tariffCards: [TariffCard] {
        [
            TariffType.free.createCard(...),
            TariffType.personal.createCard(...),
            TariffType.family.createCard(...),
            TariffType.premium.createCard(...)
        ]
    }
}
```

---

## 🔄 ПОТОКИ ДАННЫХ

### 1. Поток загрузки тарифов

```
User открывает TariffsScreen
    ↓
TariffsScreen.task вызывается
    ↓
TariffsViewModel.loadProducts()
    ↓
StoreManager.loadProducts()
    ↓
Product.products(for: productIDs) [StoreKit 2]
    ↓
StoreManager.products обновляется (@Published)
    ↓
TariffsViewModel.updateTariffs(from: products)
    ↓
TariffsViewModel.tariffs обновляется (@Published)
    ↓
TariffsScreen перерисовывается
```

### 2. Поток покупки тарифа (IAP)

```
User нажимает кнопку "Оформить подписку"
    ↓
TariffsScreen.tariffCard() → Button action
    ↓
Проверка региона (AppConfig.useAlternativePayments)
    ↓ (если не Россия)
TariffsViewModel.purchaseSelectedTariff(tariff:)
    ↓
Проверка валидности тарифа
    ↓
StoreManager.purchase(product)
    ↓
product.purchase() [StoreKit 2]
    ↓
Transaction verification
    ↓
StoreManager.updatePurchasedProducts()
    ↓
TariffManager.shared.saveTariff(tariffType)
    ↓
ProtectionSettingsManager.enableForTariff(tariffType)
    ↓
NotificationCenter.post("tariffPurchased")
    ↓
UI обновляется (isPurchaseSuccessful = true)
```

### 3. Поток покупки тарифа (QR для России)

```
User нажимает кнопку "Оформить подписку"
    ↓
TariffsScreen.tariffCard() → Button action
    ↓
Проверка региона (AppConfig.useAlternativePayments)
    ↓ (если Россия)
URLHelper.openWebsite(urlString, tariffId, referralCode)
    ↓
Открывается Safari с сайтом оплаты
    ↓
User оплачивает на сайте
    ↓
User получает код активации
    ↓
User вводит код в ActivationCodeScreen
    ↓
APIService.activateSubscriptionCode(code:)
    ↓
Backend активирует подписку
    ↓
NotificationCenter.post("paymentQRSuccess")
    ↓
TariffManager.observeTariffChanges() получает уведомление
    ↓
TariffManager.saveTariff(tariffType)
    ↓
ProtectionSettingsManager.enableForTariff(tariffType)
```

### 4. Поток автоматической активации защиты

```
TariffManager.saveTariff(tariffType)
    ↓
ProtectionSettingsManager.enableForTariff(tariffType)
    ↓
Для каждой ThreatProtectionCategory:
    ├─ Проверка isCategoryAvailable(category, in: tariffType)
    ├─ Если доступна → settings.setEnabled(category, true)
    └─ Обновление флага updated = true
    ↓
Если updated == true:
    └─ ProtectionSettingsManager.saveSettings()
    ↓
Настройки сохранены в UserDefaults
    ↓
UI автоматически обновляется через @Published
```

---

## 🔗 ИНТЕГРАЦИИ

### 1. Интеграция с StoreKit 2

**Цель:** Загрузка и покупка подписок через App Store

**Компоненты:**
- `StoreManager` - обертка над StoreKit 2
- `TariffsViewModel` - использует StoreManager для покупок

**Product IDs:**
- `family.aladdin.ios.subscription.individual.v2`
- `family.aladdin.ios.subscription.family`
- `family.aladdin.ios.subscription.premium`

**Особенности:**
- Поддержка только платных подписок (без basic)
- Автоматическая проверка транзакций
- Слушатель обновлений транзакций

### 2. Интеграция с Backend API

**Endpoints:**
- `/api/subscription/activation/verify` - проверка кода активации
- `/api/subscription/activation/activate` - активация кода

**Компоненты:**
- `APIService.activateSubscriptionCode(code:)`
- `ActivationCodeViewModel`

**Использование:**
- Только для России (QR оплата)
- После оплаты на сайте пользователь получает код
- Код активируется через API

### 3. Интеграция с NavigationManager

**Цель:** Навигация между экранами

**Использование:**
```swift
// Открытие экрана тарифов
navigationManager.navigateTo(.tariffs)

// Открытие экрана активации кода
navigationManager.navigateTo(.activationCode)
```

### 4. Интеграция с LocalizationManager

**Цель:** Многоязычность

**Использование:**
```swift
localizationManager.localized("tariffs_title")
localizationManager.localized("tariffs_free")
localizationManager.localized("tariffs_personal")
// ... и т.д.
```

**Поддерживаемые языки:**
- Русский (ru)
- Английский (en)

### 5. Интеграция с NotificationManager

**Цель:** Планирование уведомлений о подписке

**Использование:**
```swift
// После успешной покупки
if let endDate = calculateSubscriptionEndDate() {
    NotificationManager.shared.scheduleRenewalNotifications(
        subscriptionEndDate: endDate
    )
}
```

---

## 📱 СЦЕНАРИИ ИСПОЛЬЗОВАНИЯ

### Сценарий 1: Просмотр тарифов

**Шаги:**
1. User открывает приложение
2. User нажимает на карточку "Тарифы" на главном экране
3. Открывается `TariffsScreen`
4. Загружаются продукты из App Store (если не Россия)
5. Отображаются 4 карточки тарифов
6. User может просмотреть детали каждого тарифа

**Компоненты:**
- `MainScreen` → `TariffsScreen`
- `TariffsViewModel.loadProducts()`
- `StoreManager.loadProducts()`

### Сценарий 2: Покупка тарифа через IAP (не Россия)

**Шаги:**
1. User выбирает тариф (например, Family)
2. Нажимает "Оформить подписку"
3. Проверка региона → не Россия
4. Вызывается `TariffsViewModel.purchaseSelectedTariff()`
5. Вызывается `StoreManager.purchase(product)`
6. Открывается системный диалог App Store
7. User подтверждает покупку
8. StoreKit обрабатывает транзакцию
9. `TariffManager.saveTariff(.family)`
10. `ProtectionSettingsManager.enableForTariff(.family)`
11. Функции защиты автоматически активируются
12. Показывается сообщение об успехе

**Компоненты:**
- `TariffsScreen` → `TariffsViewModel` → `StoreManager` → StoreKit 2
- `TariffManager` → `ProtectionSettingsManager`

### Сценарий 3: Покупка тарифа через QR (Россия)

**Шаги:**
1. User выбирает тариф
2. Нажимает "Оформить подписку"
3. Проверка региона → Россия
4. Открывается Safari с сайтом оплаты
5. User оплачивает на сайте
6. User получает код активации
7. User возвращается в приложение
8. Нажимает "Активировать код" на экране тарифов
9. Открывается `ActivationCodeScreen`
10. User вводит код
11. Вызывается `APIService.activateSubscriptionCode(code:)`
12. Backend проверяет и активирует код
13. `NotificationCenter.post("paymentQRSuccess")`
14. `TariffManager` получает уведомление
15. `TariffManager.saveTariff(tariffType)`
16. Функции защиты активируются

**Компоненты:**
- `TariffsScreen` → Safari → `ActivationCodeScreen` → `APIService`
- `NotificationCenter` → `TariffManager` → `ProtectionSettingsManager`

### Сценарий 4: Автоматическая активация защиты

**Шаги:**
1. User покупает тариф (любым способом)
2. `TariffManager.saveTariff(tariffType)` вызывается
3. `ProtectionSettingsManager.enableForTariff(tariffType)` вызывается
4. Для каждой категории защиты:
   - Проверяется доступность для тарифа
   - Если доступна → включается автоматически
5. Настройки сохраняются
6. UI обновляется автоматически

**Компоненты:**
- `TariffManager` → `ProtectionSettingsManager`
- `ThreatProtectionCategory.allCases`

### Сценарий 5: Восстановление покупок

**Шаги:**
1. User нажимает "Восстановить покупки" (если есть такая кнопка)
2. Вызывается `TariffsViewModel.restorePurchases()`
3. Вызывается `StoreManager.restorePurchases()`
4. `AppStore.sync()` синхронизирует покупки
5. `StoreManager.updatePurchasedProducts()` обновляет список
6. `TariffsViewModel.updatePurchaseStatus()` обновляет UI

**Компоненты:**
- `TariffsViewModel` → `StoreManager` → StoreKit 2

---

## 🔧 ТЕХНИЧЕСКИЕ ДЕТАЛИ

### 1. Региональная логика оплаты

**Файл:** `Core/Config/AppConfig.swift` (строки 274-296)

```swift
static var isRussianRegion: Bool {
    return Locale.current.regionCode == "RU"
}

static var useAlternativePayments: Bool {
    return isRussianRegion
}

static var useIAP: Bool {
    return !isRussianRegion
}
```

**Использование:**
- Россия → QR оплата через сайт
- Остальные страны → IAP через App Store

### 2. Хранение данных

**UserDefaults:**
- `selected_tariff_type` - выбранный тариф
- `current_tariff_type` - текущий активный тариф
- `hasFreeTariffActivated` - статус бесплатного тарифа

**Keychain:**
- Не используется для тарифов (только для токенов)

### 3. Реактивность (Combine)

**Подписки в TariffsViewModel:**
```swift
// Подписка на изменения продуктов
storeManager.$products
    .sink { [weak self] products in
        self?.updateTariffs(from: products)
    }
    .store(in: &cancellables)

// Подписка на изменения покупок
storeManager.$purchasedProductIDs
    .sink { [weak self] _ in
        self?.updatePurchaseStatus()
    }
    .store(in: &cancellables)
```

**Подписки в TariffManager:**
```swift
// Подписка на уведомления о покупке
NotificationCenter.default.addObserver(
    forName: Notification.Name("tariffPurchased"),
    ...
)

NotificationCenter.default.addObserver(
    forName: Notification.Name("paymentQRSuccess"),
    ...
)
```

### 4. Обработка ошибок

**Уровни обработки:**

1. **UI уровень (TariffsScreen):**
   - Показ алертов с ошибками
   - Показ алертов с успехом

2. **ViewModel уровень (TariffsViewModel):**
   - Проверка валидности тарифа
   - Проверка загрузки продуктов
   - Проверка симулятора
   - Детальное логирование

3. **StoreManager уровень:**
   - Обработка ошибок StoreKit
   - Специфические сообщения для каждого типа ошибки

### 5. Логирование

**Уровни логирования:**
- `print()` для консоли (DEBUG режим)
- Детальные логи для диагностики:
  - Информация об устройстве
  - Информация о продуктах
  - Информация об ошибках

**Пример:**
```swift
print("🔄 [TariffsViewModel] ========== ЗАПУСК IAP ПОКУПКИ ==========")
print("🌍 [TariffsViewModel] Тариф: \(tariff.title) (ID: \(tariff.id))")
print("🌍 [TariffsViewModel] Device: \(UIDevice.current.model)")
print("🌍 [TariffsViewModel] OS: \(UIDevice.current.systemVersion)")
```

### 6. Маппинг тарифов

**TariffType → ProductID:**
```swift
let mapping: [String: StoreManager.ProductID] = [
    "free": .basic,
    "personal": .individual,
    "family": .family,
    "premium": .premium
]
```

**Tariff → TariffType:**
```swift
private func mapTariffToTariffType(_ tariff: Tariff) -> TariffType? {
    // Проверка по ID
    // Проверка по названию
    // Проверка по ProductID
}
```

---

## 📊 ДИАГРАММЫ ВЗАИМОДЕЙСТВИЯ

### Диаграмма последовательности: Покупка через IAP

```
User    TariffsScreen    TariffsViewModel    StoreManager    StoreKit    TariffManager    ProtectionSettingsManager
 │            │                 │                  │            │              │                      │
 │──tap──────>│                 │                  │            │              │                      │
 │            │──purchase───────>│                  │            │              │                      │
 │            │                 │──purchase───────>│            │              │                      │
 │            │                 │                  │──purchase─>│              │                      │
 │            │                 │                  │            │──dialog──────>│                      │
 │            │                 │                  │            │<──confirm──────│                      │
 │            │                 │                  │<──success──│              │                      │
 │            │                 │<──transaction────│            │              │                      │
 │            │                 │──saveTariff──────┼────────────┼──────────────>│                      │
 │            │                 │                  │            │              │──enableForTariff─────>│
 │            │                 │                  │            │              │                      │──enable categories
 │            │                 │                  │            │              │<──success────────────│
 │            │<──success───────│                  │            │              │                      │
 │<──alert────│                 │                  │            │              │                      │
```

### Диаграмма последовательности: Покупка через QR (Россия)

```
User    TariffsScreen    Safari    ActivationCodeScreen    APIService    Backend    TariffManager    ProtectionSettingsManager
 │            │            │              │                    │            │              │                      │
 │──tap──────>│            │              │                    │            │              │                      │
 │            │──open──────>│            │                    │            │              │                      │
 │            │            │──payment───>│                    │            │              │                      │
 │            │            │<──code──────│                    │            │              │                      │
 │            │<──return───│            │                    │            │              │                      │
 │            │──activate──>│            │                    │            │              │                      │
 │            │            │            │──activateCode──────>│            │              │                      │
 │            │            │            │                    │──verify────>│              │                      │
 │            │            │            │                    │<──valid─────│              │                      │
 │            │            │            │                    │──activate──>│              │                      │
 │            │            │            │                    │<──success───│              │                      │
 │            │            │            │<──success──────────│            │              │                      │
 │            │            │            │──post notification─┼────────────┼──────────────>│                      │
 │            │            │            │                    │            │              │──saveTariff─────────>│
 │            │            │            │                    │            │              │                      │──enableForTariff
 │            │            │            │                    │            │              │<──success─────────────│
 │<──success──│            │            │                    │            │              │                      │
```

### Диаграмма классов (упрощенная)

```
┌─────────────────────┐
│   TariffsScreen     │
│   (SwiftUI View)    │
└──────────┬──────────┘
           │ uses
           ▼
┌─────────────────────┐
│  TariffsViewModel   │
│  (ObservableObject) │
└──────────┬──────────┘
           │ uses
           ├─────────────────┐
           ▼                 ▼
┌─────────────────────┐  ┌─────────────────────┐
│   StoreManager      │  │  TariffManager      │
│  (StoreKit wrapper) │  │    (Singleton)      │
└──────────┬──────────┘  └──────────┬──────────┘
           │                        │ uses
           │                        ▼
           │              ┌─────────────────────┐
           │              │ProtectionSettings   │
           │              │     Manager         │
           │              └─────────────────────┘
           │
           ▼
┌─────────────────────┐
│    StoreKit 2        │
│   (Apple Framework)  │
└─────────────────────┘
```

---

## 🎯 КЛЮЧЕВЫЕ ОСОБЕННОСТИ

### 1. Автоматическая активация защиты

При покупке тарифа функции защиты активируются автоматически через цепочку:
```
Покупка → TariffManager.saveTariff() → ProtectionSettingsManager.enableForTariff()
```

### 2. Региональная логика оплаты

- **Россия:** QR оплата через сайт → код активации
- **Остальные страны:** IAP через App Store

### 3. Реактивность

Использование Combine для автоматического обновления UI при изменении:
- Списка продуктов
- Статуса покупок
- Текущего тарифа

### 4. Детальное логирование

Логирование на всех уровнях для диагностики проблем:
- Информация об устройстве
- Информация о продуктах
- Детали ошибок StoreKit

### 5. Обработка ошибок

Многоуровневая обработка ошибок:
- Проверка валидности данных
- Проверка доступности StoreKit
- Специфические сообщения для пользователя

---

## 📝 ЗАКЛЮЧЕНИЕ

Страница тарифов в приложении ALADDIN iOS представляет собой сложную систему с четкой архитектурой MVVM, интегрированную с StoreKit 2 для покупок, Backend API для активации кодов, и автоматической активацией функций защиты.

**Сильные стороны:**
- ✅ Четкое разделение ответственности
- ✅ Реактивность через Combine
- ✅ Автоматическая активация защиты
- ✅ Региональная логика оплаты
- ✅ Детальное логирование

**Возможные улучшения:**
- Добавить unit тесты для ViewModel
- Добавить интеграционные тесты для StoreManager
- Улучшить обработку edge cases
- Добавить аналитику покупок

---

**Автор анализа:** AI Assistant  
**Дата:** 2025-01-22  
**Версия документа:** 1.0
