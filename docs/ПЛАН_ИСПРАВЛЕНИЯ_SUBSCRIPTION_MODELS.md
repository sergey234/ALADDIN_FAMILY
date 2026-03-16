# 📋 ПЛАН ИСПРАВЛЕНИЯ SUBSCRIPTION MODELS - 100% КАЧЕСТВЕННО И НАДЁЖНО

**Дата создания:** 2026-03-16  
**Цель:** Полное выравнивание моделей subscription между сервером (Python/FastAPI) и клиентом (Swift/iOS) для устранения ошибок декодирования и обеспечения корректной работы автообновления токенов.

---

## 🔍 ТАБЛИЦА СООТВЕТСТВИЙ: SubscriptionPayload (Сервер) ↔ DeviceRegistrationSubscription (Клиент)

### Основная модель: JWTDeviceRegisterResponse

| Поле (Сервер) | Тип (Сервер) | Поле (Клиент) | Тип (Клиент) | Статус | Проблема |
|---------------|--------------|---------------|---------------|--------|----------|
| `token` | `str` | `token` | `String` | ✅ OK | - |
| `device_id` | `str` | `deviceId` | `String` | ✅ ИСПРАВЛЕНО | Было: отсутствовал CodingKeys |
| `expires_at` | `datetime` | `expiresAt` | `String` | ✅ OK | Дата как ISO 8601 строка |
| `registered_at` | `datetime` | `registeredAt` | `String` | ✅ OK | Дата как ISO 8601 строка |
| `subscription` | `SubscriptionPayload` | `subscription` | `DeviceRegistrationSubscription` | ❌ ПРОБЛЕМА | Несоответствие структуры |

---

### Вложенная модель: SubscriptionPayload → DeviceRegistrationSubscription

| Поле (Сервер) | Тип (Сервер) | Обязательность | Поле (Клиент) | Тип (Клиент) | Обязательность | Статус | Проблема |
|---------------|--------------|----------------|---------------|--------------|----------------|--------|----------|
| `level` | `SubscriptionLevel` (enum) | ✅ Обязательно | `level` | `String` | ✅ Обязательно | ✅ OK | Конвертация enum → string |
| `start_date` | `datetime` | ✅ Обязательно | ❌ ОТСУТСТВУЕТ | - | - | ⚠️ НЕТ | Не используется в клиенте |
| `end_date` | `Optional[datetime]` | ⚠️ Опционально | `expiresAt` | `String?` | ⚠️ Опционально | ⚠️ ЧАСТИЧНО | Маппинг `end_date` → `expiresAt` |
| `is_active` | `bool = True` | ⚠️ Default | `isActive` | `Bool` | ✅ Обязательно | ❌ КРИТИЧНО | **ОШИБКА: поле обязательное, но может отсутствовать в JSON** |
| `trial_info` | `Optional[TrialInfo]` | ⚠️ Опционально | `trialInfo` | `TrialInfo?` | ⚠️ Опционально | ⚠️ ПРОВЕРИТЬ | Структура TrialInfo может не совпадать |
| `limits` | `SubscriptionLimits` | ✅ Обязательно | ❌ ОТСУТСТВУЕТ | - | - | ❌ КРИТИЧНО | **ОШИБКА: поле обязательное на сервере, отсутствует в клиенте** |
| `permissions` | `Dict[str, Any] = {}` | ⚠️ Default | ❌ ОТСУТСТВУЕТ | - | - | ⚠️ OK | Не используется в клиенте |
| `device_id` | `str` | ✅ Обязательно | ❌ ОТСУТСТВУЕТ | - | - | ⚠️ OK | Дублируется в корне ответа |
| `user_id` | `Optional[str]` | ⚠️ Опционально | ❌ ОТСУТСТВУЕТ | - | - | ⚠️ OK | Не используется в клиенте |

---

### Вложенная модель: TrialInfo

| Поле (Сервер) | Тип (Сервер) | Обязательность | Поле (Клиент) | Тип (Клиент) | Обязательность | Статус | Проблема |
|---------------|--------------|----------------|---------------|--------------|----------------|--------|----------|
| `start_date` | `datetime` | ✅ Обязательно | `startDate` | `Date` | ✅ Обязательно | ❌ КРИТИЧНО | **ОШИБКА: сервер → ISO string, клиент → Date (нужен парсинг)** |
| `end_date` | `datetime` | ✅ Обязательно | `endDate` | `Date` | ✅ Обязательно | ❌ КРИТИЧНО | **ОШИБКА: сервер → ISO string, клиент → Date (нужен парсинг)** |
| `duration_days` | `int = 14` | ⚠️ Default | `durationDays` | `Int` | ✅ Обязательно | ⚠️ ПРОВЕРИТЬ | Может отсутствовать в JSON |

---

### Вложенная модель: SubscriptionLimits

| Поле (Сервер) | Тип (Сервер) | Обязательность | Поле (Клиент) | Тип (Клиент) | Обязательность | Статус | Проблема |
|---------------|--------------|----------------|---------------|--------------|----------------|--------|----------|
| `max_devices` | `int` | ✅ Обязательно | `maxDevices` | `Int` | ✅ Обязательно | ❌ КРИТИЧНО | **ОШИБКА: отсутствует в DeviceRegistrationSubscription** |
| `max_ai_messages` | `int` | ✅ Обязательно | `maxAIMessages` | `Int` | ✅ Обязательно | ❌ КРИТИЧНО | **ОШИБКА: отсутствует в DeviceRegistrationSubscription** |
| `max_scans` | `int` | ✅ Обязательно | `maxScans` | `Int` | ✅ Обязательно | ❌ КРИТИЧНО | **ОШИБКА: отсутствует в DeviceRegistrationSubscription** |
| `max_reports` | `int` | ✅ Обязательно | `maxReports` | `Int` | ✅ Обязательно | ❌ КРИТИЧНО | **ОШИБКА: отсутствует в DeviceRegistrationSubscription** |
| `current_usage` | `UsageCounters` | ⚠️ Default | `currentUsage` | `UsageCounters` | ⚠️ Default | ❌ КРИТИЧНО | **ОШИБКА: отсутствует в DeviceRegistrationSubscription** |

---

### Вложенная модель: UsageCounters

| Поле (Сервер) | Тип (Сервер) | Обязательность | Поле (Клиент) | Тип (Клиент) | Обязательность | Статус | Проблема |
|---------------|--------------|----------------|---------------|--------------|----------------|--------|----------|
| `ai_messages` | `int = 0` | ⚠️ Default | `aiMessages` | `Int` | ✅ Обязательно | ⚠️ ПРОВЕРИТЬ | Может отсутствовать в JSON |
| `scans` | `int = 0` | ⚠️ Default | `scans` | `Int` | ✅ Обязательно | ⚠️ ПРОВЕРИТЬ | Может отсутствовать в JSON |
| `reports` | `int = 0` | ⚠️ Default | `reports` | `Int` | ✅ Обязательно | ⚠️ ПРОВЕРИТЬ | Может отсутствовать в JSON |
| `devices` | `int = 0` | ⚠️ Default | `devices` | `Int` | ✅ Обязательно | ⚠️ ПРОВЕРИТЬ | Может отсутствовать в JSON |

---

## 🎯 КРИТИЧЕСКИЕ ПРОБЛЕМЫ (Требуют немедленного исправления)

### Проблема #1: `isActive` обязательное поле, но может отсутствовать в JSON
**Причина:**  
- Сервер: `is_active: bool = True` (default значение)
- FastAPI может **не включать** default значения в JSON, если они не были явно установлены
- Клиент: `let isActive: Bool` (обязательное поле)
- Результат: `DecodingError.keyNotFound("isActive")`

**Решение:**  
- Сделать `isActive` опциональным: `let isActive: Bool?`
- Или добавить default значение: `let isActive: Bool = true`
- Или добавить `CodingKeys` с маппингом `isActive = "is_active"` + кастомный `init(from:)`

---

### Проблема #2: `limits` отсутствует в `DeviceRegistrationSubscription`
**Причина:**  
- Сервер: `limits: SubscriptionLimits` (обязательное поле)
- Клиент: `DeviceRegistrationSubscription` **не содержит** поле `limits`
- Результат: При декодировании `subscription` поле `limits` игнорируется, но это может вызвать проблемы

**Решение:**  
- Добавить `limits: SubscriptionLimits?` в `DeviceRegistrationSubscription`
- Или создать полную модель `DeviceRegistrationSubscription` с `limits`
- Или использовать `SubscriptionPayload` напрямую (но это требует полного соответствия)

---

### Проблема #3: `TrialInfo` не декодируется из ISO строк
**Причина:**  
- Сервер: `start_date: datetime`, `end_date: datetime` → JSON как ISO 8601 строки
- Клиент: `startDate: Date`, `endDate: Date` → ожидает Date объект
- Результат: `DecodingError.typeMismatch` при попытке декодировать строку как Date

**Решение:**  
- Добавить `CodingKeys` для `TrialInfo`: `startDate = "start_date"`, `endDate = "end_date"`
- Добавить кастомный `init(from:)` для парсинга ISO 8601 строк в Date
- Или временно использовать `String` вместо `Date` и парсить позже

---

### Проблема #4: `SubscriptionLimits` не декодируется из snake_case
**Причина:**  
- Сервер: `max_devices`, `max_ai_messages`, `max_scans`, `max_reports`, `current_usage`
- Клиент: `maxDevices`, `maxAIMessages`, `maxScans`, `maxReports`, `currentUsage`
- Результат: `DecodingError.keyNotFound` для каждого поля

**Решение:**  
- Добавить `CodingKeys` в `SubscriptionLimits`:
  - `maxDevices = "max_devices"`
  - `maxAIMessages = "max_ai_messages"`
  - `maxScans = "max_scans"`
  - `maxReports = "max_reports"`
  - `currentUsage = "current_usage"`

---

### Проблема #5: `UsageCounters` не декодируется из snake_case
**Причина:**  
- Сервер: `ai_messages`, `scans`, `reports`, `devices`
- Клиент: `aiMessages`, `scans`, `reports`, `devices`
- Результат: `DecodingError.keyNotFound("ai_messages")`

**Решение:**  
- Добавить `CodingKeys` в `UsageCounters`:
  - `aiMessages = "ai_messages"`
  - Остальные поля совпадают (`scans`, `reports`, `devices`)

---

## 📝 ПЛАН ДЕЙСТВИЙ (Пошаговый)

### ЭТАП 1: Исправление DeviceRegistrationSubscription (Критично)

**Цель:** Устранить ошибку `keyNotFound("isActive")` и добавить недостающие поля.

**Шаги:**

1. **Обновить `DeviceRegistrationSubscription`:**
   - Добавить `CodingKeys` для маппинга snake_case → camelCase
   - Сделать `isActive` опциональным или с default значением
   - Добавить поле `limits: SubscriptionLimits?` (опционально, т.к. может отсутствовать)
   - Добавить поле `startDate: String?` (опционально, для совместимости)

2. **Обновить `TrialInfo`:**
   - Добавить `CodingKeys`: `startDate = "start_date"`, `endDate = "end_date"`, `durationDays = "duration_days"`
   - Изменить `startDate` и `endDate` на `String` (ISO 8601) вместо `Date`
   - Или добавить кастомный `init(from:)` для парсинга ISO строк в Date

3. **Обновить `SubscriptionLimits`:**
   - Добавить `CodingKeys` для всех полей (snake_case → camelCase)
   - Сделать `currentUsage` опциональным или с default значением

4. **Обновить `UsageCounters`:**
   - Добавить `CodingKeys`: `aiMessages = "ai_messages"`
   - Сделать все поля опциональными или с default значениями

---

### ЭТАП 2: Проверка и тестирование декодирования

**Цель:** Убедиться, что все модели корректно декодируются из реального JSON ответа сервера.

**Шаги:**

1. **Создать тестовый JSON** на основе реального ответа сервера:
   ```json
   {
     "token": "...",
     "device_id": "...",
     "expires_at": "2026-03-17T10:25:08Z",
     "registered_at": "2026-03-16T10:25:08Z",
     "subscription": {
       "level": "free",
       "start_date": "2026-03-16T10:25:08Z",
       "end_date": null,
       "is_active": true,
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
       "device_id": "...",
       "user_id": null
     }
   }
   ```

2. **Проверить декодирование:**
   - Убедиться, что все поля декодируются без ошибок
   - Проверить опциональные поля (если отсутствуют в JSON)
   - Проверить default значения

3. **Проверить конвертацию:**
   - `DeviceRegistrationSubscription.toSubscriptionStatus()` корректно создаёт `SubscriptionStatus`
   - Все данные передаются в `SubscriptionManager.storeToken()`

---

### ЭТАП 3: Исправление логики сохранения токена

**Цель:** Убедиться, что после успешного декодирования токен сохраняется во все хранилища.

**Шаги:**

1. **Проверить `SubscriptionManager.registerDeviceAnonymously()`:**
   - После успешного декодирования `JWTDeviceRegisterResponse`
   - Вызывается `storeToken(jwtToken)` с корректными данными
   - Вызывается `updateSubscriptionStatus(...)` с данными из `subscription`

2. **Проверить `SubscriptionManager.storeToken()`:**
   - Сохраняет токен в Keychain
   - Устанавливает `AppConfig.authToken`
   - Запускает `TokenHealthMonitor.startMonitoring()`

3. **Проверить синхронизацию:**
   - `AppConfig.authToken` всегда синхронизирован с `SubscriptionManager.currentToken.token`
   - При старте приложения токен загружается из Keychain в `AppConfig.authToken`

---

### ЭТАП 4: Улучшение логики автообновления токена

**Цель:** Реализовать полноценное автообновление токена через refresh endpoint.

**Шаги:**

1. **Проверить наличие refresh endpoint:**
   - `/api/auth/refresh` существует на сервере
   - Принимает `refresh_token` и возвращает новый `access_token`

2. **Реализовать `refreshToken()` в `TokenHealthMonitor`:**
   - Использовать `APIService.refreshToken()`
   - При успехе → обновить токен через `saveNewToken()`
   - При ошибке → fallback к `registerDeviceAnonymously()`

3. **Обновить `performProactiveRefresh()`:**
   - Сначала попытка `refreshToken()` (2-3 попытки с retry)
   - При неудаче → fallback к `registerDeviceAnonymously()`

---

### ЭТАП 5: Тестирование всех сценариев

**Цель:** Убедиться, что все сценарии работают корректно.

**Сценарии:**

1. **Первый запуск (нет токена):**
   - ✅ Регистрация устройства успешна
   - ✅ Токен декодируется без ошибок
   - ✅ Токен сохраняется в Keychain и AppConfig
   - ✅ `AnalyticsViewModel` видит токен

2. **Повторный запуск (валидный токен):**
   - ✅ Токен загружается из Keychain
   - ✅ Регистрация устройства не вызывается
   - ✅ `AnalyticsViewModel` видит токен

3. **Токен истёк:**
   - ✅ TokenValidator обнаруживает истёкший токен
   - ✅ Токен очищается из всех хранилищ
   - ✅ Вызывается регистрация устройства
   - ✅ Новый токен успешно декодируется и сохраняется

4. **Токен скоро истечёт (proactive refresh):**
   - ✅ TokenHealthMonitor обнаруживает скорое истечение
   - ✅ Вызывается refreshToken() или registerDeviceAnonymously()
   - ✅ Новый токен сохраняется до истечения старого

---

## 🔧 ТЕХНИЧЕСКИЕ ДЕТАЛИ ИСПРАВЛЕНИЙ

### Исправление #1: DeviceRegistrationSubscription

**Было:**
```swift
struct DeviceRegistrationSubscription: Codable {
    let level: String
    let isActive: Bool  // ❌ Обязательное, но может отсутствовать
    let expiresAt: String?
    let trialInfo: TrialInfo?
}
```

**Должно быть:**
```swift
struct DeviceRegistrationSubscription: Codable {
    let level: String
    let startDate: String?  // ✅ Добавить для совместимости
    let endDate: String?    // ✅ Маппинг end_date → endDate
    let isActive: Bool      // ✅ Сделать опциональным или с default
    let trialInfo: TrialInfo?
    let limits: SubscriptionLimits?  // ✅ Добавить limits (опционально)
    let permissions: [String: Any]?  // ✅ Опционально
    let deviceId: String?            // ✅ Опционально (дублируется в корне)
    let userId: String?             // ✅ Опционально
    
    enum CodingKeys: String, CodingKey {
        case level
        case startDate = "start_date"
        case endDate = "end_date"
        case isActive = "is_active"
        case trialInfo = "trial_info"
        case limits
        case permissions
        case deviceId = "device_id"
        case userId = "user_id"
    }
    
    // ✅ Кастомный init для обработки отсутствующих полей
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        level = try container.decode(String.self, forKey: .level)
        startDate = try container.decodeIfPresent(String.self, forKey: .startDate)
        endDate = try container.decodeIfPresent(String.self, forKey: .endDate)
        isActive = try container.decodeIfPresent(Bool.self, forKey: .isActive) ?? true  // ✅ Default = true
        trialInfo = try container.decodeIfPresent(TrialInfo.self, forKey: .trialInfo)
        limits = try container.decodeIfPresent(SubscriptionLimits.self, forKey: .limits)
        permissions = try container.decodeIfPresent([String: AnyCodable].self, forKey: .permissions)?.reduce(into: [String: Any]()) { $0[$1.key] = $1.value }
        deviceId = try container.decodeIfPresent(String.self, forKey: .deviceId)
        userId = try container.decodeIfPresent(String.self, forKey: .userId)
    }
}
```

---

### Исправление #2: TrialInfo

**Было:**
```swift
struct TrialInfo: Codable, Equatable {
    let startDate: Date  // ❌ Ожидает Date, но сервер отправляет ISO string
    let endDate: Date
    let durationDays: Int
}
```

**Должно быть:**
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
    
    // ✅ Кастомный init для парсинга ISO строк в Date
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        
        // Парсим ISO 8601 строки в Date
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime]
        
        let startDateString = try container.decode(String.self, forKey: .startDate)
        guard let startDateParsed = formatter.date(from: startDateString) else {
            throw DecodingError.dataCorruptedError(forKey: .startDate, in: container, debugDescription: "Invalid date format")
        }
        self.startDate = startDateParsed
        
        let endDateString = try container.decode(String.self, forKey: .endDate)
        guard let endDateParsed = formatter.date(from: endDateString) else {
            throw DecodingError.dataCorruptedError(forKey: .endDate, in: container, debugDescription: "Invalid date format")
        }
        self.endDate = endDateParsed
        
        durationDays = try container.decodeIfPresent(Int.self, forKey: .durationDays) ?? 14  // ✅ Default = 14
    }
}
```

---

### Исправление #3: SubscriptionLimits

**Было:**
```swift
struct SubscriptionLimits: Codable, Equatable {
    let maxDevices: Int  // ❌ Ожидает maxDevices, но сервер отправляет max_devices
    let maxAIMessages: Int
    let maxScans: Int
    let maxReports: Int
    var currentUsage: UsageCounters
}
```

**Должно быть:**
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
    
    // ✅ Кастомный init для обработки отсутствующих полей
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        maxDevices = try container.decode(Int.self, forKey: .maxDevices)
        maxAIMessages = try container.decode(Int.self, forKey: .maxAIMessages)
        maxScans = try container.decode(Int.self, forKey: .maxScans)
        maxReports = try container.decode(Int.self, forKey: .maxReports)
        currentUsage = try container.decodeIfPresent(UsageCounters.self, forKey: .currentUsage) ?? UsageCounters()  // ✅ Default
    }
}
```

---

### Исправление #4: UsageCounters

**Было:**
```swift
struct UsageCounters: Codable, Equatable {
    var aiMessages: Int  // ❌ Ожидает aiMessages, но сервер отправляет ai_messages
    var scans: Int
    var reports: Int
    var devices: Int
}
```

**Должно быть:**
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
    
    // ✅ Кастомный init для обработки отсутствующих полей
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        aiMessages = try container.decodeIfPresent(Int.self, forKey: .aiMessages) ?? 0  // ✅ Default = 0
        scans = try container.decodeIfPresent(Int.self, forKey: .scans) ?? 0
        reports = try container.decodeIfPresent(Int.self, forKey: .reports) ?? 0
        devices = try container.decodeIfPresent(Int.self, forKey: .devices) ?? 0
    }
}
```

---

## 📊 ПРИОРИТЕТЫ ИСПРАВЛЕНИЙ

### 🔴 КРИТИЧНО (Блокирует работу):
1. ✅ Исправить `DeviceRegistrationSubscription.isActive` (сделать опциональным или с default)
2. ✅ Добавить `CodingKeys` в `SubscriptionLimits` (snake_case → camelCase)
3. ✅ Добавить `CodingKeys` в `UsageCounters` (`ai_messages` → `aiMessages`)
4. ✅ Исправить `TrialInfo` (ISO string → Date парсинг)

### 🟡 ВАЖНО (Улучшает надёжность):
5. Добавить поле `limits` в `DeviceRegistrationSubscription` (опционально)
6. Добавить поля `startDate`, `endDate` в `DeviceRegistrationSubscription` для совместимости
7. Проверить синхронизацию `AppConfig.authToken` с `SubscriptionManager.currentToken`

### 🟢 ЖЕЛАТЕЛЬНО (Улучшает функциональность):
8. Реализовать полноценный `refreshToken()` в `TokenHealthMonitor`
9. Улучшить логику proactive refresh (умный гибрид)
10. Добавить больше логирования для отладки

---

## ✅ КРИТЕРИИ УСПЕХА

После всех исправлений должно быть:

1. ✅ **Нет ошибок декодирования:**
   - `JWTDeviceRegisterResponse` декодируется без `DecodingError`
   - `DeviceRegistrationSubscription` декодируется полностью
   - Все вложенные модели (`TrialInfo`, `SubscriptionLimits`, `UsageCounters`) декодируются корректно

2. ✅ **Токен сохраняется корректно:**
   - После регистрации устройства токен появляется в `AppConfig.authToken`
   - Токен сохраняется в Keychain
   - Токен сохраняется в `SubscriptionManager.currentToken`
   - `SubscriptionManager.currentSubscription` заполнен данными из `subscription`

3. ✅ **Автообновление работает:**
   - При истёкшем токене автоматически вызывается регистрация
   - Новый токен успешно декодируется и сохраняется
   - `AnalyticsViewModel` видит токен после регистрации

4. ✅ **Логи показывают успех:**
   - `✅ DEFENSIVE JWT: Токен успешно установлен`
   - `Token Exists: true` в health check
   - `AnalyticsViewModel: Токен найден`

---

## 📝 ЗАМЕТКИ

- **Важно:** Все изменения должны быть **обратно совместимыми** - не ломать существующий код
- **Тестирование:** После каждого исправления проверять компиляцию и запуск приложения
- **Логирование:** Добавить детальное логирование для отладки проблем декодирования
- **Документация:** Обновить комментарии в коде с указанием соответствия серверным моделям

---

**Следующий шаг:** Начать реализацию исправлений по приоритетам (🔴 КРИТИЧНО → 🟡 ВАЖНО → 🟢 ЖЕЛАТЕЛЬНО)
