# 📋 ПЛАН: Бесплатное приложение + Активация на сайте

## 🎯 Цель
Сделать приложение полностью бесплатным в App Store, убрав все экраны оплаты. Оплата и оформление подписки происходят на сайте, в приложении только активация уже оплаченного доступа.

---

## ✅ Почему это безопасно для App Store

1. **Соответствует правилам Apple**: В приложении нет продажи цифрового контента
2. **Нет комиссии Apple**: Оплата происходит на сайте, не через App Store
3. **Низкий риск отклонения**: Многие приложения используют этот подход
4. **Гибкость**: Можно использовать любые способы оплаты на сайте (QR, СБП, карты)

---

## 📝 ПОДРОБНЫЙ ПЛАН РЕАЛИЗАЦИИ

### ЭТАП 1: Подготовка конфигурации

#### Шаг 1.1: Добавить URL сайта в AppConfig
**Файл:** `Core/Config/AppConfig.swift`

**Что добавить:**
```swift
// MARK: - Website Configuration

/**
 * URL сайта для оформления подписки
 * Пользователи переходят на этот сайт для оплаты
 */
static let subscriptionWebsiteURL: String = "https://aladdin.family/subscribe"

/**
 * URL сайта для активации кода подписки
 * Пользователи могут активировать уже оплаченный код
 */
static let activationWebsiteURL: String = "https://aladdin.family/activate"
```

**Где вставить:**
- После секции `// MARK: - Support Configuration`
- Перед секцией `// MARK: - Consent Configuration`

**Что это даёт:**
- Централизованное хранение URL сайта
- Легко изменить URL в одном месте
- Можно использовать в разных экранах

---

### ЭТАП 2: Создать функцию открытия Safari

#### Шаг 2.1: Создать helper-функцию для открытия ссылок
**Файл:** `Core/Helpers/URLHelper.swift` (новый файл)

**Что создать:**
```swift
import SwiftUI
import SafariServices

struct URLHelper {
    /**
     * Открыть URL в Safari
     * @param urlString - строка с URL (например, "https://aladdin.family/subscribe")
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

**Что это даёт:**
- Удобная функция для открытия ссылок
- Автоматическое добавление параметров (например, ID тарифа)
- Обработка ошибок

---

### ЭТАП 3: Обновить локализацию

#### Шаг 3.1: Добавить новые ключи локализации
**Файл:** `Core/Localization/LocalizationManager.swift`

**Что добавить в RU секцию:**
```swift
// Тарифы - новые тексты для ссылок на сайт
"tariffs_subscribe_on_website": "Оформить на сайте",
"tariffs_subscribe_on_website_description": "Оплата и оформление подписки происходит на нашем сайте",
"tariffs_website_button": "Перейти на сайт",
"tariffs_activation_code": "Активировать код",
"tariffs_activation_code_description": "У вас уже есть код подписки? Активируйте его здесь",
"tariffs_website_info": "💡 Оплата происходит на сайте aladdin.family\nПосле оплаты вы получите код активации",
```

**Что добавить в EN секцию:**
```swift
// Tariffs - new texts for website links
"tariffs_subscribe_on_website": "Subscribe on website",
"tariffs_subscribe_on_website_description": "Payment and subscription setup happens on our website",
"tariffs_website_button": "Go to website",
"tariffs_activation_code": "Activate code",
"tariffs_activation_code_description": "Already have a subscription code? Activate it here",
"tariffs_website_info": "💡 Payment happens on aladdin.family website\nAfter payment you'll receive an activation code",
```

**Где вставить:**
- В секции с тарифами (рядом с `"tariffs_pay_qr"`)

---

### ЭТАП 4: Изменить экран тарифов

#### Шаг 4.1: Заменить кнопки оплаты на ссылки на сайт
**Файл:** `Screens/10_TariffsScreen.swift`

**Что изменить:**

**БЫЛО (строки ~477-509):**
```swift
if AppConfig.useAlternativePayments {
    // Открывает PaymentQRScreen
    navigationManager.navigateTo(.paymentQR)
} else {
    // Использует IAP
    await viewModel.purchaseSelectedTariff(tariff: localTariffObj)
}
```

**ДОЛЖНО БЫТЬ:**
```swift
// ✅ ВСЕГДА открываем сайт для оплаты (безопасно для App Store)
// В приложении нет продажи цифрового контента - только ссылка на сайт
let websiteURL = AppConfig.subscriptionWebsiteURL
URLHelper.openWebsite(urlString: websiteURL, tariffId: tariffObj.id)
```

**Что это даёт:**
- Убираем QR оплату из приложения
- Убираем IAP из приложения
- Только ссылка на сайт (безопасно для App Store)

---

#### Шаг 4.2: Изменить текст кнопки
**Файл:** `Screens/10_TariffsScreen.swift`

**БЫЛО (строка ~232):**
```swift
return localizationManager.localized("tariffs_pay_qr")
```

**ДОЛЖНО БЫТЬ:**
```swift
return localizationManager.localized("tariffs_subscribe_on_website")
```

---

#### Шаг 4.3: Добавить информационный блок
**Файл:** `Screens/10_TariffsScreen.swift`

**Где добавить:**
- После списка тарифов, перед кнопками

**Что добавить:**
```swift
// Информационный блок о том, что оплата на сайте
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
```

---

### ЭТАП 5: Добавить экран активации кода

#### Шаг 5.1: Создать экран активации кода
**Файл:** `Screens/26_ActivationCodeScreen.swift` (новый файл)

**Что создать:**
- Экран с полем ввода кода активации
- Кнопка "Активировать"
- Ссылка "Оформить подписку на сайте" (если кода нет)
- Интеграция с API для проверки и активации кода

**Основные элементы:**
1. Поле ввода кода (TextField)
2. Кнопка "Активировать"
3. Кнопка "Оформить на сайте" (открывает Safari)
4. Информационный текст

**Логика:**
- Пользователь вводит код → отправляем на сервер → активируем подписку
- Если кода нет → кнопка "Оформить на сайте"

---

#### Шаг 5.2: Добавить в навигацию
**Файл:** `Core/Navigation/NavigationManager.swift`

**Что добавить:**
- В enum `ALADDINScreen`: `case activationCode = "26_ActivationCodeScreen"`
- В switch для отображения экранов

---

### ЭТАП 6: Обновить главный экран

#### Шаг 6.1: Добавить кнопку активации кода
**Файл:** `Screens/01_MainScreen.swift`

**Где добавить:**
- В настройках или в профиле
- Или в меню тарифов

**Что добавить:**
- Кнопка "Активировать код подписки"
- При нажатии → открывается `ActivationCodeScreen`

---

### ЭТАП 7: Убрать/скрыть PaymentQRScreen

#### Шаг 7.1: Скрыть PaymentQRScreen из навигации
**Файл:** `Core/Navigation/NavigationManager.swift`

**Вариант 1: Полностью убрать (если не нужен для Android)**
- Удалить `case paymentQR` из enum
- Удалить все упоминания

**Вариант 2: Оставить, но скрыть (если нужен для Android/RuStore)**
- Оставить код, но не использовать в iOS билде
- Можно использовать флаг `#if !APP_STORE_BUILD`

---

#### Шаг 7.2: Убрать навигацию на PaymentQR
**Файл:** `Screens/10_TariffsScreen.swift`

**Что убрать:**
- Все строки с `navigationManager.navigateTo(.paymentQR)`
- Заменить на открытие сайта

---

### ЭТАП 8: Обновить API для активации кода

#### Шаг 8.1: Добавить метод активации кода
**Файл:** `Core/Network/APIService.swift`

**Что добавить:**
```swift
/**
 * Активировать код подписки
 * @param code - код активации, полученный после оплаты на сайте
 */
func activateSubscriptionCode(code: String, completion: @escaping (Result<ActivationResponse, Error>) -> Void)
```

**Что это даёт:**
- Проверка кода на сервере
- Активация подписки
- Возврат информации о подписке

---

### ЭТАП 9: Обновить Terms of Service

#### Шаг 9.1: Обновить текст о платежах
**Файл:** `Core/Localization/LocalizationManager.swift`

**Что изменить:**
- Убрать упоминания о QR оплате в приложении
- Добавить информацию о том, что оплата на сайте
- Объяснить процесс: оплата на сайте → получение кода → активация в приложении

---

## 🔄 ПОЛНЫЙ FLOW (Как это работает)

### Сценарий 1: Новый пользователь хочет подписку

1. **Пользователь открывает приложение** → видит экран тарифов
2. **Выбирает тариф** → нажимает "Оформить на сайте"
3. **Открывается Safari** → переходит на `https://aladdin.family/subscribe?tariff=premium`
4. **На сайте:**
   - Регистрация/вход
   - Выбор способа оплаты (QR, СБП, карта)
   - Оплата
   - Получение кода активации
5. **Возвращается в приложение** → вводит код → активирует подписку

### Сценарий 2: Пользователь уже оплатил на сайте

1. **Пользователь открывает приложение**
2. **Переходит в "Активировать код"** (из меню или тарифов)
3. **Вводит код**, полученный на сайте
4. **Нажимает "Активировать"** → код проверяется на сервере
5. **Подписка активируется** → пользователь получает доступ

---

## 📍 ГДЕ ЧТО НАХОДИТСЯ

### Файлы для изменения:

1. **`Core/Config/AppConfig.swift`**
   - Добавить URL сайта

2. **`Core/Helpers/URLHelper.swift`** (новый файл)
   - Функция открытия Safari

3. **`Core/Localization/LocalizationManager.swift`**
   - Новые тексты для кнопок и описаний

4. **`Screens/10_TariffsScreen.swift`**
   - Заменить кнопки оплаты на ссылки
   - Добавить информационный блок

5. **`Screens/26_ActivationCodeScreen.swift`** (новый файл)
   - Экран активации кода

6. **`Core/Navigation/NavigationManager.swift`**
   - Добавить экран активации
   - Убрать/скрыть PaymentQR

7. **`Core/Network/APIService.swift`**
   - Метод активации кода

8. **`Screens/01_MainScreen.swift`** (опционально)
   - Кнопка активации кода

---

## ⚠️ ВАЖНЫЕ МОМЕНТЫ

### 1. URL сайта
- **Где взять:** У тебя должен быть сайт `aladdin.family`
- **Что должно быть на сайте:**
  - Страница оформления подписки (`/subscribe`)
  - Страница активации кода (`/activate`)
  - Приём оплаты (QR, СБП, карты)
  - Генерация кода активации после оплаты

### 2. Код активации
- **Формат:** Может быть любой (например, `ALADDIN-XXXX-XXXX-XXXX`)
- **Где генерируется:** На сайте после оплаты
- **Где проверяется:** На сервере через API
- **Где активируется:** В приложении через `ActivationCodeScreen`

### 3. Безопасность
- Код должен быть уникальным
- Код должен проверяться на сервере (не в приложении)
- Код должен быть привязан к тарифу и сроку действия

### 4. UX (Пользовательский опыт)
- Понятные инструкции: "Оплата на сайте, затем активируйте код"
- Простой процесс активации: ввод кода → активация
- Обратная связь: показывать статус активации

---

## ✅ ЧЕКЛИСТ ПЕРЕД РЕАЛИЗАЦИЕЙ

- [ ] Есть сайт `aladdin.family` с оплатой
- [ ] На сайте есть страница `/subscribe` для оформления подписки
- [ ] На сайте есть страница `/activate` для активации кода (опционально)
- [ ] На сайте реализована генерация кода после оплаты
- [ ] На сервере есть API для проверки и активации кода
- [ ] Понятно, какой формат кода будет использоваться

---

## 🎯 РЕЗУЛЬТАТ

После реализации:
- ✅ Приложение полностью бесплатное в App Store
- ✅ Нет экранов оплаты в приложении
- ✅ Только ссылки на сайт (безопасно для Apple)
- ✅ Активация кода в приложении
- ✅ Нет комиссии Apple
- ✅ Низкий риск отклонения

---

## 📞 ВОПРОСЫ ДЛЯ УТОЧНЕНИЯ

1. **URL сайта:** Какой точный URL будет использоваться?
   - `https://aladdin.family/subscribe`?
   - Или другой?

2. **Формат кода:** Какой формат кода активации?
   - `ALADDIN-XXXX-XXXX-XXXX`?
   - Или другой?

3. **API:** Есть ли уже API для активации кода?
   - Если нет, нужно будет создать

4. **Сайт:** Готов ли сайт с оплатой?
   - Если нет, нужно будет создать

---

## 🚀 ГОТОВ К РЕАЛИЗАЦИИ

После того, как ты подтвердишь:
- URL сайта
- Формат кода
- Готовность API и сайта

Я начну реализацию по этому плану! 🎯



