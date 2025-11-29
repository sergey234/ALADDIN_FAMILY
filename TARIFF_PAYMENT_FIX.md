# 🔧 ИСПРАВЛЕНИЕ ЛОГИКИ ОПЛАТЫ НА СТРАНИЦЕ ТАРИФОВ

**Дата:** 29 октября 2025  
**Проблема:** При нажатии "Подключить" ничего не происходит

---

## 🚨 ПРОБЛЕМЫ

1. **Для не-российских регионов** — только `print()`, покупка не выполняется
2. **Нет обработки ошибок** при покупке IAP
3. **Нет уведомлений** пользователю о статусе покупки
4. **Не реализована** функция `purchaseSelectedTariff(tariff:)` для прямого вызова

---

## ✅ ИСПРАВЛЕНИЯ

### 1. Добавлен прямой вызов покупки

**Файл:** `Screens/10_TariffsScreen.swift`, строка 230

```swift
} else {
    // 🌍 За границей → IAP (App Store)
    print("🌍 Регион: \(Locale.current.regionCode ?? "unknown") → Запускаем IAP")
    Task {
        await viewModel.purchaseSelectedTariff(tariff: tariffObj)
    }
}
```

**Что изменилось:**
- ✅ Теперь вызывается реальная функция покупки
- ✅ Используется `Task` для асинхронного вызова
- ✅ Добавлено логирование для отладки

---

### 2. Добавлена перегрузка функции покупки

**Файл:** `ViewModels/TariffsViewModel.swift`

```swift
/**
 * Купить конкретный тариф (перегрузка для прямого вызова)
 */
func purchaseSelectedTariff(tariff: Tariff) async {
    await purchaseTariff(tariff)
}

/**
 * Основная функция покупки тарифа
 */
private func purchaseTariff(_ tariff: Tariff) async {
    // ... логика покупки
}
```

**Что добавлено:**
- ✅ Можно вызвать покупку напрямую с тарифом
- ✅ Единая функция `purchaseTariff` для всех случаев

---

### 3. Добавлен маппинг тарифов на Product IDs

```swift
/**
 * Найти ProductID для тарифа
 */
private func findProductID(for tariffId: String) -> StoreManager.ProductID? {
    let mapping: [String: StoreManager.ProductID] = [
        "free": .basic,
        "personal": .individual,
        "family": .family,
        "premium": .premium
    ]
    // ...
}
```

**Что делает:**
- ✅ Преобразует ID тарифа в Product ID App Store
- ✅ Находит соответствующий продукт в StoreKit

---

### 4. Добавлены Alert'ы для пользователя

**Файл:** `Screens/10_TariffsScreen.swift`

```swift
.alert("Ошибка оплаты", isPresented: .constant(viewModel.errorMessage != nil)) {
    Button("OK") {
        viewModel.errorMessage = nil
    }
} message: {
    if let error = viewModel.errorMessage {
        Text(error)
    }
}
.alert("Покупка успешна!", isPresented: .constant(viewModel.isPurchaseSuccessful)) {
    Button("Отлично!") {
        viewModel.isPurchaseSuccessful = false
    }
} message: {
    Text("Подписка успешно активирована!")
}
```

**Что добавлено:**
- ✅ Уведомление об ошибке покупки
- ✅ Уведомление об успешной покупке

---

## 🔄 ЛОГИКА ОПЛАТЫ ТЕПЕРЬ

### Для России (QR-оплата):
```
Пользователь нажимает "ОПЛАТИТЬ ЧЕРЕЗ QR"
    ↓
selectedTariffForPayment = tariffObj
    ↓
showPaymentQRScreen = true
    ↓
Открывается sheet с PaymentQRScreen
    ↓
Показываются QR-коды (СБП, SberPay)
    ↓
Пользователь сканирует и оплачивает
    ↓
Автоматическая проверка статуса каждые 30 сек
    ↓
При успехе → alert "Оплата успешна!"
```

### Для других регионов (IAP):
```
Пользователь нажимает "ПОДКЛЮЧИТЬ"
    ↓
Task { await viewModel.purchaseSelectedTariff(tariff: tariffObj) }
    ↓
findProductID(for: tariff.id)
    ↓
storeManager.purchase(product)
    ↓
App Store показывает диалог покупки
    ↓
При успехе → alert "Покупка успешна!"
    ↓
При ошибке → alert "Ошибка оплаты"
```

---

## 📍 ГДЕ В КОДЕ

| Что | Файл | Строка |
|-----|------|--------|
| **Кнопка оплаты** | `10_TariffsScreen.swift` | 204-233 |
| **Логика QR-оплаты** | `10_TariffsScreen.swift` | 226-229 |
| **Логика IAP** | `10_TariffsScreen.swift` | 231-233 |
| **Функция покупки** | `TariffsViewModel.swift` | 138-227 |
| **Маппинг Product IDs** | `TariffsViewModel.swift` | 195-214 |
| **Alerts** | `10_TariffsScreen.swift` | 123-140 |

---

## ✅ РЕЗУЛЬТАТ

Теперь при нажатии на кнопку тарифа:

1. **Россия:** 
   - ✅ Открывается экран с QR-кодами
   - ✅ Пользователь может оплатить через СБП/SberPay

2. **Другие регионы:**
   - ✅ Запускается покупка через App Store
   - ✅ Показывается диалог App Store
   - ✅ При успехе/ошибке показываются alerts

3. **Отладка:**
   - ✅ Добавлены print'ы для проверки работы
   - ✅ Можно отследить весь процесс в консоли

---

**Статус:** ✅ **ИСПРАВЛЕНО И ГОТОВО К ТЕСТИРОВАНИЮ!**
