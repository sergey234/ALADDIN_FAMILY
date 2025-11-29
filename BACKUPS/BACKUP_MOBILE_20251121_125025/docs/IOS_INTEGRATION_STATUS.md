# 📱 Статус интеграции оплаты в iOS приложение

**Дата:** 17 ноября 2025  
**Статус:** ⚠️ Частично готово (70%), требуется доработка

---

## ❓ Что значит "iOS приложение (0% — не начато)"?

Это означает, что **основная функциональность уже есть**, но нужно:
1. **Проверить** и **исправить** существующий код
2. **Подключить** к новому backend API (который мы только что создали)
3. **Скрыть** старый экран оплаты QR в App Store билде
4. **Добавить** недостающие строки локализации

---

## ✅ ЧТО УЖЕ ЕСТЬ (70% готово)

### 1. ActivationCodeScreen.swift ✅
**Файл:** `Screens/26_ActivationCodeScreen.swift`

**Что есть:**
- ✅ Экран для ввода кода активации
- ✅ Поле ввода кода
- ✅ Кнопка "Активировать"
- ✅ Отображение успеха/ошибки
- ✅ Кнопка "Оформить на сайте"

**Что нужно проверить:**
- ⚠️ Использует ли правильные API эндпоинты?

### 2. ActivationCodeViewModel.swift ✅
**Файл:** `ViewModels/ActivationCodeViewModel.swift`

**Что есть:**
- ✅ ViewModel для логики активации
- ✅ Вызов API через `APIService.activateSubscriptionCode()`

**Что нужно исправить:**
- ⚠️ Использует старый метод `activateSubscriptionCode()`
- ⚠️ Нужно использовать новые эндпоинты:
  - `/api/activation/verify` - проверка кода
  - `/api/activation/activate` - активация кода

### 3. URLHelper.swift ✅
**Файл:** `Core/Helpers/URLHelper.swift`

**Что есть:**
- ✅ Функция `openWebsite(urlString:tariffId:)`
- ✅ Открывает Safari с передачей `tariffId` в URL

**Статус:** ✅ **ГОТОВО** - ничего менять не нужно!

### 4. TariffsScreen.swift ✅
**Файл:** `Screens/10_TariffsScreen.swift`

**Что есть:**
- ✅ Кнопка "Оформить на сайте" для `APP_STORE_BUILD`
- ✅ Вызов `URLHelper.openWebsite()` с `tariffId`

**Статус:** ✅ **ГОТОВО** - работает правильно!

### 5. AppConfig.swift ✅
**Файл:** `Core/Config/AppConfig.swift`

**Что есть:**
- ✅ `subscriptionWebsiteURL = "https://aladdin.family/subscribe"`
- ✅ `activationWebsiteURL = "https://aladdin.family/activate"`

**Статус:** ✅ **ГОТОВО** - URL настроены!

### 6. NavigationManager.swift ✅
**Файл:** `Core/Navigation/NavigationManager.swift`

**Что есть:**
- ✅ `case activationCode = "26_ActivationCodeScreen"`

**Статус:** ✅ **ГОТОВО** - навигация настроена!

---

## ⚠️ ЧТО НУЖНО ИСПРАВИТЬ (30% осталось)

### 1. ActivationCodeViewModel - подключить новый API ⚠️

**Проблема:**
Сейчас используется старый метод `APIService.activateSubscriptionCode()`, который может не работать с новым backend.

**Что нужно сделать:**
1. Проверить, есть ли в `APIService.swift` методы:
   - `verifyActivationCode(code:completion:)` → `/api/activation/verify`
   - `activateCode(code:deviceId:familyId:completion:)` → `/api/activation/activate`

2. Если нет - добавить эти методы в `APIService.swift`

3. Обновить `ActivationCodeViewModel.swift`:
   ```swift
   // Вместо:
   apiService.activateSubscriptionCode(code: trimmedCode) { ... }
   
   // Использовать:
   // 1. Сначала проверить код
   apiService.verifyActivationCode(code: trimmedCode) { [weak self] result in
       // 2. Если код валидный - активировать
       apiService.activateCode(code: trimmedCode, deviceId: ..., familyId: ...) { ... }
   }
   ```

### 2. PaymentQRScreen - скрыть в App Store билде ⚠️

**Файл:** `Screens/25_PaymentQRScreen.swift`

**Что нужно сделать:**
Обернуть весь файл в `#if !APP_STORE_BUILD`:

```swift
#if !APP_STORE_BUILD
// Весь код PaymentQRScreen.swift
#endif
```

**Почему:**
Apple не разрешает QR оплату в App Store билде (Guideline 3.1.1). Нужно скрыть этот экран, но оставить для Android/RuStore.

### 3. NavigationManager - скрыть paymentQR ⚠️

**Файл:** `Core/Navigation/NavigationManager.swift`

**Что нужно сделать:**
Обернуть `case paymentQR` в `#if !APP_STORE_BUILD`:

```swift
#if !APP_STORE_BUILD
case paymentQR = "25_PaymentQRScreen"
#endif
```

### 4. ALADDINApp.swift - скрыть переходы к paymentQR ⚠️

**Файл:** `ALADDINApp.swift`

**Что нужно сделать:**
Найти все места, где используется `.paymentQR`, и обернуть в `#if !APP_STORE_BUILD`.

### 5. LocalizationManager - добавить строки ⚠️

**Файл:** `Core/Localization/LocalizationManager.swift`

**Что нужно проверить:**
Есть ли все эти строки:
- `tariffs_subscribe_on_website` ✅ (уже есть)
- `tariffs_website_info` ✅ (уже есть)
- `activation_code_title` ✅ (нужно проверить)
- `activation_code_subtitle` ✅ (нужно проверить)
- `activation_code_placeholder` ✅ (нужно проверить)
- `activation_code_button` ✅ (нужно проверить)
- `activation_code_instruction_title` ✅ (нужно проверить)
- `activation_code_instruction_body` ✅ (уже есть)
- `activation_code_help_title` ✅ (нужно проверить)
- `activation_code_help_step_1` ✅ (нужно проверить)
- `activation_code_help_step_2` ✅ (нужно проверить)
- `activation_code_help_step_3` ✅ (нужно проверить)

### 6. APIService - добавить новые методы ⚠️

**Файл:** `Core/Network/APIService.swift`

**Что нужно добавить:**

```swift
// Проверка кода активации
func verifyActivationCode(code: String, completion: @escaping (Result<ActivationCodeVerifyResponse, Error>) -> Void) {
    let endpoint = "/activation/verify"
    let body: [String: Any] = [
        "code": code
    ]
    // ... реализация
}

// Активация кода
func activateCode(code: String, deviceId: String, familyId: String?, completion: @escaping (Result<ActivationCodeActivateResponse, Error>) -> Void) {
    let endpoint = "/activation/activate"
    let body: [String: Any] = [
        "code": code,
        "deviceId": deviceId,
        "familyId": familyId ?? ""
    ]
    // ... реализация
}
```

---

## 📋 ЧЕКЛИСТ ИСПРАВЛЕНИЙ

### Приоритет 1 (Критично для работы):
- [ ] **APIService.swift** - добавить методы `verifyActivationCode()` и `activateCode()`
- [ ] **ActivationCodeViewModel.swift** - использовать новые методы API
- [ ] **PaymentQRScreen.swift** - обернуть в `#if !APP_STORE_BUILD`

### Приоритет 2 (Важно для App Store):
- [ ] **NavigationManager.swift** - скрыть `case paymentQR`
- [ ] **ALADDINApp.swift** - скрыть переходы к `.paymentQR`
- [ ] **LocalizationManager.swift** - проверить все строки активации

### Приоритет 3 (Проверка):
- [ ] Протестировать активацию кода
- [ ] Протестировать открытие сайта из приложения
- [ ] Проверить, что PaymentQRScreen скрыт в App Store билде

---

## 🎯 ИТОГО

**Готово:** 70%
- ✅ ActivationCodeScreen существует
- ✅ URLHelper работает
- ✅ TariffsScreen открывает сайт
- ✅ AppConfig настроен
- ✅ NavigationManager настроен

**Осталось:** 30%
- ⚠️ Подключить новый API (verify + activate)
- ⚠️ Скрыть PaymentQRScreen в App Store билде
- ⚠️ Проверить строки локализации

**Время на исправление:** ~2-3 часа

---

## 📝 ПРИМЕР ИСПРАВЛЕНИЯ ActivationCodeViewModel

**Было:**
```swift
apiService.activateSubscriptionCode(code: trimmedCode) { ... }
```

**Должно быть:**
```swift
// 1. Сначала проверить код
apiService.verifyActivationCode(code: trimmedCode) { [weak self] result in
    guard let self = self else { return }
    
    switch result {
    case .success(let verifyResponse):
        // Код валидный, можно активировать
        let deviceId = UIDevice.current.identifierForVendor?.uuidString ?? "unknown"
        let familyId = UserDefaults.standard.string(forKey: "family_id")
        
        self.apiService.activateCode(
            code: trimmedCode,
            deviceId: deviceId,
            familyId: familyId
        ) { activateResult in
            DispatchQueue.main.async {
                self.isLoading = false
                switch activateResult {
                case .success(let activateResponse):
                    self.successMessage = activateResponse.message ?? "Подписка активирована"
                    self.activatedPlanName = activateResponse.tariffId
                    // ...
                case .failure(let error):
                    self.errorMessage = error.localizedDescription
                }
            }
        }
        
    case .failure(let error):
        DispatchQueue.main.async {
            self.isLoading = false
            self.errorMessage = error.localizedDescription
        }
    }
}
```

---

**Вывод:** Код уже на 70% готов! Нужно только подключить новый backend API и скрыть старый экран QR оплаты. Это займёт 2-3 часа работы.


