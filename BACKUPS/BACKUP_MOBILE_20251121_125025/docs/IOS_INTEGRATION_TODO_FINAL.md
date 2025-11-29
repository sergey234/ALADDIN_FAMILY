# ✅ ФИНАЛЬНЫЙ СПИСОК: Что нужно сделать для интеграции оплаты в iOS

**Дата:** 17 ноября 2025  
**Статус:** Проверено по факту

---

## ✅ ЧТО УЖЕ ГОТОВО (70%)

1. ✅ **PaymentQRScreen** - скрыт в App Store билде (`#if !APP_STORE_BUILD`)
2. ✅ **NavigationManager** - paymentQR скрыт в App Store билде
3. ✅ **LocalizationManager** - все строки для активации кода есть
4. ✅ **ActivationCodeScreen** - экран существует и работает
5. ✅ **URLHelper** - открывает сайт с тарифом
6. ✅ **TariffsScreen** - кнопка "Оформить на сайте" работает
7. ✅ **Backend API** - эндпоинты `/api/activation/verify` и `/api/activation/activate` готовы

---

## ❌ ЧТО НУЖНО СДЕЛАТЬ (30% - 1-2 часа)

### Задача 1: Добавить эндпоинты в AppConfig ✅

**Файл:** `Core/Config/AppConfig.swift`

**Место:** В enum `Endpoint` (около строки 152)

**Добавить:**
```swift
// Subscription
static let tariffs = "/subscription/tariffs"
static let subscribe = "/subscription/subscribe"
static let activateSubscription = "/subscription/activate-code"  // Старый (можно оставить для совместимости)

// Activation (новые эндпоинты)
static let activationVerify = "/api/activation/verify"
static let activationActivate = "/api/activation/activate"
```

---

### Задача 2: Добавить модели в APIModels ✅

**Файл:** `Core/Models/APIModels.swift`

**Место:** После существующих моделей активации (около строки 331)

**Добавить:**
```swift
// MARK: - Activation Code Models (новые для payment_service)

// Запрос на проверку кода
struct ActivationVerifyRequest: Codable {
    let code: String
    let familyId: String
    let deviceId: String
}

// Ответ на проверку кода
struct ActivationVerifyResponse: Codable {
    let tariffId: String
    let status: String  // "pending", "active", "redeemed", "expired"
    let expiresAt: String  // ISO 8601 format
}

// Запрос на активацию кода
struct ActivationActivateRequest: Codable {
    let code: String
    let familyId: String
    let deviceId: String
}

// Ответ на активацию кода
struct ActivationActivateResponse: Codable {
    let success: Bool
    let tariffId: String
    let expiresAt: String  // ISO 8601 format
}
```

**Примечание:** Старые модели `ActivationCodeRequest` и `ActivationCodeResponse` можно оставить для совместимости, но они не используются новым backend.

---

### Задача 3: Добавить методы в APIService ✅

**Файл:** `Core/Network/APIService.swift`

**Место:** После метода `activateSubscriptionCode` (около строки 160)

**Добавить:**
```swift
// MARK: - Activation Code API (новые методы для payment_service)

/// Проверка кода активации перед активацией
func verifyActivationCode(code: String, familyId: String, deviceId: String, completion: @escaping (Result<ActivationVerifyResponse, Error>) -> Void) {
    let request = ActivationVerifyRequest(code: code, familyId: familyId, deviceId: deviceId)
    networkManager.post(endpoint: AppConfig.Endpoint.activationVerify, body: request, completion: completion)
}

/// Активация кода
func activateCode(code: String, familyId: String, deviceId: String, completion: @escaping (Result<ActivationActivateResponse, Error>) -> Void) {
    let request = ActivationActivateRequest(code: code, familyId: familyId, deviceId: deviceId)
    networkManager.post(endpoint: AppConfig.Endpoint.activationActivate, body: request, completion: completion)
}
```

---

### Задача 4: Обновить ActivationCodeViewModel ✅

**Файл:** `ViewModels/ActivationCodeViewModel.swift`

**Изменить метод `activateCode()`:**

**Было:**
```swift
func activateCode() {
    // ... валидация ...
    apiService.activateSubscriptionCode(code: trimmedCode) { ... }
}
```

**Должно быть:**
```swift
func activateCode() {
    let trimmedCode = code.trimmingCharacters(in: .whitespacesAndNewlines)
    guard !trimmedCode.isEmpty else {
        errorMessage = "Введите код активации"
        successMessage = nil
        return
    }
    
    errorMessage = nil
    successMessage = nil
    isLoading = true
    
    // Получаем deviceId и familyId
    let deviceId = UIDevice.current.identifierForVendor?.uuidString ?? "unknown"
    let familyId = UserDefaults.standard.string(forKey: "family_id") ?? ""
    
    // 1. Сначала проверить код
    apiService.verifyActivationCode(code: trimmedCode, familyId: familyId, deviceId: deviceId) { [weak self] verifyResult in
        guard let self = self else { return }
        
        switch verifyResult {
        case .success(let verifyResponse):
            // Проверяем статус кода
            if verifyResponse.status == "redeemed" {
                DispatchQueue.main.async {
                    self.isLoading = false
                    self.errorMessage = "Этот код уже был активирован"
                }
                return
            }
            
            if verifyResponse.status == "expired" {
                DispatchQueue.main.async {
                    self.isLoading = false
                    self.errorMessage = "Срок действия кода истёк"
                }
                return
            }
            
            // Код валидный, активируем
            self.apiService.activateCode(
                code: trimmedCode,
                familyId: familyId,
                deviceId: deviceId
            ) { activateResult in
                DispatchQueue.main.async {
                    self.isLoading = false
                    
                    switch activateResult {
                    case .success(let activateResponse):
                        if activateResponse.success {
                            self.successMessage = "Подписка успешно активирована"
                            self.activatedPlanName = activateResponse.tariffId
                            
                            // Форматируем дату истечения
                            let formatter = ISO8601DateFormatter()
                            if let date = formatter.date(from: activateResponse.expiresAt) {
                                let displayFormatter = DateFormatter()
                                displayFormatter.dateStyle = .medium
                                displayFormatter.timeStyle = .none
                                self.activationExpiration = displayFormatter.string(from: date)
                            } else {
                                self.activationExpiration = activateResponse.expiresAt
                            }
                        } else {
                            self.errorMessage = "Не удалось активировать код"
                        }
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
}
```

---

## 📋 ЧЕКЛИСТ ВЫПОЛНЕНИЯ

- [ ] **Задача 1:** Добавить эндпоинты в `AppConfig.swift`
- [ ] **Задача 2:** Добавить модели в `APIModels.swift`
- [ ] **Задача 3:** Добавить методы в `APIService.swift`
- [ ] **Задача 4:** Обновить `ActivationCodeViewModel.swift`
- [ ] **Тест:** Проверить активацию кода в приложении
- [ ] **Тест:** Проверить обработку ошибок (код уже активирован, код истёк)

---

## ⏱️ ОЦЕНКА ВРЕМЕНИ

**Время на выполнение:** 1-2 часа

**Разбивка:**
- Задача 1: 5 минут
- Задача 2: 10 минут
- Задача 3: 10 минут
- Задача 4: 30-45 минут
- Тестирование: 30-45 минут

---

## 🎯 ИТОГ

**Готово:** 70% ✅
- PaymentQRScreen скрыт
- NavigationManager скрыт
- Все строки локализации есть
- Backend API готов

**Осталось:** 30% (1-2 часа) ❌
- 4 задачи по коду
- Тестирование

**Вывод:** Большая часть работы уже сделана! Осталось только подключить новый backend API.

---

## 📝 ПРИМЕЧАНИЯ

1. **Старый метод `activateSubscriptionCode`** можно оставить для совместимости, но он не будет использоваться новым backend.

2. **familyId** - если у пользователя нет семьи, можно использовать пустую строку или "default". Backend должен обработать это.

3. **deviceId** - используется `UIDevice.current.identifierForVendor?.uuidString` для уникальной идентификации устройства.

4. **Формат кода:** `ALDN-XXXX-XXXX-XXXX` (12 символов, формат проверяется на backend).

5. **Обработка ошибок:** Нужно обработать случаи:
   - Код не найден
   - Код уже активирован
   - Код истёк
   - Сетевые ошибки


