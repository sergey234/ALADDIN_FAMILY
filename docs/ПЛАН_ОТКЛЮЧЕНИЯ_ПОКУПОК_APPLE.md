# 📋 ПЛАН ОТКЛЮЧЕНИЯ ПОКУПОК ДЛЯ APPLE REVIEW

## 🎯 ЦЕЛЬ
Отключить все функции, связанные с подписками и покупками, **минимальными изменениями** без удаления кода.

## ✅ ПРЕИМУЩЕСТВА ПОДХОДА
- ✅ Код остается в проекте (можно быстро включить обратно)
- ✅ Минимальные изменения (только флаги и проверки)
- ✅ Легко откатить изменения
- ✅ Не ломает существующую логику

---

## 📝 ПЛАН ИЗМЕНЕНИЙ

### 1️⃣ **Добавить флаг в AppConfig.swift**

**Файл:** `Core/Config/AppConfig.swift`

**Добавить после строки 178:**
```swift
// MARK: - Feature Flags

static let isNetworkProtectionEnabled = true
static let isAIEnabled = true
static let isParentalControlEnabled = true
static let isAnalyticsEnabled = true

// ✅ НОВЫЙ ФЛАГ: Отключение покупок для Apple Review
/// Отключить все функции покупок и подписок (для соответствия требованиям Apple)
static let isPurchasesDisabled: Bool = true  // ⚠️ ИЗМЕНИТЬ НА false КОГДА НУЖНО ВКЛЮЧИТЬ ОБРАТНО
```

**Изменить существующие флаги:**
```swift
// MARK: - Payment Configuration

/**
 * Использовать IAP (In-App Purchase через App Store)
 * ✅ ОТКЛЮЧЕНО: Если isPurchasesDisabled = true, всегда возвращает false
 */
static var useIAP: Bool {
    if isPurchasesDisabled {
        return false
    }
    return !isRussianRegion
}

/**
 * Включить альтернативные способы оплаты (QR-коды)
 * ✅ ОТКЛЮЧЕНО: Если isPurchasesDisabled = true, всегда возвращает false
 */
static var useAlternativePayments: Bool {
    if isPurchasesDisabled {
        return false
    }
    return isRussianRegion
}
```

---

### 2️⃣ **Модифицировать StoreManager.swift**

**Файл:** `Core/Store/StoreManager.swift`

**Изменить метод `startLoading()` (строка 96):**
```swift
func startLoading() {
    print("🔍 StoreManager.startLoading: Начало загрузки продуктов")
    
    // ✅ ОТКЛЮЧЕНО: Если покупки отключены, не загружаем продукты
    if AppConfig.isPurchasesDisabled {
        print("⚠️ StoreManager.startLoading: Покупки отключены (isPurchasesDisabled = true)")
        return
    }
    
    // ✅ ЗАЩИТА: Проверяем симулятор перед загрузкой
    #if targetEnvironment(simulator)
    print("⚠️ StoreManager.startLoading: Симулятор - пропускаем загрузку продуктов")
    return
    #else
    Task { @MainActor in
        await loadProducts()
        await updatePurchasedProducts()
        await listenForTransactions()
    }
    #endif
}
```

**Изменить метод `purchase()` (найти метод покупки):**
```swift
func purchase(_ product: Product) async throws -> Transaction? {
    // ✅ ОТКЛЮЧЕНО: Если покупки отключены, возвращаем ошибку
    if AppConfig.isPurchasesDisabled {
        throw NSError(domain: "StoreManager", code: -1, userInfo: [NSLocalizedDescriptionKey: "Purchases are disabled"])
    }
    
    // ... остальной код ...
}
```

---

### 3️⃣ **Модифицировать TariffsScreen.swift**

**Файл:** `Screens/10_TariffsScreen.swift`

**Изменить метод `tariffCard()` - скрыть кнопки покупки (строка 290):**
```swift
// Кнопка выбора/оплаты
if AppConfig.isPurchasesDisabled {
    // ✅ ОТКЛЮЧЕНО: Показываем только бесплатный тариф
    if tariff == .free {
        Button(action: {
            HapticFeedback.impact(.medium)
            selectedTariff = tariff
            // Активируем бесплатный тариф
            if let storeManager = viewModel.storeManager {
                storeManager.activateFreeTariff()
            }
        }) {
            Text(localizationManager.localized("tariffs_free_button"))
                .font(.bodyBold)
                .foregroundColor(.backgroundDark)
                .frame(maxWidth: .infinity)
                .padding(Spacing.m)
                .background(tariff.color)
                .cornerRadius(CornerRadius.medium)
        }
    } else {
        // Скрываем платные тарифы или показываем сообщение
        VStack(spacing: Spacing.s) {
            Text(localizationManager.localized("tariffs_unavailable"))
                .font(.body)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
                .padding(Spacing.m)
        }
        .frame(maxWidth: .infinity)
        .padding(Spacing.m)
        .background(Color.surfaceDark)
        .cornerRadius(CornerRadius.medium)
    }
} else {
    // ✅ СТАРЫЙ КОД: Оставляем как есть, если покупки включены
    Button(action: {
        // ... существующий код ...
    }) {
        // ... существующий код ...
    }
}
```

**Или более простой вариант - скрыть платные тарифы полностью:**
```swift
// В body экрана, где отображаются тарифы:
VStack(spacing: Spacing.l) {
    // Всегда показываем бесплатный тариф
    tariffCard(.free)
    
    // Платные тарифы показываем только если покупки включены
    if !AppConfig.isPurchasesDisabled {
        tariffCard(.personal)
        tariffCard(.family)
        tariffCard(.premium)
    }
}
```

---

### 4️⃣ **Модифицировать TariffsViewModel.swift**

**Файл:** `ViewModels/TariffsViewModel.swift`

**Изменить метод `loadProducts()` (строка 88):**
```swift
func loadProducts() async {
    // ✅ ОТКЛЮЧЕНО: Если покупки отключены, не загружаем продукты
    if AppConfig.isPurchasesDisabled {
        print("⚠️ TariffsViewModel.loadProducts: Покупки отключены, пропускаем загрузку")
        isLoading = false
        return
    }
    
    isLoading = true
    await storeManager.loadProducts()
    isLoading = false
}
```

**Изменить метод `purchaseSelectedTariff()` (найти метод):**
```swift
func purchaseSelectedTariff(tariff: Tariff) async {
    // ✅ ОТКЛЮЧЕНО: Если покупки отключены, показываем ошибку
    if AppConfig.isPurchasesDisabled {
        let localizationManager = LocalizationManager()
        errorMessage = localizationManager.localized("tariffs_error_purchases_disabled")
        return
    }
    
    // ... остальной код ...
}
```

---

### 5️⃣ **Скрыть PaymentQRScreen (уже сделано)**

**Файл:** `Screens/25_PaymentQRScreen.swift`

✅ **УЖЕ ОБЕРНУТ В:** `#if !APP_STORE_BUILD` - это хорошо!

**Но нужно также проверить навигацию:**
- Найти все места, где открывается PaymentQRScreen
- Добавить проверку `if !AppConfig.isPurchasesDisabled`

---

### 6️⃣ **Добавить локализацию для сообщения об отключенных покупках**

**Файл:** `Core/Localization/LocalizationManager.swift`

**Добавить ключи:**
```swift
"tariffs_unavailable" = "Тариф временно недоступен";
"tariffs_error_purchases_disabled" = "Покупки временно отключены";
```

---

## 📊 ИТОГОВАЯ СТАТИСТИКА ИЗМЕНЕНИЙ

### Файлы для изменения:
1. ✅ `Core/Config/AppConfig.swift` - добавить флаг (1 изменение)
2. ✅ `Core/Store/StoreManager.swift` - добавить проверки (2-3 изменения)
3. ✅ `Screens/10_TariffsScreen.swift` - скрыть кнопки/тарифы (1-2 изменения)
4. ✅ `ViewModels/TariffsViewModel.swift` - добавить проверки (2 изменения)
5. ✅ `Core/Localization/LocalizationManager.swift` - добавить ключи (опционально)

### Всего изменений: **~8-10 строк кода**

---

## 🚀 КАК ВКЛЮЧИТЬ ОБРАТНО

Когда Apple одобрит приложение или когда нужно будет включить покупки:

1. Открыть `Core/Config/AppConfig.swift`
2. Изменить `static let isPurchasesDisabled: Bool = true` на `false`
3. Готово! Все функции покупок снова работают.

---

## ✅ ПРОВЕРКА

После изменений нужно проверить:
- ✅ Экран тарифов показывает только бесплатный тариф
- ✅ Кнопки покупки не отображаются
- ✅ StoreManager не загружает продукты из App Store
- ✅ PaymentQRScreen не открывается
- ✅ Приложение компилируется без ошибок

---

## 📝 ПРИМЕЧАНИЯ

- Все функции покупок остаются в коде
- Код не удаляется, только отключается через флаги
- Легко включить обратно одной строкой
- Минимальные изменения = минимальный риск ошибок

