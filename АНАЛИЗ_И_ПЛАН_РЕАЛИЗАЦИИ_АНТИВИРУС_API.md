# 🔍 АНАЛИЗ И ПЛАН РЕАЛИЗАЦИИ API ДЛЯ АНТИВИРУСА

**Дата:** 13 марта 2025  
**Статус:** ⚠️ ТРЕБУЕТСЯ РЕАЛИЗАЦИЯ  
**Приоритет:** 🔴 КРИТИЧЕСКИЙ (выход в продакшн)

---

## 📋 ТЕКУЩАЯ СИТУАЦИЯ

### ✅ ЧТО РАБОТАЕТ:
- Локальный карантин работает полностью ✅
- Сканирование антивируса работает ✅
- UI для антивируса реализован на 100% ✅
- Гармошка антивируса работает ✅
- Модальные окна работают ✅

### ❌ ЧТО НЕ РАБОТАЕТ:
- Синхронизация карантина с сервером ❌
- Получение списка угроз с сервера ❌
- Отправка действий карантина на сервер ❌

---

## 🔍 АНАЛИЗ НЕДОСТАЮЩИХ МЕТОДОВ

### 1. `getUserThreatsAsync(status: String)` ❌

**Где используется:**
- `Core/Antivirus/QuarantineManager.swift`, строка 247
- Метод `syncQuarantineWithServer()`

**Что нужно:**
- Получить список угроз пользователя с сервера
- Фильтр по статусу: `"quarantined"`, `"active"`, `"resolved"`

**Текущий статус:** ❌ Метод не реализован в `APIService.swift`

---

### 2. `quarantineFileAsync(threatId: String, action: String)` ❌

**Где используется:**
- `Core/Antivirus/QuarantineManager.swift`, строка 331
- Метод `syncWithServer(_ quarantinedFile: QuarantinedFile, action: String)`

**Что нужно:**
- Отправить действие с файлом в карантине на сервер
- Действия: `"quarantine"`, `"restore"`, `"remove"`

**Текущий статус:** ❌ Метод не реализован в `APIService.swift`

---

## 📊 АНАЛИЗ СУЩЕСТВУЮЩИХ ЭНДПОИНТОВ

### ✅ ЭНДПОИНТЫ, КОТОРЫЕ УЖЕ ЕСТЬ:

#### 1. Protection API (в AppConfig.swift):
```swift
static let protectionSettings = "/api/protection/settings"
static let protectionStatus = "/api/protection/status"
static let threatScenarios = "/api/protection/threat-scenarios"
static let protectionEnable = "/api/protection/enable"
static let protectionDisable = "/api/protection/disable"
static let protectionStats = "/api/protection/stats"
static let protectionSync = "/api/protection/sync"
```

#### 2. Malware API (из документации сервера):
```http
GET    /api/malware/quarantine        - Настройки карантина
PUT    /api/malware/quarantine        - Изменить карантин
POST   /api/malware/scan_now          - Запустить сканирование
GET    /api/malware/scan_scheduled    - Расписание сканирования
PUT    /api/malware/scan_scheduled    - Настроить расписание
```

---

## 🎯 ПЛАН РЕАЛИЗАЦИИ

### ЭТАП 1: ДОБАВИТЬ ЭНДПОИНТЫ В AppConfig.swift

**Нужно добавить:**
```swift
// Protection Threats & Quarantine
static let protectionThreats = "/api/protection/threats"           // GET - список угроз
static let protectionThreatsByStatus = "/api/protection/threats/{status}"  // GET - угрозы по статусу
static let protectionQuarantine = "/api/protection/quarantine"      // POST - действие с карантином
static let protectionQuarantineList = "/api/protection/quarantine/list"  // GET - список файлов в карантине
```

**Альтернатива (если сервер использует `/api/malware/`):**
```swift
// Malware API (если сервер использует этот путь)
static let malwareThreats = "/api/malware/threats"                 // GET - список угроз
static let malwareQuarantineAction = "/api/malware/quarantine/action"  // POST - действие с карантином
```

---

### ЭТАП 2: СОЗДАТЬ МОДЕЛИ ДАННЫХ

**Нужно создать структуры:**

```swift
// MARK: - Threat Models

struct ThreatResponse: Codable {
    let id: String
    let name: String
    let type: String
    let severity: String
    let confidence: Double
    let filePath: String?
    let fileSize: Int64?
    let detectedAt: Date
    let status: String  // "active", "quarantined", "resolved"
    let quarantinePath: String?
    let quarantinedAt: Date?
}

struct ThreatsListResponse: Codable {
    let threats: [ThreatResponse]
    let total: Int
    let active: Int
    let quarantined: Int
    let resolved: Int
}

struct QuarantineActionRequest: Codable {
    let threatId: String
    let action: String  // "quarantine", "restore", "remove"
    let filePath: String?
}

struct QuarantineActionResponse: Codable {
    let success: Bool
    let message: String?
    let threat: ThreatResponse?
}
```

---

### ЭТАП 3: РЕАЛИЗОВАТЬ МЕТОДЫ В APIService.swift

**Метод 1: `getUserThreatsAsync(status: String)`**

```swift
/// Получить список угроз пользователя с сервера
func getUserThreatsAsync(status: String? = nil) async throws -> [ThreatResponse] {
    return try await withCheckedThrowingContinuation { continuation in
        var hasResumed = false
        
        var endpoint = AppConfig.Endpoint.protectionThreats
        if let status = status {
            endpoint = AppConfig.Endpoint.protectionThreatsByStatus.replacingOccurrences(of: "{status}", with: status)
        }
        
        networkManager.get(endpoint: endpoint) { (result: Result<ThreatsListResponse, Error>) in
            guard !hasResumed else {
                logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in getUserThreatsAsync()!")
                return
            }
            hasResumed = true
            
            switch result {
            case .success(let response):
                continuation.resume(returning: response.threats)
            case .failure(let error):
                continuation.resume(throwing: error)
            }
        }
    }
}
```

**Метод 2: `quarantineFileAsync(threatId: String, action: String)`**

```swift
/// Выполнить действие с файлом в карантине на сервере
func quarantineFileAsync(threatId: String, action: String, filePath: String? = nil) async throws -> QuarantineActionResponse {
    return try await withCheckedThrowingContinuation { continuation in
        var hasResumed = false
        
        let request = QuarantineActionRequest(
            threatId: threatId,
            action: action,
            filePath: filePath
        )
        
        networkManager.post(endpoint: AppConfig.Endpoint.protectionQuarantine, body: request) { (result: Result<QuarantineActionResponse, Error>) in
            guard !hasResumed else {
                logger.error("⚠️ CRITICAL: Attempted to resume continuation twice in quarantineFileAsync()!")
                return
            }
            hasResumed = true
            continuation.resume(with: result)
        }
    }
}
```

---

### ЭТАП 4: РАСКОММЕНТИРОВАТЬ КОД В QuarantineManager.swift

**В методе `syncQuarantineWithServer()`:**
- Раскомментировать код синхронизации (строки 244-270)
- Убрать TODO комментарии

**В методе `syncWithServer()`:**
- Раскомментировать код синхронизации (строки 329-340)
- Убрать TODO комментарии

---

## 🔧 АЛЬТЕРНАТИВНЫЙ ПОДХОД (если сервер использует `/api/malware/`)

Если сервер использует путь `/api/malware/` вместо `/api/protection/`, нужно:

1. **Добавить эндпоинты в AppConfig.swift:**
```swift
// Malware API
static let malwareThreats = "/api/malware/threats"
static let malwareQuarantineAction = "/api/malware/quarantine/action"
```

2. **Использовать эти эндпоинты в методах APIService**

---

## 📋 ПРОВЕРКА СЕРВЕРА

**Нужно проверить на сервере:**

1. **Какие эндпоинты реально существуют:**
   - `/api/protection/threats` - существует?
   - `/api/malware/threats` - существует?
   - `/api/protection/quarantine` - существует?
   - `/api/malware/quarantine/action` - существует?

2. **Какая структура ответа:**
   - Формат данных угроз
   - Формат запроса для действий с карантином

3. **Требуется ли аутентификация:**
   - JWT токен в заголовках
   - Другие требования

---

## 🚨 КРИТИЧЕСКИЕ ВОПРОСЫ ДЛЯ ПРОВЕРКИ

1. **Существуют ли эндпоинты на сервере?**
   - Если нет → нужно создать на сервере
   - Если да → нужно проверить формат запроса/ответа

2. **Какой путь использовать?**
   - `/api/protection/threats` или `/api/malware/threats`?
   - Нужно проверить документацию сервера

3. **Какой формат данных?**
   - Нужно проверить реальные ответы сервера
   - Возможно, нужно адаптировать модели данных

---

## ✅ ЧЕКЛИСТ РЕАЛИЗАЦИИ

- [ ] Проверить существующие эндпоинты на сервере
- [ ] Добавить эндпоинты в `AppConfig.swift`
- [ ] Создать модели данных (`ThreatResponse`, `QuarantineActionRequest`, etc.)
- [ ] Реализовать `getUserThreatsAsync()` в `APIService.swift`
- [ ] Реализовать `quarantineFileAsync()` в `APIService.swift`
- [ ] Раскомментировать код синхронизации в `QuarantineManager.swift`
- [ ] Протестировать синхронизацию с сервером
- [ ] Обработать ошибки сети
- [ ] Добавить логирование
- [ ] Обновить документацию

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

1. **Проверить сервер** - какие эндпоинты реально существуют
2. **Реализовать методы** - добавить в `APIService.swift`
3. **Включить синхронизацию** - раскомментировать код в `QuarantineManager.swift`
4. **Протестировать** - проверить работу синхронизации

---

**СТАТУС:** ⚠️ ТРЕБУЕТСЯ РЕАЛИЗАЦИЯ ДЛЯ ПРОДАКШНА
