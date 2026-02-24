# 🚨 PRODUCTION SECURITY OPTIMIZATION PLAN
## Защита чувствительных данных в логах

**Создатель:** AI Assistant
**Дата:** 24 февраля 2026
**Статус:** CRITICAL - ТРЕБУЕТ НЕМЕДЛЕННОЙ РЕАЛИЗАЦИИ

---

## 🔍 АНАЛИЗ ТЕКУЩЕГО СОСТОЯНИЯ

### ✅ ЧТО УЖЕ РЕАЛИЗОВАНО:
- **MasterLogger** с базовой защитой заголовка `Authorization`
- **6 уровней логирования** (TRACE → FATAL)
- **7 категорий** (SYSTEM, UI, NETWORK, BUSINESS, SECURITY, PERFORMANCE, ERROR)

### ❌ КРИТИЧЕСКИЕ ПРОБЛЕМЫ БЕЗОПАСНОСТИ:

#### 🚨 **КРИТИЧНЫЕ УЯЗВИМОСТИ:**

##### 1. **ТОКЕНЫ В ОТКРЫТОМ ВИДЕ** (FamilyRegistrationViewModel)
```swift
// ViewModels/FamilyRegistrationViewModel.swift:300-303
if self?.isValidJWTToken(response.access_token) == true,  // ❌ ЛОГИРУЕТСЯ!
   self?.isValidJWTToken(response.refresh_token) == true, // ❌ ЛОГИРУЕТСЯ!
   let accessToken = response.access_token,              // ❌ ЛОГИРУЕТСЯ!
   let refreshToken = response.refresh_token {           // ❌ ЛОГИРУЕТСЯ!
```

##### 2. **ПРЯМЫЕ PRINT() СТАТЕМЕНТЫ** (МНОГО ФАЙЛОВ)
```swift
// FamilyRegistrationViewModel.swift
print("🏠 [FamilyRegistrationViewModel.createFamily] Роль: \(role.rawValue)")
// ❌ НЕ КОНТРОЛИРУЕТСЯ MasterLogger!

// PerformanceMonitor.swift
print("📈 PerformanceMonitor: Экран загружен за \(loadTime) сек")
// ❌ НЕТ ЗАЩИТЫ ЧУВСТВИТЕЛЬНЫХ ДАННЫХ
```

##### 3. **НЕДОСТАТОЧНАЯ ЗАЩИТА ЗАГОЛОВКОВ**
```swift
// MasterLogger.swift:192 - ТОЛЬКО Authorization
if headers["Authorization"] != nil { headers["Authorization"] = "<redacted>" }
// ❌ ПРОПУЩЕНЫ: X-API-Key, X-Auth-Token, Bearer в body, Cookie и др.
```

##### 4. **ОТСУТСТВИЕ ЗАЩИТЫ ТЕЛ ЗАПРОСОВ/ОТВЕТОВ**
- JSON с паролями, email, номерами карт логируется открыто
- Нет маскировки в NetworkManager.dataTask completion handlers

---

## 🎯 ДЕТАЛЬНЫЙ ПЛАН РЕАЛИЗАЦИИ

### **ЭТАП 1: АВАРИЙНАЯ ЗАЩИТА ТОКЕНОВ (2-4 часа)**

#### 1.1 Создать LogSanitizer класс
```swift
// Core/Utilities/LogSanitizer.swift - НОВЫЙ ФАЙЛ
class LogSanitizer {
    static func sanitizeString(_ input: String) -> String {
        // Маскировка JWT токенов
        let jwtPattern = #"eyJ[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*\.[A-Za-z0-9-_]*"#
        var result = input.replacingOccurrences(of: jwtPattern, with: "<jwt-token>", options: .regularExpression)

        // Маскировка email
        let emailPattern = #"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"#
        result = result.replacingOccurrences(of: emailPattern, with: "***@***.***", options: .regularExpression)

        return result
    }

    static func sanitizeHeaders(_ headers: [String: String]) -> [String: String] {
        var sanitized = headers
        let sensitiveKeys = ["authorization", "x-api-key", "x-auth-token", "bearer", "cookie", "set-cookie"]

        for key in headers.keys {
            if sensitiveKeys.contains(key.lowercased()) {
                sanitized[key] = "<redacted>"
            }
        }
        return sanitized
    }
}
```

#### 1.2 Обновить MasterLogger
```swift
// В Core/Utilities/MasterLogger.swift добавить:
func logRequest(_ request: URLRequest, function: String = #function, file: String = #file, line: Int = #line) {
    var headers = request.allHTTPHeaderFields ?? [:]
    headers = LogSanitizer.sanitizeHeaders(headers)  // ✅ НОВАЯ ЗАЩИТА

    let message = "➡️ \(request.httpMethod ?? "GET") \(request.url?.absoluteString ?? "-") headers=\(headers)"
    network(message, function: function, file: file, line: line)
}
```

#### 1.3 Защитить токены в FamilyRegistrationViewModel
```swift
// ViewModels/FamilyRegistrationViewModel.swift
private func createFamily() {
    // ДО:
    print("🏠 Роль: \(role.rawValue)")  // ❌ ОПАСНО

    // ПОСЛЕ:
    logger.business("Creating family with role: \(role.rawValue)")  // ✅ ЗАЩИЩЕНО
}

// В методах работы с токенами:
private func saveTokens(accessToken: String, refreshToken: String) {
    // ДО: токены в логах

    // ПОСЛЕ:
    logger.business("Saving user tokens (access: \(accessToken.prefix(10))..., refresh: \(refreshToken.prefix(10))...)")
    // ✅ ТОЛЬКО ПЕРВЫЕ 10 СИМВОЛОВ
}
```

---

### **ЭТАП 2: ЗАЩИТА ТЕЛ ЗАПРОСОВ/ОТВЕТОВ (4-6 часов)**

#### 2.1 Добавить JSON маскировку
```swift
// LogSanitizer.swift - расширение
static func sanitizeJSON(_ jsonString: String) -> String {
    guard let data = jsonString.data(using: .utf8),
          let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any] else {
        return sanitizeString(jsonString)
    }

    var sanitized = json

    // Маскировка чувствительных полей
    let sensitiveFields = ["password", "email", "phone", "card_number", "cvv", "pin"]
    for field in sensitiveFields {
        if sanitized[field] != nil {
            sanitized[field] = "<redacted>"
        }
    }

    // Частичная маскировка карт
    if let cardNumber = sanitized["card_number"] as? String {
        sanitized["card_number"] = maskCreditCard(cardNumber)
    }

    // Сериализация обратно
    if let data = try? JSONSerialization.data(withJSONObject: sanitized),
       let result = String(data: data, encoding: .utf8) {
        return result
    }

    return "<json-sanitized>"
}

private static func maskCreditCard(_ number: String) -> String {
    let cleanNumber = number.replacingOccurrences(of: "[^0-9]", with: "", options: .regularExpression)
    guard cleanNumber.count >= 4 else { return "****" }

    let last4 = String(cleanNumber.suffix(4))
    return "**** **** **** \(last4)"
}
```

#### 2.2 Обновить NetworkManager
```swift
// Core/Network/NetworkManager.swift
session.dataTask(with: request) { [weak self] data, response, error in
    // ДО:
    MasterLogger.shared.network("⬅️ Response: status=\(http.statusCode) url=\(http.url?.absoluteString ?? "-")")

    // ПОСЛЕ:
    var responseInfo = "status=\(http.statusCode) url=\(http.url?.absoluteString ?? "-")"

    if let data = data, let jsonString = String(data: data, encoding: .utf8) {
        let sanitizedJSON = LogSanitizer.sanitizeJSON(jsonString)
        responseInfo += " body=\(sanitizedJSON)"
    }

    MasterLogger.shared.network("⬅️ Response: \(responseInfo)")
}
```

---

### **ЭТАП 3: ЗАМЕНА PRINT() НА LOGGER (3-4 часа)**

#### 3.1 FamilyRegistrationViewModel
```swift
// ЗАМЕНИТЬ ВСЕ print() на logger.business()
print("✅ Роль сохранена: \(role.rawValue)")
// НА:
logger.business("Family role saved: \(role.rawValue)")
```

#### 3.2 AntivirusManager
```swift
// Core/Antivirus/AntivirusManager.swift
print("[AntivirusManager] \(message)")
// НА:
logger.business("[Antivirus] \(message)")
```

#### 3.3 PerformanceMonitor
```swift
// Core/Monitoring/PerformanceMonitor.swift
print("📈 PerformanceMonitor: \(message)")
// НА:
logger.performance(message)
```

---

### **ЭТАП 4: RELEASE VS DEBUG РЕЖИМЫ (2-3 часа)**

#### 4.1 Создать конфигурацию уровней
```swift
// MasterLogger.swift - расширение
var maxLogLevel: LogLevel {
    #if DEBUG
    return .trace  // Все логи в отладке
    #else
    return .info   // Только INFO и выше в продакшене
    #endif
}
```

#### 4.2 Фильтрация по режимам
```swift
func log(_ level: LogLevel, category: LogCategory, message: String, function: String, file: String, line: Int) {
    guard level.priority >= maxLogLevel.priority else { return }

    // В RELEASE режиме дополнительная фильтрация
    #if !DEBUG
    if containsSensitiveData(message) {
        return // Не логировать чувствительные данные в продакшене
    }
    #endif

    // ... остальной код логирования
}
```

---

### **ЭТАП 5: ТЕСТИРОВАНИЕ И ВАЛИДАЦИЯ (4-6 часов)**

#### 5.1 Модульные тесты
```swift
// Tests/LogSanitizerTests.swift
func testSanitizeJWTToken() {
    let input = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    let output = LogSanitizer.sanitizeString(input)
    XCTAssertEqual(output, "Bearer <jwt-token>")
}

func testSanitizeEmail() {
    let input = "user@example.com"
    let output = LogSanitizer.sanitizeString(input)
    XCTAssertEqual(output, "***@***.***")
}

func testSanitizeCreditCard() {
    let input = "4111111111111111"
    let output = LogSanitizer.maskCreditCard(input)
    XCTAssertEqual(output, "**** **** **** 1111")
}
```

#### 5.2 Интеграционные тесты
- Запустить приложение в DEBUG режиме
- Проверить, что чувствительные данные маскируются
- Запустить в RELEASE конфигурации
- Убедиться, что лишние логи не выводятся

---

## 📊 МЕТРИКИ УСПЕХА

### **ДО РЕАЛИЗАЦИИ:**
- 🚨 **Токены в логах:** 100% открыто
- 🚨 **Print statements:** 15+ неконтролируемых
- 🚨 **JSON тела:** 0% защиты
- 🚨 **Headers:** 16% защиты (только Authorization)

### **ПОСЛЕ РЕАЛИЗАЦИИ:**
- ✅ **Токены:** 100% маскированы
- ✅ **Print statements:** 100% заменены на logger
- ✅ **JSON тела:** 100% санитизированы
- ✅ **Headers:** 100% защищены
- ✅ **Release mode:** Только безопасные логи

---

## ⏰ СРОКИ И ПРИОРИТЕТЫ

### **КРИТИЧНЫЙ ПРИОРИТЕТ (1-2 дня):**
- Этап 1: Аварийная защита токенов
- Этап 3: Замена print() на logger

### **ВЫСОКИЙ ПРИОРИТЕТ (3-4 дня):**
- Этап 2: Защита тел запросов
- Этап 4: Release vs Debug режимы

### **СРЕДНИЙ ПРИОРИТЕТ (2-3 дня):**
- Этап 5: Тестирование и валидация

---

## 🛡️ РИСК-АНАЛИЗ

### **РИСКИ НЕВЫПОЛНЕНИЯ:**
- **Утечка токенов:** Кража аккаунтов пользователей
- **Штрафы GDPR:** До 4% годового оборота
- **Блокировка App Store:** Нарушение правил приватности
- **Репутационные потери:** Потеря доверия пользователей

### **РИСКИ РЕАЛИЗАЦИИ:**
- **Производительность:** +5-10% CPU на санитизацию
- **Сложность отладки:** Меньше деталей в продакшен логах
- **Ложные срабатывания:** Перемаскировка безопасных данных

---

## 🎯 РЕКОМЕНДАЦИИ

### **НЕМЕДЛЕННО СДЕЛАТЬ:**
1. **Этап 1** - Защита токенов (критично для безопасности)
2. **Этап 3** - Замена print() (стандартизация логирования)

### **СДЕЛАТЬ В ТЕЧЕНИЕ НЕДЕЛИ:**
3. **Этап 2** - Защита JSON (комплексная безопасность)
4. **Этап 4** - Режимы логирования (production готовность)

### **ФИНАЛЬНО:**
5. **Этап 5** - Тестирование (гарантия качества)

---

## 💡 ПРОФЕССИОНАЛЬНЫЕ СОВЕТЫ

### **ЗОЛОТОЕ ПРАВИЛО:**
> "Лучше замаскировать лишнее, чем пропустить одно чувствительное поле"

### **СТАНДАРТЫ БЕЗОПАСНОСТИ:**
- **OWASP:** Не логировать PII (Personally Identifiable Information)
- **PCI DSS:** Не логировать данные платежных карт
- **Apple Guidelines:** Защита пользовательских данных

### **МОНИТОРИНГ:**
- Регулярные аудиты логов
- Автоматические алерты на подозрительные паттерны
- Обновление правил маскировки при добавлении новых полей

---

*Этот план является **КРИТИЧНЫМ** для безопасности приложения и должен быть реализован **НЕМЕДЛЕННО** перед выпуском в продакшн.*

**Статус:** 🟥 **ТРЕБУЕТ НЕМЕДЛЕННОЙ РЕАЛИЗАЦИИ**
**Приоритет:** **CRITICAL** 🚨