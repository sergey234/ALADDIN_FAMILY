# ✅ ОТЧЁТ ОБ ИСПРАВЛЕНИЯХ BUILD 121 - SUBSCRIPTION MODELS

**Дата:** 2026-03-16  
**Цель:** Исправление ошибок декодирования subscription models для корректной работы регистрации устройства и автообновления токенов.

---

## 🎯 ВЫПОЛНЕННЫЕ ИСПРАВЛЕНИЯ

### ✅ Исправление #1: DeviceRegistrationSubscription

**Проблема:**
- `isActive` было обязательным полем, но сервер может не включать его в JSON (если default)
- Отсутствовало поле `limits`
- Не было маппинга snake_case → camelCase

**Решение:**
- ✅ Добавлены `CodingKeys` для маппинга `is_active` → `isActive`
- ✅ `isActive` теперь имеет default значение `true` если отсутствует в JSON
- ✅ Добавлено поле `limits: SubscriptionLimits?` (опционально)
- ✅ Добавлены поля `startDate`, `permissions`, `deviceId`, `userId` для совместимости
- ✅ Добавлен кастомный `init(from:)` для обработки отсутствующих полей

**Код:**
```swift
struct DeviceRegistrationSubscription: Codable {
    let level: String
    let startDate: String?
    let expiresAt: String?
    let isActive: Bool  // default = true
    let trialInfo: TrialInfo?
    let limits: SubscriptionLimits?  // ✅ Добавлено
    // ...
    
    enum CodingKeys: String, CodingKey {
        case level
        case startDate = "start_date"
        case expiresAt = "end_date"
        case isActive = "is_active"  // ✅ Маппинг
        case trialInfo = "trial_info"
        case limits
        // ...
    }
    
    init(from decoder: Decoder) throws {
        // ...
        isActive = try container.decodeIfPresent(Bool.self, forKey: .isActive) ?? true  // ✅ Default
        limits = try container.decodeIfPresent(SubscriptionLimits.self, forKey: .limits)
        // ...
    }
}
```

---

### ✅ Исправление #2: TrialInfo

**Проблема:**
- Сервер отправляет ISO 8601 строки (`start_date`, `end_date`), но клиент ожидал `Date`
- Не было маппинга snake_case → camelCase
- `durationDays` мог отсутствовать в JSON

**Решение:**
- ✅ Добавлены `CodingKeys` для маппинга `start_date` → `startDate`, `end_date` → `endDate`
- ✅ Добавлен кастомный `init(from:)` для парсинга ISO 8601 строк в `Date`
- ✅ Поддержка fractional seconds и fallback без них
- ✅ `durationDays` имеет default значение `14` если отсутствует

**Код:**
```swift
struct TrialInfo: Codable, Equatable {
    let startDate: Date
    let endDate: Date
    let durationDays: Int
    
    enum CodingKeys: String, CodingKey {
        case startDate = "start_date"
        case endDate = "end_date"
        case durationDays = "duration_days"
    }
    
    init(from decoder: Decoder) throws {
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        
        let startDateString = try container.decode(String.self, forKey: .startDate)
        guard let startDateParsed = formatter.date(from: startDateString) else {
            // Fallback без fractional seconds
            // ...
        }
        // ...
        durationDays = try container.decodeIfPresent(Int.self, forKey: .durationDays) ?? 14
    }
}
```

---

### ✅ Исправление #3: SubscriptionLimits

**Проблема:**
- Не было маппинга snake_case → camelCase (`max_devices` → `maxDevices`)
- `currentUsage` мог отсутствовать в JSON

**Решение:**
- ✅ Добавлены `CodingKeys` для всех полей (snake_case → camelCase)
- ✅ Добавлен кастомный `init(from:)` для обработки отсутствующих полей
- ✅ `currentUsage` имеет default значение `UsageCounters()` если отсутствует
- ✅ Добавлен обычный инициализатор для создания вручную

**Код:**
```swift
struct SubscriptionLimits: Codable, Equatable {
    let maxDevices: Int
    let maxAIMessages: Int
    let maxScans: Int
    let maxReports: Int
    var currentUsage: UsageCounters
    
    enum CodingKeys: String, CodingKey {
        case maxDevices = "max_devices"
        case maxAIMessages = "max_ai_messages"
        case maxScans = "max_scans"
        case maxReports = "max_reports"
        case currentUsage = "current_usage"
    }
    
    init(from decoder: Decoder) throws {
        // ...
        currentUsage = try container.decodeIfPresent(UsageCounters.self, forKey: .currentUsage) ?? UsageCounters()
    }
}
```

---

### ✅ Исправление #4: UsageCounters

**Проблема:**
- Не было маппинга `ai_messages` → `aiMessages`
- Поля могли отсутствовать в JSON

**Решение:**
- ✅ Добавлены `CodingKeys` для маппинга `ai_messages` → `aiMessages`
- ✅ Добавлен кастомный `init(from:)` для обработки отсутствующих полей
- ✅ Все поля имеют default значение `0` если отсутствуют
- ✅ Добавлен обычный инициализатор для создания вручную

**Код:**
```swift
struct UsageCounters: Codable, Equatable {
    var aiMessages: Int
    var scans: Int
    var reports: Int
    var devices: Int
    
    enum CodingKeys: String, CodingKey {
        case aiMessages = "ai_messages"
        case scans
        case reports
        case devices
    }
    
    init(from decoder: Decoder) throws {
        aiMessages = try container.decodeIfPresent(Int.self, forKey: .aiMessages) ?? 0
        scans = try container.decodeIfPresent(Int.self, forKey: .scans) ?? 0
        reports = try container.decodeIfPresent(Int.self, forKey: .reports) ?? 0
        devices = try container.decodeIfPresent(Int.self, forKey: .devices) ?? 0
    }
}
```

---

### ✅ Исправление #5: toSubscriptionStatus()

**Проблема:**
- Метод всегда использовал `SubscriptionLimits.freeLimits` вместо `limits` из ответа сервера

**Решение:**
- ✅ Обновлён метод `toSubscriptionStatus()` для использования `limits` из ответа
- ✅ Fallback на `SubscriptionLimits.freeLimits` если `limits` отсутствует
- ✅ Улучшен парсинг ISO дат с поддержкой fractional seconds

**Код:**
```swift
extension DeviceRegistrationSubscription {
    func toSubscriptionStatus() -> SubscriptionStatus {
        return SubscriptionStatus(
            level: SubscriptionLevel(rawValue: level) ?? .free,
            isActive: isActive,
            expiresAt: parseISODate(expiresAt),
            trialInfo: trialInfo,
            limits: limits ?? SubscriptionLimits.freeLimits,  // ✅ Используем limits из ответа
            components: [],
            lastUpdated: Date()
        )
    }
}
```

---

## 📊 РЕЗУЛЬТАТЫ

### ✅ Компиляция
- **Статус:** ✅ УСПЕШНО
- **Ошибки:** 0
- **Предупреждения:** Только существующие warnings (не связанные с нашими изменениями)

### ✅ Изменённые файлы
1. `Core/Models/SubscriptionModels.swift`
   - `DeviceRegistrationSubscription` - полностью переработан
   - `TrialInfo` - добавлены CodingKeys и кастомный init
   - `SubscriptionLimits` - добавлены CodingKeys и кастомный init
   - `UsageCounters` - добавлены CodingKeys и кастомный init
   - `toSubscriptionStatus()` - обновлён для использования limits из ответа

---

## 🔍 ТЕСТИРОВАНИЕ

### Сценарий #1: Первый запуск (нет токена)

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

### Сценарий #2: Токен истёк

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

### Сценарий #3: AnalyticsViewModel видит токен

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

## 📝 СЛЕДУЮЩИЕ ШАГИ

### TODO (Осталось выполнить):

1. ✅ Исправить DeviceRegistrationSubscription - **ВЫПОЛНЕНО**
2. ✅ Добавить поле limits - **ВЫПОЛНЕНО**
3. ✅ Исправить TrialInfo - **ВЫПОЛНЕНО**
4. ✅ Исправить SubscriptionLimits - **ВЫПОЛНЕНО**
5. ✅ Исправить UsageCounters - **ВЫПОЛНЕНО**
6. ✅ Проверить компиляцию - **ВЫПОЛНЕНО**
7. ⏳ Проверить что токен сохраняется в AppConfig.authToken после регистрации
8. ⏳ Проверить что токен сохраняется в SubscriptionManager.currentToken
9. ⏳ Проверить что AnalyticsViewModel видит токен после регистрации
10. ⏳ Протестировать сценарий: первый запуск (нет токена) → регистрация → токен установлен
11. ⏳ Протестировать сценарий: токен истёк → очистка → регистрация → новый токен установлен

---

## 🎉 ЗАКЛЮЧЕНИЕ

Все критические исправления моделей выполнены успешно. Проект компилируется без ошибок. Готово к тестированию всех сценариев регистрации устройства и проверки токена в AnalyticsViewModel.

**Статус:** ✅ ГОТОВО К ТЕСТИРОВАНИЮ
