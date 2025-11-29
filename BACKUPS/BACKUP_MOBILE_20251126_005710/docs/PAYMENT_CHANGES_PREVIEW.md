# 📋 ПРЕДПРОСМОТР ВСЕХ ИЗМЕНЕНИЙ: Оплата в App Store

**Дата:** 16 ноября 2025  
**Статус:** ⚠️ ПРЕДПРОСМОТР - НЕ РЕАЛИЗОВАНО

---

## 🎯 ЛОГИКА РАБОТЫ ДЛЯ РАЗНЫХ СТРАН

### Для App Store билда:

**Все пользователи (Россия, Беларусь, Казахстан, другие страны):**
- ✅ Видят кнопку "Оформить на сайте"
- ✅ При нажатии → открывается Safari с ссылкой на сайт
- ✅ На сайте оплачивают подписку
- ✅ Получают код активации
- ✅ Возвращаются в приложение → активируют код

**IAP (In-App Purchase):**
- ❌ **НЕ показываем** в App Store билде
- ❌ **НЕ используем** для оплаты
- ✅ **Оставляем код** StoreManager (может пригодиться позже)

**Почему так:**
- ✅ Безопасно для App Store (нет продажи в приложении)
- ✅ Работает для всех стран одинаково
- ✅ Нет проблем с определением региона

---

## 📝 ВСЕ ИЗМЕНЕНИЯ В ФАЙЛАХ

### 1. `Core/Config/AppConfig.swift`

#### БЫЛО:
```swift
// MARK: - Payment Configuration

static var isRussianRegion: Bool {
    return Locale.current.regionCode == "RU"
}

static var allowAlternativePayments: Bool {
    #if APP_STORE_BUILD
    return false
    #else
    return isRussianRegion
    #endif
}

static var useIAP: Bool {
    return true
}
```

#### ДОЛЖНО БЫТЬ:
```swift
// MARK: - Payment Configuration

/**
 * Проверка региона пользователя
 * ⚠️ ВАЖНО: Используется только для логирования, не для определения способа оплаты
 */
static var isRussianRegion: Bool {
    return Locale.current.regionCode == "RU"
}

/**
 * Разрешено ли использовать альтернативные способы оплаты (QR-коды)
 * ⚠️ В App Store билде всегда false (QR оплата убрана)
 */
static var allowAlternativePayments: Bool {
    #if APP_STORE_BUILD
    return false  // ✅ В App Store билде QR оплата отключена
    #else
    return isRussianRegion  // Для других билдов (Android/RuStore)
    #endif
}

/**
 * Использовать IAP (In-App Purchase через App Store)
 * ⚠️ В App Store билде НЕ используем IAP (только ссылка на сайт)
 */
static var useIAP: Bool {
    #if APP_STORE_BUILD
    return false  // ✅ В App Store билде не используем IAP
    #else
    return true   // Для других билдов можно использовать
    #endif
}

// MARK: - Website Configuration

/**
 * URL сайта для оформления подписки
 * ⚠️ ВАЖНО: Сайт пока не готов, используем placeholder
 * После создания сайта заменить на реальный URL
 */
static let subscriptionWebsiteURL: String = "https://aladdin.family/subscribe"

/**
 * URL сайта для активации кода подписки
 * ⚠️ ВАЖНО: Сайт пока не готов, используем placeholder
 * После создания сайта заменить на реальный URL
 */
static let activationWebsiteURL: String = "https://aladdin.family/activate"
```

---

### 2. `Core/Helpers/URLHelper.swift` (НОВЫЙ ФАЙЛ)

#### СОЗДАТЬ:
```swift
import SwiftUI
import SafariServices

/**
 * Helper для открытия внешних ссылок
 */
struct URLHelper {
    /**
     * Открыть URL в Safari
     * @param urlString - строка с URL
     * @param tariffId - опциональный ID тарифа для передачи в URL
     */
    static func openWebsite(urlString: String, tariffId: String? = nil) {
        var finalURL = urlString
        
        // Если передан tariffId, добавляем его в URL как параметр
        if let tariffId = tariffId, !tariffId.isEmpty {
            let separator = urlString.contains("?") ? "&" : "?"
            finalURL = "\(urlString)\(separator)tariff=\(tariffId)"
        }
        
        guard let url = URL(string: finalURL) else {
            print("❌ Неверный URL: \(finalURL)")
            return
        }
        
        // Открываем в Safari
        UIApplication.shared.open(url)
    }
}
```

---

### 3. `Screens/10_TariffsScreen.swift`

#### ИЗМЕНЕНИЕ 1: Функция `getButtonText`

**БЫЛО:**
```swift
private func getButtonText(for tariff: TariffType) -> String {
    if tariff == .free {
        return localizationManager.localized("tariffs_free_button")
    } else if selectedTariff == tariff {
        return localizationManager.localized("tariffs_selected")
    } else {
        // ✅ ВСЕГДА используем QR оплату (IAP в России недоступен)
        return localizationManager.localized("tariffs_pay_qr")
    }
}
```

**ДОЛЖНО БЫТЬ:**
```swift
private func getButtonText(for tariff: TariffType) -> String {
    if tariff == .free {
        return localizationManager.localized("tariffs_free_button")
    } else if selectedTariff == tariff {
        return localizationManager.localized("tariffs_selected")
    } else {
        #if APP_STORE_BUILD
        // В App Store билде всегда ссылка на сайт
        return localizationManager.localized("tariffs_subscribe_on_website")
        #else
        // В других билдах (Android/RuStore) можно использовать QR
        if AppConfig.allowAlternativePayments {
            return localizationManager.localized("tariffs_pay_qr")
        } else {
            return localizationManager.localized("tariffs_buy")
        }
        #endif
    }
}
```

#### ИЗМЕНЕНИЕ 2: Логика кнопки оплаты (строки ~477-509)

**БЫЛО:**
```swift
if AppConfig.useAlternativePayments {
    guard !tariffObj.id.isEmpty,
          !tariffObj.title.isEmpty,
          !tariffObj.price.isEmpty else {
        viewModel.errorMessage = localizationManager.localized("tariffs_error_create_tariff")
        return
    }
    
    navigationManager.selectedTariffForPayment = tariffObj
    
    guard navigationManager.selectedTariffForPayment != nil else {
        viewModel.errorMessage = localizationManager.localized("tariffs_error_select_tariff")
        return
    }
    
    navigationManager.navigateTo(.paymentQR)
} else {
    guard !tariffObj.id.isEmpty,
          !tariffObj.title.isEmpty else {
        viewModel.errorMessage = localizationManager.localized("tariffs_error_purchase_tariff")
        return
    }
    
    #if targetEnvironment(simulator)
    viewModel.errorMessage = "In-App Purchase недоступен в симуляторе..."
    #else
    let localTariffObj = tariffObj
    
    Task { @MainActor in
        await viewModel.purchaseSelectedTariff(tariff: localTariffObj)
    }
    #endif
}
```

**ДОЛЖНО БЫТЬ:**
```swift
#if APP_STORE_BUILD
// ✅ В App Store билде всегда открываем сайт
guard !tariffObj.id.isEmpty,
      !tariffObj.title.isEmpty else {
    viewModel.errorMessage = localizationManager.localized("tariffs_error_select_tariff")
    return
}

// Открываем сайт в Safari
let websiteURL = AppConfig.subscriptionWebsiteURL
URLHelper.openWebsite(urlString: websiteURL, tariffId: tariffObj.id)

#else
// Для других билдов (Android/RuStore) оставляем старую логику
if AppConfig.useAlternativePayments {
    guard !tariffObj.id.isEmpty,
          !tariffObj.title.isEmpty,
          !tariffObj.price.isEmpty else {
        viewModel.errorMessage = localizationManager.localized("tariffs_error_create_tariff")
        return
    }
    
    navigationManager.selectedTariffForPayment = tariffObj
    
    guard navigationManager.selectedTariffForPayment != nil else {
        viewModel.errorMessage = localizationManager.localized("tariffs_error_select_tariff")
        return
    }
    
    navigationManager.navigateTo(.paymentQR)
} else {
    guard !tariffObj.id.isEmpty,
          !tariffObj.title.isEmpty else {
        viewModel.errorMessage = localizationManager.localized("tariffs_error_purchase_tariff")
        return
    }
    
    #if targetEnvironment(simulator)
    viewModel.errorMessage = "In-App Purchase недоступен в симуляторе..."
    #else
    let localTariffObj = tariffObj
    
    Task { @MainActor in
        await viewModel.purchaseSelectedTariff(tariff: localTariffObj)
    }
    #endif
}
#endif
```

#### ИЗМЕНЕНИЕ 3: Добавить информационный блок (после списка тарифов, перед кнопками)

**ДОБАВИТЬ:**
```swift
// Информационный блок о том, что оплата на сайте
#if APP_STORE_BUILD
VStack(spacing: Spacing.s) {
    Text(localizationManager.localized("tariffs_website_info"))
        .font(.caption)
        .foregroundColor(.textSecondary)
        .multilineTextAlignment(.center)
        .padding(Spacing.m)
        .background(
            RoundedRectangle(cornerRadius: CornerRadius.medium)
                .fill(Color.blue.opacity(0.1))
        )
}
.padding(.horizontal, Spacing.screenPadding)
.padding(.top, Spacing.s)
#endif
```

---

### 4. `Screens/25_PaymentQRScreen.swift`

#### ИЗМЕНЕНИЕ: Обернуть весь файл в `#if !APP_STORE_BUILD`

**БЫЛО:**
```swift
import SwiftUI

struct PaymentQRScreen: View {
    // ... весь код
}
```

**ДОЛЖНО БЫТЬ:**
```swift
#if !APP_STORE_BUILD
// ⚠️ ВАЖНО: PaymentQRScreen используется только для Android/RuStore
// В App Store билде этот экран не компилируется

import SwiftUI

struct PaymentQRScreen: View {
    // ... весь код без изменений
}
#endif
```

**Почему:**
- ✅ Код остается для Android/RuStore
- ✅ В App Store билде не компилируется
- ✅ Apple не увидит этот код при проверке

---

### 5. `Core/Navigation/NavigationManager.swift`

#### ИЗМЕНЕНИЕ 1: Обернуть `case paymentQR` в `#if !APP_STORE_BUILD`

**БЫЛО:**
```swift
enum ALADDINScreen: String, CaseIterable {
    // ...
    case paymentQR = "25_PaymentQRScreen"
    // ...
}
```

**ДОЛЖНО БЫТЬ:**
```swift
enum ALADDINScreen: String, CaseIterable {
    // ...
    #if !APP_STORE_BUILD
    case paymentQR = "25_PaymentQRScreen"
    #endif
    // ...
}
```

#### ИЗМЕНЕНИЕ 2: Обернуть все упоминания `paymentQR` в `#if !APP_STORE_BUILD`

**Найти и обернуть:**
- `case .paymentQR: return "Оплата QR"` (строка ~97)
- `case .paymentQR: return "qrcode"` (строка ~145)
- Все проверки `if case .paymentQR` (строки ~201, 238, 293, 326)
- `case .paymentQR` в switch (строка ~531)

---

### 6. `ALADDINApp.swift`

#### ИЗМЕНЕНИЕ: Обернуть `case .paymentQR` в `#if !APP_STORE_BUILD`

**БЫЛО:**
```swift
case .paymentQR:
    // ... весь код PaymentQRScreen
```

**ДОЛЖНО БЫТЬ:**
```swift
#if !APP_STORE_BUILD
case .paymentQR:
    // ... весь код PaymentQRScreen
#endif
```

---

### 7. `Core/Localization/LocalizationManager.swift`

#### ДОБАВИТЬ новые ключи локализации:

**RU секция:**
```swift
// Тарифы - новые тексты для ссылок на сайт
"tariffs_subscribe_on_website": "Оформить на сайте",
"tariffs_subscribe_on_website_description": "Оплата и оформление подписки происходит на нашем сайте",
"tariffs_website_button": "Перейти на сайт",
"tariffs_website_info": "💡 Оплата происходит на сайте aladdin.family\nПосле оплаты вы получите код активации в приложении",
"tariffs_activation_code": "Активировать код",
"tariffs_activation_code_description": "У вас уже есть код подписки? Активируйте его здесь",
```

**EN секция:**
```swift
// Tariffs - new texts for website links
"tariffs_subscribe_on_website": "Subscribe on website",
"tariffs_subscribe_on_website_description": "Payment and subscription setup happens on our website",
"tariffs_website_button": "Go to website",
"tariffs_website_info": "💡 Payment happens on aladdin.family website\nAfter payment you'll receive an activation code in the app",
"tariffs_activation_code": "Activate code",
"tariffs_activation_code_description": "Already have a subscription code? Activate it here",
```

**⚠️ ВАЖНО:** Убрали упоминание email, так как почту не собираем!

---

## 📋 ИТОГОВЫЙ СПИСОК ИЗМЕНЕНИЙ

### Файлы для изменения:

1. ✅ `Core/Config/AppConfig.swift`
   - Добавить URL сайта (placeholder, так как сайта пока нет)
   - Изменить `useIAP` для App Store билда

2. ✅ `Core/Helpers/URLHelper.swift` (НОВЫЙ)
   - Создать helper для открытия Safari

3. ✅ `Screens/10_TariffsScreen.swift`
   - Изменить `getButtonText`
   - Изменить логику кнопки оплаты
   - Добавить информационный блок

4. ✅ `Screens/25_PaymentQRScreen.swift`
   - Обернуть в `#if !APP_STORE_BUILD`

5. ✅ `Core/Navigation/NavigationManager.swift`
   - Обернуть `case paymentQR` в `#if !APP_STORE_BUILD`
   - Обернуть все упоминания `paymentQR`

6. ✅ `ALADDINApp.swift`
   - Обернуть `case .paymentQR` в `#if !APP_STORE_BUILD`

7. ✅ `Core/Localization/LocalizationManager.swift`
   - Добавить новые ключи локализации (БЕЗ упоминания email)

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

### 1. Сайт пока не готов:
- ✅ Используем placeholder URL: `https://aladdin.family/subscribe`
- ✅ После создания сайта заменить на реальный URL

### 2. Email не собираем:
- ✅ Убрали упоминание email из текстов
- ✅ Код активации будет приходить "в приложении" (через API/уведомления)

### 3. PaymentQRScreen:
- ✅ НЕ удаляем файл
- ✅ Обернем в `#if !APP_STORE_BUILD`
- ✅ Остается для Android/RuStore

### 4. IAP:
- ✅ В App Store билде НЕ используем
- ✅ Код StoreManager оставляем (может пригодиться позже)
- ✅ Для всех стран одинаково: ссылка на сайт

---

## 🎯 РЕЗУЛЬТАТ

После изменений:

**Для App Store билда:**
- ✅ Все пользователи видят "Оформить на сайте"
- ✅ При нажатии → открывается Safari
- ✅ Нет QR оплаты в приложении
- ✅ Нет IAP в приложении
- ✅ Безопасно для Apple

**Для других билдов (Android/RuStore):**
- ✅ Остается QR оплата (если нужно)
- ✅ Остается IAP (если нужно)
- ✅ Код не меняется

---

**Готов к реализации после подтверждения!** ✅




