# 🔄 FLOW РЕГИСТРАЦИИ УСТРОЙСТВА - ПОЛНОЕ ОПИСАНИЕ

**Дата создания:** 2026-03-16  
**Цель:** Детальное описание процесса регистрации устройства и проверки токена в приложении ALADDIN iOS.

---

## 📱 СЦЕНАРИЙ #1: ПЕРВЫЙ ЗАПУСК (НЕТ ТОКЕНА)

### Шаг 1: Запуск приложения (`ALADDINApp.init()`)

```
🚀 ALADDINApp.init() called - APP STARTING
🚀 SubscriptionManager.shared created
```

**Что происходит:**
- Создаётся `SubscriptionManager.shared` (singleton)
- В `init()` вызывается `loadPersistedData()` → загружает токен из Keychain (если есть)
- Если токена нет → `currentToken = nil`

**Код:**
```swift
// Core/Managers/SubscriptionManager.swift:init()
loadPersistedData()  // Загружает токен из Keychain
```

---

### Шаг 2: Отображение UI (`ALADDINApp.body`)

```
ALADDINApp.body → NavigationView → mainAppContent()
```

**Что происходит:**
- SwiftUI отрисовывает `NavigationView`
- Вызывается `.onAppear` на корневом View

**Код:**
```swift
// ALADDINApp.swift:324
.onAppear {
    // ...
    Task {
        await subscriptionManager.initializeOnAppStart()
    }
}
```

---

### Шаг 3: Инициализация SubscriptionManager (`initializeOnAppStart()`)

```
🚀 SubscriptionManager.initializeOnAppStart() called
📊 ИНИЦИАЛИЗАЦИЯ ПОДПИСКИ - ПРОВЕРКА ТЕКУЩЕГО СОСТОЯНИЯ
```

**Что происходит:**

1. **Проверка токена через TokenValidator:**
   ```swift
   let tokenStatus = TokenValidator.validateCurrentToken()
   // Результат: .none (токена нет)
   ```

2. **Выбор действия в зависимости от статуса:**
   ```swift
   switch tokenStatus {
   case .none:
       logger.business("📱 DEFENSIVE JWT: Токена нет - запускаем первичную регистрацию")
       await performDeviceRegistration()
   // ...
   }
   ```

**Код:**
```swift
// Core/Managers/SubscriptionManager.swift:165-226
func initializeOnAppStart() async {
    // ...
    let tokenStatus = TokenValidator.validateCurrentToken()
    switch tokenStatus {
    case .none:
        await performDeviceRegistration()
    // ...
    }
}
```

---

### Шаг 4: Регистрация устройства (`performDeviceRegistration()`)

```
📱 DEFENSIVE JWT: Выполняем регистрацию устройства
📱 DEFENSIVE JWT: Запуск registerDeviceAnonymously()...
```

**Что происходит:**

1. **Вызов `registerDeviceAnonymously()`:**
   ```swift
   try await registerDeviceAnonymously()
   ```

2. **Обработка результата:**
   - ✅ Успех → токен установлен в `currentToken`
   - ❌ Ошибка → логирование ошибки, переход в offline режим (если не 422)

**Код:**
```swift
// Core/Managers/SubscriptionManager.swift:263-321
private func performDeviceRegistration() async {
    do {
        try await registerDeviceAnonymously()
        if let token = currentToken {
            logger.business("✅ DEFENSIVE JWT: Токен успешно установлен")
        }
    } catch {
        logger.error("❌ DEFENSIVE JWT: Регистрация провалилась")
        // Обработка ошибок...
    }
}
```

---

### Шаг 5: API вызов (`registerDeviceAnonymously()`)

```
📱 НАЧАЛО РЕГИСТРАЦИИ УСТРОЙСТВА АНОНИМНО
📋 Параметры регистрации:
   - DeviceID: [UUID]
   - DeviceType: ios
📡 ВЫЗОВ API: POST /api/auth/register-device
```

**Что происходит:**

1. **Подготовка запроса:**
   ```swift
   let deviceId = UIDevice.current.identifierForVendor?.uuidString ?? UUID().uuidString
   let deviceType = "ios"
   let request = DeviceRegisterRequest(deviceId: deviceId, deviceType: deviceType)
   ```

2. **API вызов через APIService:**
   ```swift
   APIService.shared.registerDeviceAnonymously(request: request) { result in
       switch result {
       case .success(let jwtResponse):
           // ✅ Успех - декодируем ответ
       case .failure(let error):
           // ❌ Ошибка - пробрасываем дальше
       }
   }
   ```

3. **Сервер возвращает:**
   ```json
   {
     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "device_id": "12345678-1234-1234-1234-123456789012",
     "expires_at": "2026-03-17T10:25:08Z",
     "registered_at": "2026-03-16T10:25:08Z",
     "subscription": {
       "level": "free",
       "start_date": "2026-03-16T10:25:08Z",
       "end_date": null,
       "is_active": true,  // ⚠️ Может отсутствовать в JSON!
       "trial_info": null,
       "limits": {
         "max_devices": 1,
         "max_ai_messages": 10,
         "max_scans": 5,
         "max_reports": 2,
         "current_usage": {
           "ai_messages": 0,
           "scans": 0,
           "reports": 0,
           "devices": 0
         }
       },
       "permissions": {},
       "device_id": "12345678-1234-1234-1234-123456789012",
       "user_id": null
     }
   }
   ```

**Код:**
```swift
// Core/Managers/SubscriptionManager.swift:683-818
func registerDeviceAnonymously() async throws -> JWTToken {
    // ...
    let response = try await withCheckedThrowingContinuation { continuation in
        APIService.shared.registerDeviceAnonymously(request: request) { result in
            // Обработка результата...
        }
    }
    // ...
}
```

---

### Шаг 6: Декодирование ответа (❌ ПРОБЛЕМА ЗДЕСЬ!)

```
✅ РЕГИСТРАЦИЯ УСТРОЙСТВА ПРОШЛА УСПЕШНО
📋 Получен ответ от сервера:
   - Token: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   - Subscription Level: free
```

**Что происходит:**

1. **Попытка декодирования `JWTDeviceRegisterResponse`:**
   ```swift
   // Пытается декодировать JSON в структуру:
   struct JWTDeviceRegisterResponse: Codable {
       let token: String
       let deviceId: String
       let expiresAt: String
       let registeredAt: String
       let subscription: DeviceRegistrationSubscription  // ⚠️ ПРОБЛЕМА ЗДЕСЬ!
   }
   ```

2. **Попытка декодирования `DeviceRegistrationSubscription`:**
   ```swift
   struct DeviceRegistrationSubscription: Codable {
       let level: String
       let isActive: Bool  // ❌ Ожидает обязательное поле, но может отсутствовать!
       let expiresAt: String?
       let trialInfo: TrialInfo?  // ❌ Может не декодироваться из-за ISO строк!
   }
   ```

3. **ОШИБКА ДЕКОДИРОВАНИЯ:**
   ```
   DecodingError.keyNotFound(CodingKeys(stringValue: "isActive", intValue: nil), ...)
   ```

**Проблема:**
- Сервер отправляет `is_active: true` (snake_case), но может не включать поле в JSON если оно default
- Клиент ожидает `isActive: Bool` (camelCase, обязательное поле)
- Результат: `DecodingError.keyNotFound("isActive")`

**Код (текущий - с ошибкой):**
```swift
// Core/Models/SubscriptionModels.swift:364-376
struct DeviceRegistrationSubscription: Codable {
    let level: String
    let isActive: Bool  // ❌ Обязательное, но может отсутствовать в JSON
    let expiresAt: String?
    let trialInfo: TrialInfo?  // ❌ Может не декодироваться
}
```

---

### Шаг 7: Сохранение токена (НЕ ВЫПОЛНЯЕТСЯ из-за ошибки декодирования!)

```
💾 СОХРАНЕНИЕ ТОКЕНА В ЗАЩИЩЕННОЕ ХРАНИЛИЩЕ
```

**Что должно происходить (но не происходит из-за ошибки):**

1. **Создание `JWTToken` из ответа:**
   ```swift
   let jwtToken = JWTToken(
       token: response.token,
       deviceId: response.deviceId,
       subscriptionLevel: SubscriptionLevel(rawValue: response.subscription.level) ?? .free,
       // ...
   )
   ```

2. **Сохранение токена:**
   ```swift
   await storeToken(jwtToken)  // Сохраняет в Keychain и AppConfig.authToken
   await updateSubscriptionStatus(newSubscriptionStatus)  // Сохраняет подписку
   ```

3. **Результат:**
   - ✅ `AppConfig.authToken = jwtToken.token`
   - ✅ `SubscriptionManager.currentToken = jwtToken`
   - ✅ `SubscriptionManager.currentSubscription = newSubscriptionStatus`
   - ✅ Токен сохранён в Keychain

**Код (не выполняется из-за ошибки):**
```swift
// Core/Managers/SubscriptionManager.swift:770-790
logger.business("💾 СОХРАНЕНИЕ ТОКЕНА В ЗАЩИЩЕННОЕ ХРАНИЛИЩЕ")
let jwtToken = JWTToken(...)
await storeToken(jwtToken)
await updateSubscriptionStatus(newSubscriptionStatus)
```

---

### Шаг 8: Проверка токена в AnalyticsViewModel (❌ ТОКЕН НЕ НАЙДЕН!)

```
🔍 AnalyticsViewModel: Диагностика токена
   - AppConfig.authToken: ❌ нет
   - Keychain token: ❌ нет
   - SubscriptionManager token: ❌ нет
```

**Что происходит:**

1. **Проверка токена:**
   ```swift
   let tokenAvailability = TokenManager.shared.checkTokenAvailability()
   // Результат: .unavailable (токена нет)
   ```

2. **Показ ошибки:**
   ```swift
   errorMessage = "Не удалось загрузить данные аналитики. Проверьте подключение к интернету."
   isLoading = false
   dataSource = .empty
   ```

**Код:**
```swift
// ViewModels/AnalyticsViewModel.swift:58-128
@MainActor
func load() async {
    let tokenAvailability = TokenManager.shared.checkTokenAvailability()
    if tokenAvailability == .unavailable {
        errorMessage = "Не удалось загрузить данные аналитики..."
        return
    }
    // ...
}
```

---

## 📱 СЦЕНАРИЙ #2: ТОКЕН ИСТЁК

### Шаг 1: Запуск приложения

```
🚀 SubscriptionManager.initializeOnAppStart() called
```

**Что происходит:**
- `loadPersistedData()` загружает старый токен из Keychain
- `currentToken` содержит истёкший токен

---

### Шаг 2: Проверка токена (`TokenValidator.validateCurrentToken()`)

```
🔍 DEFENSIVE JWT: Статус токена: expired
```

**Что происходит:**
```swift
let tokenStatus = TokenValidator.validateCurrentToken()
// Результат: .expired (токен истёк)
```

---

### Шаг 3: Очистка токена (`clearToken()`)

```
⏰ DEFENSIVE JWT: Токен истек/невалиден - очищаем и регистрируем заново
🧹 DEFENSIVE JWT: Очищаем токен из всех хранилищ
```

**Что происходит:**

1. **Остановка мониторинга:**
   ```swift
   TokenHealthMonitor.shared.stopMonitoring()
   ```

2. **Очистка Keychain:**
   ```swift
   KeychainManager.shared.delete(forKey: .authToken)
   KeychainManager.shared.delete(forKey: .refreshToken)
   ```

3. **Очистка памяти:**
   ```swift
   currentToken = nil
   currentSubscription = nil
   ```

4. **Очистка UserDefaults:**
   ```swift
   UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.authToken)
   ```

**Код:**
```swift
// Core/Managers/SubscriptionManager.swift:348-375
func clearToken() async {
    TokenHealthMonitor.shared.stopMonitoring()
    KeychainManager.shared.delete(forKey: .authToken)
    currentToken = nil
    currentSubscription = nil
    UserDefaults.standard.removeObject(forKey: AppConfig.UserDefaultsKeys.authToken)
}
```

---

### Шаг 4: Регистрация устройства (повторяется Шаг 4-7 из Сценария #1)

```
📱 DEFENSIVE JWT: Выполняем регистрацию устройства
📱 DEFENSIVE JWT: Запуск registerDeviceAnonymously()...
```

**Что происходит:**
- Повторяется весь процесс регистрации из Сценария #1
- Если декодирование успешно → токен сохраняется
- Если декодирование проваливается → токен не сохраняется, ошибка повторяется

---

## 📱 СЦЕНАРИЙ #3: ТОКЕН ВАЛИДЕН (ИДЕАЛЬНЫЙ СЛУЧАЙ)

### Шаг 1: Запуск приложения

```
🚀 SubscriptionManager.initializeOnAppStart() called
```

**Что происходит:**
- `loadPersistedData()` загружает валидный токен из Keychain
- `currentToken` содержит валидный токен

---

### Шаг 2: Проверка токена

```
🔍 DEFENSIVE JWT: Статус токена: valid
✅ DEFENSIVE JWT: Токен валиден - используем существующий
```

**Что происходит:**
```swift
let tokenStatus = TokenValidator.validateCurrentToken()
// Результат: .valid (токен валиден)

switch tokenStatus {
case .valid:
    logger.business("✅ DEFENSIVE JWT: Токен валиден - используем существующий")
    // Ничего не делаем, токен рабочий
}
```

---

### Шаг 3: Проверка токена в AnalyticsViewModel (✅ ТОКЕН НАЙДЕН!)

```
🔍 AnalyticsViewModel: Диагностика токена
   - AppConfig.authToken: ✅ есть
   - Keychain token: ✅ есть
   - SubscriptionManager token: ✅ есть
```

**Что происходит:**

1. **Проверка токена:**
   ```swift
   let tokenAvailability = TokenManager.shared.checkTokenAvailability()
   // Результат: .available (токен найден)
   ```

2. **Загрузка данных:**
   ```swift
   async let summaryTask = service.fetchSummary(period: cachedPeriod, filters: cachedFilters)
   async let securityTask = service.fetchSecurityAnalytics(period: cachedPeriod)
   let (summaryResult, securityResult) = try await (summaryTask, securityTask)
   ```

**Код:**
```swift
// ViewModels/AnalyticsViewModel.swift:130-159
if tokenAvailability == .available {
    isLoading = true
    async let summaryTask = service.fetchSummary(...)
    async let securityTask = service.fetchSecurityAnalytics(...)
    // Загрузка данных...
}
```

---

## 🔍 ДЕТАЛЬНЫЙ FLOW ДЕКОДИРОВАНИЯ (ТЕКУЩАЯ ПРОБЛЕМА)

### Что происходит сейчас:

```
1. Сервер отправляет JSON:
   {
     "subscription": {
       "level": "free",
       "is_active": true,  // ⚠️ Может отсутствовать если default!
       "limits": { ... }   // ❌ Отсутствует в DeviceRegistrationSubscription!
     }
   }

2. Клиент пытается декодировать:
   struct DeviceRegistrationSubscription: Codable {
       let level: String
       let isActive: Bool  // ❌ Ожидает обязательное поле
       // ❌ Нет поля limits!
   }

3. ОШИБКА:
   DecodingError.keyNotFound("isActive")
   или
   DecodingError.keyNotFound("limits")
```

### Что должно происходить после исправлений:

```
1. Сервер отправляет JSON:
   {
     "subscription": {
       "level": "free",
       "is_active": true,  // Может отсутствовать
       "limits": { ... }   // Всегда присутствует
     }
   }

2. Клиент декодирует с CodingKeys:
   struct DeviceRegistrationSubscription: Codable {
       let level: String
       let isActive: Bool  // ✅ Опциональное или с default
       let limits: SubscriptionLimits?  // ✅ Добавлено
       
       enum CodingKeys: String, CodingKey {
           case level
           case isActive = "is_active"  // ✅ Маппинг snake_case
           case limits
       }
       
       init(from decoder: Decoder) throws {
           let container = try decoder.container(keyedBy: CodingKeys.self)
           level = try container.decode(String.self, forKey: .level)
           isActive = try container.decodeIfPresent(Bool.self, forKey: .isActive) ?? true  // ✅ Default
           limits = try container.decodeIfPresent(SubscriptionLimits.self, forKey: .limits)
       }
   }

3. УСПЕХ:
   ✅ Декодирование прошло успешно
   ✅ Токен сохранён в AppConfig.authToken
   ✅ AnalyticsViewModel видит токен
```

---

## 📊 ТАБЛИЦА СОСТОЯНИЙ ТОКЕНА

| Состояние | `AppConfig.authToken` | `SubscriptionManager.currentToken` | `Keychain` | `AnalyticsViewModel` |
|-----------|----------------------|-----------------------------------|------------|---------------------|
| **Первый запуск** | `nil` | `nil` | Пусто | ❌ Ошибка "Не удалось загрузить данные" |
| **После регистрации (успех)** | ✅ `"eyJ..."` | ✅ `JWTToken(...)` | ✅ Сохранён | ✅ Загружает данные |
| **После регистрации (ошибка декодирования)** | ❌ `nil` | ❌ `nil` | ❌ Пусто | ❌ Ошибка "Не удалось загрузить данные" |
| **Токен истёк** | ❌ Старый токен | ❌ Старый токен | ❌ Старый токен | ❌ Ошибка 401 |
| **После очистки** | ❌ `nil` | ❌ `nil` | ❌ Пусто | ❌ Ошибка "Не удалось загрузить данные" |
| **Токен валиден** | ✅ `"eyJ..."` | ✅ `JWTToken(...)` | ✅ Сохранён | ✅ Загружает данные |

---

## ✅ КРИТЕРИИ УСПЕХА ДЛЯ ТЕСТИРОВАНИЯ

### Тест #1: Первый запуск (нет токена)

**Ожидаемый результат:**
1. ✅ `initializeOnAppStart()` вызывается
2. ✅ `TokenValidator.validateCurrentToken()` возвращает `.none`
3. ✅ `performDeviceRegistration()` вызывается
4. ✅ `registerDeviceAnonymously()` успешно декодирует ответ
5. ✅ `storeToken()` сохраняет токен в `AppConfig.authToken`
6. ✅ `AnalyticsViewModel.load()` видит токен и загружает данные

**Логи для проверки:**
```
🚀 SubscriptionManager.initializeOnAppStart() called
📱 DEFENSIVE JWT: Токена нет - запускаем первичную регистрацию
✅ РЕГИСТРАЦИЯ УСТРОЙСТВА ПРОШЛА УСПЕШНО
✅ DEFENSIVE JWT: Токен успешно установлен после регистрации
🔍 AnalyticsViewModel: Диагностика токена
   - AppConfig.authToken: ✅ есть
```

---

### Тест #2: Токен истёк

**Ожидаемый результат:**
1. ✅ `initializeOnAppStart()` вызывается
2. ✅ `TokenValidator.validateCurrentToken()` возвращает `.expired`
3. ✅ `clearToken()` очищает все хранилища
4. ✅ `performDeviceRegistration()` вызывается
5. ✅ Новый токен успешно декодируется и сохраняется
6. ✅ `AnalyticsViewModel.load()` видит новый токен

**Логи для проверки:**
```
⏰ DEFENSIVE JWT: Токен истек/невалиден - очищаем и регистрируем заново
🧹 DEFENSIVE JWT: Очищаем токен из всех хранилищ
✅ DEFENSIVE JWT: Токен успешно установлен после регистрации
```

---

### Тест #3: AnalyticsViewModel видит токен

**Ожидаемый результат:**
1. ✅ `AnalyticsViewModel.load()` вызывается
2. ✅ `TokenManager.shared.checkTokenAvailability()` возвращает `.available`
3. ✅ `service.fetchSummary()` успешно загружает данные
4. ✅ `service.fetchSecurityAnalytics()` успешно загружает данные
5. ✅ Данные отображаются на экране

**Логи для проверки:**
```
🔍 AnalyticsViewModel: Диагностика токена
   - AppConfig.authToken: ✅ есть
   - Keychain token: ✅ есть
   - SubscriptionManager token: ✅ есть
📊 AnalyticsViewModel: Загрузка аналитики...
✅ AnalyticsViewModel: Данные загружены
```

---

## 🔧 ТЕКУЩИЕ ПРОБЛЕМЫ И РЕШЕНИЯ

### Проблема #1: Ошибка декодирования `isActive`

**Симптомы:**
- `DecodingError.keyNotFound("isActive")`
- Токен не сохраняется после регистрации
- `AnalyticsViewModel` не видит токен

**Решение:**
- Добавить `CodingKeys` с маппингом `isActive = "is_active"`
- Сделать `isActive` опциональным или с default значением `true`
- Добавить кастомный `init(from:)` для обработки отсутствующих полей

---

### Проблема #2: Отсутствие поля `limits` в `DeviceRegistrationSubscription`

**Симптомы:**
- `DecodingError.keyNotFound("limits")` (если поле обязательное)
- Или поле игнорируется (если опциональное, но не декодируется из-за snake_case)

**Решение:**
- Добавить `limits: SubscriptionLimits?` в `DeviceRegistrationSubscription`
- Добавить `CodingKeys` для `SubscriptionLimits` (snake_case → camelCase)
- Добавить кастомный `init(from:)` для `SubscriptionLimits`

---

### Проблема #3: `TrialInfo` не декодируется из ISO строк

**Симптомы:**
- `DecodingError.typeMismatch` при попытке декодировать строку как `Date`
- `trialInfo` всегда `nil` даже если сервер отправляет данные

**Решение:**
- Добавить `CodingKeys` для `TrialInfo` (`start_date` → `startDate`, `end_date` → `endDate`)
- Добавить кастомный `init(from:)` для парсинга ISO 8601 строк в `Date`

---

## 📝 ЗАМЕТКИ

- **Важно:** Все исправления должны быть обратно совместимыми
- **Тестирование:** После каждого исправления проверять все 3 сценария
- **Логирование:** Добавить детальное логирование для отладки проблем декодирования
- **Документация:** Обновить комментарии в коде с указанием соответствия серверным моделям

---

**Следующий шаг:** Реализовать исправления из `docs/ПЛАН_ИСПРАВЛЕНИЯ_SUBSCRIPTION_MODELS.md` и протестировать все 3 сценария.
