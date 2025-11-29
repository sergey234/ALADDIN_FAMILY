# 🛠️ ПЛАН ИСПРАВЛЕНИЯ ТАРИФОВ - ДЕТАЛЬНАЯ ИНСТРУКЦИЯ

## 📋 ОБЩАЯ ИНФОРМАЦИЯ

**Цель:** Исправить проблему с выбором тарифов (краш/не работает)  
**Файл для изменения:** `Screens/10_TariffsScreen.swift`  
**Сложность:** Средняя  
**Время выполнения:** ~30 минут

---

## 🔧 ПОШАГОВЫЙ ПЛАН ИСПРАВЛЕНИЯ

### **ШАГ 1: Добавить защиту при создании Tariff объекта**

**Местоположение:** `Screens/10_TariffsScreen.swift`, строки 262-281

**Текущий код:**
```swift
let tariffObj: Tariff = {
    if !viewModel.tariffs.isEmpty,
       let existingTariff = viewModel.tariffs.first(where: { $0.id == tariffId }) {
        print("✅ Используем тариф из StoreKit: \(existingTariff.id)")
        return existingTariff
    } else {
        print("ℹ️ Создан новый тариф для оплаты: \(tariffId)")
        return Tariff(
            id: tariffId,
            title: tariff.title,
            price: tariff.price,
            period: tariff.period,
            features: tariff.features.isEmpty ? ["Базовая защита"] : tariff.features,
            product: nil,
            isPurchased: false
        )
    }
}()
```

**Заменить на:**
```swift
// Безопасно создаём тариф с полной проверкой
let tariffObj: Tariff = {
    // Сначала пытаемся найти существующий тариф из StoreKit
    if !viewModel.tariffs.isEmpty,
       let existingTariff = viewModel.tariffs.first(where: { $0.id == tariffId }) {
        print("✅ Используем тариф из StoreKit: \(existingTariff.id)")
        
        // Проверяем, что тариф валиден
        guard !existingTariff.id.isEmpty, !existingTariff.title.isEmpty else {
            print("⚠️ Тариф из StoreKit невалиден, создаём новый")
            // Продолжаем создание нового тарифа
        } else {
            return existingTariff
        }
    }
    
    // Создаём новый тариф для QR-оплаты (или если StoreKit тариф невалиден)
    print("ℹ️ Создан новый тариф для оплаты: \(tariffId)")
    
    // Проверяем обязательные поля перед созданием
    let safeTitle = tariff.title.isEmpty ? "Тариф \(tariffId)" : tariff.title
    let safePrice = tariff.price.isEmpty ? "0 ₽" : tariff.price
    let safePeriod = tariff.period.isEmpty ? "в месяц" : tariff.period
    let safeFeatures = tariff.features.isEmpty ? ["Базовая защита"] : tariff.features
    
    print("🔍 DEBUG: Создаём Tariff с параметрами:")
    print("   - id: \(tariffId)")
    print("   - title: \(safeTitle)")
    print("   - price: \(safePrice)")
    print("   - period: \(safePeriod)")
    print("   - features: \(safeFeatures.count) шт.")
    
    return Tariff(
        id: tariffId,
        title: safeTitle,
        price: safePrice,
        period: safePeriod,
        features: safeFeatures,
        product: nil,
        isPurchased: false
    )
}()
```

---

### **ШАГ 2: Улучшить логику открытия PaymentQRScreen**

**Местоположение:** `Screens/10_TariffsScreen.swift`, строки 284-298

**Текущий код:**
```swift
// Проверяем регион и запускаем оплату
if AppConfig.useAlternativePayments {
    // 🇷🇺 Россия → QR оплата
    print("🇷🇺 Регион: Россия → Открываем QR-оплату для тарифа: \(tariff.title)")
    // Установка на main thread (уже на нём)
    selectedTariffForPayment = tariffObj
    showPaymentQRScreen = true
} else {
    // 🌍 За границей → IAP (App Store)
    print("🌍 Регион: \(Locale.current.regionCode ?? "unknown") → Запускаем IAP для тарифа: \(tariff.title)")
    
    // Запускаем покупку асинхронно с защитой от ошибок
    Task { @MainActor in
        await viewModel.purchaseSelectedTariff(tariff: tariffObj)
    }
}
```

**Заменить на:**
```swift
// Проверяем регион и запускаем оплату
if AppConfig.useAlternativePayments {
    // 🇷🇺 Россия → QR оплата
    print("🇷🇺 Регион: Россия → Открываем QR-оплату для тарифа: \(tariff.title)")
    print("🔍 DEBUG: tariffObj проверка:")
    print("   - id: \(tariffObj.id)")
    print("   - title: \(tariffObj.title)")
    print("   - price: \(tariffObj.price)")
    
    // Проверяем, что tariffObj валиден
    guard !tariffObj.id.isEmpty, !tariffObj.title.isEmpty, !tariffObj.price.isEmpty else {
        print("❌ КРИТИЧЕСКАЯ ОШИБКА: tariffObj создан неправильно!")
        print("   id.isEmpty: \(tariffObj.id.isEmpty)")
        print("   title.isEmpty: \(tariffObj.title.isEmpty)")
        print("   price.isEmpty: \(tariffObj.price.isEmpty)")
        viewModel.errorMessage = "Ошибка создания тарифа. Попробуйте ещё раз."
        return
    }
    
    // Безопасная установка на main thread с задержкой для гарантии
    DispatchQueue.main.async { [weak self] in
        guard let self = self else {
            print("❌ self is nil при открытии sheet")
            return
        }
        
        print("✅ Устанавливаем selectedTariffForPayment и открываем sheet")
        self.selectedTariffForPayment = tariffObj
        self.showPaymentQRScreen = true
        
        // Дополнительная проверка после установки
        if self.selectedTariffForPayment == nil {
            print("❌ ОШИБКА: selectedTariffForPayment остался nil!")
            self.viewModel.errorMessage = "Не удалось выбрать тариф. Попробуйте ещё раз."
            self.showPaymentQRScreen = false
        } else {
            print("✅ selectedTariffForPayment установлен: \(self.selectedTariffForPayment!.id)")
        }
    }
} else {
    // 🌍 За границей → IAP (App Store)
    print("🌍 Регион: \(Locale.current.regionCode ?? "unknown") → Запускаем IAP для тарифа: \(tariff.title)")
    
    // Запускаем покупку асинхронно с защитой от ошибок
    Task { @MainActor in
        print("🔍 DEBUG: Запуск IAP покупки...")
        await viewModel.purchaseSelectedTariff(tariff: tariffObj)
        print("🔍 DEBUG: IAP покупка завершена")
    }
}
```

---

### **ШАГ 3: Улучшить sheet binding**

**Местоположение:** `Screens/10_TariffsScreen.swift`, строки 123-134

**Текущий код:**
```swift
.sheet(isPresented: $showPaymentQRScreen) {
    if let tariff = selectedTariffForPayment {
        PaymentQRScreen(tariff: tariff) {
            // Callback после успешной оплаты
            print("✅ Подписка успешно оплачена!")
            // Можно обновить UI или показать уведомление
        }
    } else {
        // Плейсхолдер, если тариф не выбран (не должно происходить)
        Text("Ошибка: тариф не выбран")
            .padding()
    }
}
```

**Заменить на:**
```swift
.sheet(
    isPresented: Binding(
        get: {
            let shouldShow = showPaymentQRScreen && selectedTariffForPayment != nil
            if shouldShow {
                print("✅ Sheet должен открыться с тарифом: \(selectedTariffForPayment?.id ?? "nil")")
            }
            return shouldShow
        },
        set: { newValue in
            showPaymentQRScreen = newValue
            if !newValue {
                print("🔙 Sheet закрывается")
                // Не очищаем selectedTariffForPayment сразу - PaymentQRScreen может ещё использовать
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                    selectedTariffForPayment = nil
                }
            }
        }
    )
) {
    if let tariff = selectedTariffForPayment {
        print("✅ Открываем PaymentQRScreen для тарифа: \(tariff.title)")
        PaymentQRScreen(tariff: tariff) {
            // Callback после успешной оплаты
            print("✅ Подписка успешно оплачена!")
            showPaymentQRScreen = false
            // Можно обновить UI или показать уведомление
        }
    } else {
        // Плейсхолдер, если тариф не выбран (не должно происходить)
        VStack(spacing: 20) {
            ProgressView()
                .scaleEffect(1.5)
            Text("Загрузка тарифа...")
                .font(.headline)
                .foregroundColor(.secondary)
        }
        .padding()
        .onAppear {
            print("⚠️ Sheet открыт, но selectedTariffForPayment = nil!")
            // Закрываем sheet, если тариф не загрузился за 2 секунды
            DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
                if selectedTariffForPayment == nil {
                    showPaymentQRScreen = false
                    viewModel.errorMessage = "Не удалось загрузить тариф. Попробуйте ещё раз."
                }
            }
        }
    }
}
```

---

### **ШАГ 4: Добавить расширенное логирование в начало Button action**

**Местоположение:** `Screens/10_TariffsScreen.swift`, строка 240

**Добавить в самое начало Button action (после строки 242):**

```swift
Button(action: {
    print("🔍 ========== НАЧАЛО ВЫБОРА ТАРИФА ==========")
    print("🔍 Выбран тариф: \(tariff.title)")
    print("🔍 TariffType: \(tariff)")
    print("🔍 Регион: \(Locale.current.regionCode ?? "unknown")")
    print("🔍 Locale: \(Locale.current.identifier)")
    print("🔍 AppConfig.useAlternativePayments: \(AppConfig.useAlternativePayments)")
    print("🔍 viewModel.tariffs.count: \(viewModel.tariffs.count)")
    print("🔍 viewModel.isLoading: \(viewModel.isLoading)")
    
    // Безопасная обработка выбора тарифа
    HapticFeedback.impact(.medium)
    selectedTariff = tariff
    
    // ... остальной код ...
    
    print("🔍 ========== КОНЕЦ ВЫБОРА ТАРИФА ==========")
})
```

---

## ✅ ПРОВЕРКА ПОСЛЕ ИСПРАВЛЕНИЯ

### **Тест 1: Выбор бесплатного тарифа**

**Действие:** Нажать на тариф "БАЗОВЫЙ" (бесплатный)

**Ожидаемый результат:**
- В консоли: `✅ Активирован бесплатный тариф`
- Тариф отмечен как выбранный
- Sheet НЕ открывается

### **Тест 2: Выбор платного тарифа (Россия → QR)**

**Предусловия:**
- Симулятор/устройство настроено на регион RU
- `AppConfig.useAlternativePayments == true`

**Действие:** Нажать на тариф "ЛИЧНЫЙ", "СЕМЕЙНЫЙ", или "ПРЕМИУМ"

**Ожидаемый результат:**
1. В консоли появляются логи:
   ```
   🔍 ========== НАЧАЛО ВЫБОРА ТАРИФА ==========
   🔍 Выбран тариф: ЛИЧНЫЙ
   🇷🇺 Регион: Россия → Открываем QR-оплату для тарифа: ЛИЧНЫЙ
   🔍 DEBUG: tariffObj проверка:
      - id: personal
      - title: ЛИЧНЫЙ
      - price: 290 ₽
   ✅ Устанавливаем selectedTariffForPayment и открываем sheet
   ✅ selectedTariffForPayment установлен: personal
   ✅ Sheet должен открыться с тарифом: personal
   ✅ Открываем PaymentQRScreen для тарифа: ЛИЧНЫЙ
   ```

2. Sheet открывается с PaymentQRScreen
3. PaymentQRScreen показывает QR-коды для оплаты
4. Нет крашей или ошибок

### **Тест 3: Выбор платного тарифа (Не Россия → IAP)**

**Предусловия:**
- Симулятор/устройство настроено на регион НЕ RU (например, US)
- `AppConfig.useAlternativePayments == false`

**Действие:** Нажать на тариф "ЛИЧНЫЙ", "СЕМЕЙНЫЙ", или "ПРЕМИУМ"

**Ожидаемый результат:**
1. В консоли появляются логи:
   ```
   🌍 Регион: US → Запускаем IAP для тарифа: ЛИЧНЫЙ
   🔍 DEBUG: Запуск IAP покупки...
   ```

2. Открывается системный диалог App Store для покупки
3. Нет крашей или ошибок

### **Тест 4: Проверка error handling**

**Действие:** Нажать на тариф, когда что-то идёт не так

**Ожидаемый результат:**
- Появляется alert с ошибкой (если есть)
- `viewModel.errorMessage` установлен
- Приложение не крашится

---

## 🔍 ОТЛАДКА (ЕСЛИ НЕ РАБОТАЕТ)

### **Проблема: Sheet не открывается**

**Проверка:**
1. В консоли искать: `✅ selectedTariffForPayment установлен`
2. Если этого нет - проблема в DispatchQueue.main.async
3. Проверить, что `showPaymentQRScreen` установлен в `true`

**Решение:**
```swift
// Попробовать без async (если мы уже на main thread)
selectedTariffForPayment = tariffObj
showPaymentQRScreen = true

// Или с небольшой задержкой
DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
    self.showPaymentQRScreen = true
}
```

### **Проблема: Sheet открывается, но показывает "Загрузка тарифа..."**

**Проверка:**
1. В консоли искать: `⚠️ Sheet открыт, но selectedTariffForPayment = nil!`
2. Проверить timing - возможно sheet открывается раньше, чем устанавливается tariff

**Решение:**
Увеличить задержку в DispatchQueue.main.async или использовать другой подход

### **Проблема: Краш при создании Tariff**

**Проверка:**
1. В консоли искать: `❌ КРИТИЧЕСКАЯ ОШИБКА: tariffObj создан неправильно!`
2. Проверить все поля tariff перед созданием

**Решение:**
Убедиться, что все поля tariff (title, price, period, features) заполнены

---

## 📊 ДОПОЛНИТЕЛЬНАЯ ИНФОРМАЦИЯ

### **Структура Tariff:**
```swift
struct Tariff: Identifiable {
    let id: String           // "personal", "family", "premium"
    let title: String        // "ЛИЧНЫЙ", "СЕМЕЙНЫЙ", "ПРЕМИУМ"
    let price: String        // "290 ₽", "590 ₽", "990 ₽"
    let period: String       // "в месяц"
    let features: [String]   // ["VPN Pro", "3 устройства", ...]
    let product: Product?    // nil для QR оплаты, Product для IAP
    var isPurchased: Bool   // false по умолчанию
}
```

### **Проверка региона:**
```swift
// Core/Config/AppConfig.swift
static var isRussianRegion: Bool {
    return Locale.current.regionCode == "RU"
}

static var useAlternativePayments: Bool {
    return isRussianRegion
}
```

### **Связь с другими компонентами:**
- `PaymentQRScreen` требует валидный `Tariff` объект
- `PaymentQRViewModel` создаётся с `Tariff` в init
- Все поля `Tariff` должны быть заполнены

---

## ✅ ФИНАЛЬНЫЙ ЧЕКЛИСТ

После применения всех исправлений:

- [ ] Код компилируется без ошибок
- [ ] Добавлена защита при создании Tariff
- [ ] Добавлена защита при открытии sheet
- [ ] Улучшен sheet binding
- [ ] Добавлено логирование
- [ ] Тест бесплатного тарифа работает
- [ ] Тест QR-оплаты (Россия) работает
- [ ] Тест IAP (не Россия) работает
- [ ] Нет крашей
- [ ] Ошибки обрабатываются корректно

---

**Дата создания:** 2024-10-28  
**Версия:** 1.0  
**Статус:** Готов к применению
