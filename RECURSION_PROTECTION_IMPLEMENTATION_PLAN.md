# 🛡️ ПЛАН РЕАЛИЗАЦИИ ЗАЩИТЫ ОТ РЕКУРСИИ В ЛОГИРОВАНИИ
## Детальный план исправления краша BUILD 86

**Дата создания:** 2026-03-09  
**Приоритет:** 🔴 КРИТИЧЕСКИЙ  
**Цель:** Устранить рекурсию в os_log при обработке эмодзи

---

## 📋 ОБЩИЙ ПЛАН

### **Этап 1: Критические исправления (высокий приоритет)**
1. Отключить os_log в RELEASE
2. Убрать эмодзи перед os_log
3. Убрать эмодзи из NetworkManager os_log

### **Этап 2: Дополнительные защиты (средний приоритет)**
4. Добавить защиту от рекурсии в VisualLogger
5. Добавить защиту от рекурсии в MasterLogger

### **Этап 3: Тестирование**
6. Проверить компиляцию
7. Проверить работу логирования

---

## 🔴 ЭТАП 1: КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ

### **ЗАДАЧА 1: Отключить os_log в RELEASE**

**Файл:** `Core/Diagnostics/SettingsDiagnosticsLogger.swift`  
**Строки:** 158-169  
**Приоритет:** 🔴 ВЫСОКИЙ

**Текущий код:**
```swift
// 1. os_log (системное логирование) - с try-catch для безопасности
do {
    os_log(
        "%{public}@",
        log: osLog,
        type: level.osLogType,
        safeMessage
    )
} catch {
    // Fallback если os_log сломался - просто print уже сделали выше
    print("⚠️ OS_LOG_ERROR: \(error.localizedDescription)")
}
```

**Новый код:**
```swift
// 1. os_log (системное логирование) - ТОЛЬКО в DEBUG
#if DEBUG
    // В DEBUG используем os_log для системного логирования
    os_log(
        "%{public}@",
        log: osLog,
        type: level.osLogType,
        safeMessage
    )
#else
    // В RELEASE используем только print() - os_log вызывает рекурсию при обработке эмодзи
    // print() уже вызван выше (строка 156), но можно добавить дополнительный print для ясности
    // os_log отключен для предотвращения рекурсии в TestFlight/Production
#endif
```

**Изменения:**
- ✅ Обернуть os_log в `#if DEBUG`
- ✅ Убрать try-catch (os_log не выбрасывает исключения)
- ✅ Добавить комментарий объясняющий почему отключен

**Почему критично:**
- os_log вызывает рекурсию при обработке строк с эмодзи
- Краш происходит в RELEASE сборке (TestFlight)
- print() безопаснее и не вызывает рекурсию

---

### **ЗАДАЧА 2: Создать функцию removeEmoji()**

**Файл:** `Core/Diagnostics/SettingsDiagnosticsLogger.swift`  
**Место:** После метода `log()` или в extension  
**Приоритет:** 🔴 ВЫСОКИЙ

**Новый код:**
```swift
// MARK: - String Sanitization

/// Удаляет эмодзи из строки для безопасного использования в os_log
/// Эмодзи могут вызывать рекурсию в os_log при обработке UTF-16
private func removeEmoji(_ string: String) -> String {
    return string.unicodeScalars
        .filter { scalar in
            // Удаляем все эмодзи и связанные символы
            !scalar.properties.isEmoji &&
            !scalar.properties.isEmojiPresentation &&
            scalar.value != 0xFE0F // Variation Selector-16 (emoji modifier)
        }
        .reduce("") { $0 + String($1) }
}
```

**Альтернативный вариант (более простой):**
```swift
/// Удаляет эмодзи из строки для безопасного использования в os_log
private func removeEmoji(_ string: String) -> String {
    return string.unicodeScalars
        .filter { !$0.properties.isEmoji }
        .reduce("") { $0 + String($1) }
}
```

**Изменения:**
- ✅ Добавить приватный метод `removeEmoji()`
- ✅ Использовать `unicodeScalars` для фильтрации эмодзи
- ✅ Вернуть строку без эмодзи

**Почему критично:**
- Эмодзи вызывают рекурсию в os_log
- Нужно убрать эмодзи перед передачей в os_log

---

### **ЗАДАЧА 3: Применить removeEmoji() перед os_log**

**Файл:** `Core/Diagnostics/SettingsDiagnosticsLogger.swift`  
**Строки:** 149-169  
**Приоритет:** 🔴 ВЫСОКИЙ

**Текущий код:**
```swift
// 🔒 ОГРАНИЧИТЬ ДЛИНУ СООБЩЕНИЯ ДЛЯ БЕЗОПАСНОСТИ
let safeMessage = entry.formattedMessage.count > 500 ?
    String(entry.formattedMessage.prefix(500)) + "..." : entry.formattedMessage

// ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Сначала print() для немедленного отображения в Xcode
print("🔍 SETTINGS_DIAG: \(safeMessage)")

// 1. os_log (системное логирование) - ТОЛЬКО в DEBUG
#if DEBUG
    os_log("%{public}@", log: osLog, type: level.osLogType, safeMessage)
#endif
```

**Новый код:**
```swift
// 🔒 ОГРАНИЧИТЬ ДЛИНУ СООБЩЕНИЯ ДЛЯ БЕЗОПАСНОСТИ
let safeMessage = entry.formattedMessage.count > 500 ?
    String(entry.formattedMessage.prefix(500)) + "..." : entry.formattedMessage

// ✅ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Сначала print() для немедленного отображения в Xcode
// print() безопасен и может содержать эмодзи
print("🔍 SETTINGS_DIAG: \(safeMessage)")

// 1. os_log (системное логирование) - ТОЛЬКО в DEBUG, БЕЗ ЭМОДЗИ
#if DEBUG
    // Убираем эмодзи перед os_log для предотвращения рекурсии
    let messageForOSLog = removeEmoji(safeMessage)
    os_log("%{public}@", log: osLog, type: level.osLogType, messageForOSLog)
#endif
```

**Изменения:**
- ✅ Применить `removeEmoji()` перед os_log
- ✅ Сохранить эмодзи в print() (он безопасен)
- ✅ Убрать эмодзи только для os_log

**Почему критично:**
- Эмодзи вызывают рекурсию в os_log
- print() безопасен и может содержать эмодзи

---

### **ЗАДАЧА 4: Убрать эмодзи из NetworkManager os_log**

**Файл:** `Core/Network/NetworkManager.swift`  
**Приоритет:** 🔴 ВЫСОКИЙ

**Найти все места с os_log и эмодзи:**

1. **Строка 127:** `os_log("🚨 КРИТИЧЕСКАЯ ОШИБКА: SSL Pinning отключен...")`
2. **Строка 137:** `os_log("🔐 SSL Pinning: %{public}@...")`
3. **Строка 661:** `os_log("🚫 Rate Limit: Request blocked...")`
4. **Строка 677:** `os_log("🌐 API Request: %{public}@...")`
5. **Строка 739:** `os_log("❌ Network Error: %{public}@...")`
6. **Строка 788:** `os_log("❌ Invalid Response: %{public}@...")`
7. **Строка 806:** `os_log("⚠️ HTTP Error: %d - %{public}@...")`
8. **Строка 835:** `os_log("⚠️ 429 Too Many Requests: %{public}@...")`
9. **Строка 856:** `os_log("❌ Max retries exceeded for 401: %{public}@...")`
10. **Строка 879:** `os_log("⚠️ 401 Unauthorized: %{public}@...")`
11. **Строка 894:** `os_log("❌ No valid token: %{public}@...")`
12. **Строка 920:** `os_log("✅ Token refreshed: %{public}@...")`
13. **Строка 962:** `os_log("❌ Token refresh failed: %{public}@...")`
14. **Строка 1000:** `os_log("❌ HTTP Error %d: %{public}@...")`
15. **Строка 1054:** `os_log("❌ No data in response: %{public}@...")`
16. **Строка 1102:** `os_log("❌ Validation Error: %{public}@...")`
17. **Строка 1116:** `os_log("❌ Unexpected validation error: %{public}@...")`
18. **Строка 1127:** `os_log("❌ Decoding Error: %{public}@...")`
19. **Строка 1241:** `os_log("✅ SSL Pinning: Сертификат для %{public}@...")`
20. **Строка 1252:** `os_log("🚨 SSL Pinning ERROR: Соединение заблокировано...")`

**Решение:**

**Вариант 1: Убрать эмодзи из всех строк**
```swift
// ❌ БЫЛО:
os_log("❌ Network Error: %{public}@ - %{public}@", ...)

// ✅ СТАЛО:
os_log("Network Error: %{public}@ - %{public}@", ...)
```

**Вариант 2: Обернуть в #if DEBUG и убрать эмодзи**
```swift
#if DEBUG
    os_log("Network Error: %{public}@ - %{public}@", ...)
#else
    // В RELEASE используем только print() или убираем логирование
#endif
```

**Рекомендация:** Использовать Вариант 1 (убрать эмодзи) для всех os_log вызовов

**Изменения:**
- ✅ Убрать все эмодзи из строк формата os_log
- ✅ Сохранить информативность сообщений без эмодзи
- ✅ Можно оставить эмодзи в print() если он используется рядом

**Почему критично:**
- Прямое использование эмодзи в os_log вызывает рекурсию
- Множество мест использования требует исправления

---

## 🟡 ЭТАП 2: ДОПОЛНИТЕЛЬНЫЕ ЗАЩИТЫ

### **ЗАДАЧА 5: Добавить защиту от рекурсии в VisualLogger**

**Файл:** `Core/Utilities/VisualLogger.swift`  
**Метод:** `log(_:level:file:line:)`  
**Приоритет:** 🟡 СРЕДНИЙ

**Текущий код:**
```swift
func log(_ message: String, level: LogLevel = .info, file: String = #file, line: Int = #line) {
    let fileName = (file as NSString).lastPathComponent
    let entry = LogEntry(...)
    
    DispatchQueue.main.async {
        self.logs.append(entry)
        // ...
    }
    
    saveLogToUserDefaults(entry)
    print("[\(entry.formattedTime)] [\(level.rawValue)] [\(fileName):\(line)] \(message)")
}
```

**Новый код:**
```swift
/// 🛡️ Флаг защиты от рекурсии - предотвращает бесконечный цикл
private var isLoggingInProgress = false

func log(_ message: String, level: LogLevel = .info, file: String = #file, line: Int = #line) {
    // 🛡️ ЗАЩИТА ОТ РЕКУРСИИ - если уже логируем, выходим
    guard !isLoggingInProgress else { return }
    isLoggingInProgress = true
    defer { isLoggingInProgress = false }
    
    let fileName = (file as NSString).lastPathComponent
    let entry = LogEntry(...)
    
    DispatchQueue.main.async {
        self.logs.append(entry)
        // ...
    }
    
    saveLogToUserDefaults(entry)
    print("[\(entry.formattedTime)] [\(level.rawValue)] [\(fileName):\(line)] \(message)")
}
```

**Изменения:**
- ✅ Добавить приватное свойство `isLoggingInProgress`
- ✅ Добавить проверку в начале метода `log()`
- ✅ Использовать `defer` для сброса флага

**Почему важно:**
- Защита от повторных вызовов log()
- Единообразие с SettingsDiagnosticsLogger

---

### **ЗАДАЧА 6: Добавить защиту от рекурсии в MasterLogger**

**Файл:** `Core/Utilities/MasterLogger.swift`  
**Метод:** `log(_:category:message:function:file:line:)`  
**Приоритет:** 🟡 СРЕДНИЙ

**Текущий код:**
```swift
func log(
    _ level: LogLevel,
    category: LogCategory = .system,
    message: String,
    function: String = #function,
    file: String = #file,
    line: Int = #line
) {
    guard level.priority >= maxLogLevel.priority else { return }
    
    let fileName = (file as NSString).lastPathComponent
    let fullMessage = "[\(category.rawValue)] \(message)"
    
    // 1. SettingsDiagnosticsLogger
    switch level {
    case .trace, .debug, .info:
        settingsLogger.logFunction(function, message: fullMessage, section: category.rawValue)
    // ...
    }
    
    // 2. Visual Logger
    if enableVisualLogging {
        visualLogger.log(...)
    }
    
    // 3. Console logging
    #if DEBUG
    if enableConsoleLogging {
        print(...)
    }
    #endif
}
```

**Новый код:**
```swift
/// 🛡️ Флаг защиты от рекурсии - предотвращает бесконечный цикл
private var isLoggingInProgress = false

func log(
    _ level: LogLevel,
    category: LogCategory = .system,
    message: String,
    function: String = #function,
    file: String = #file,
    line: Int = #line
) {
    // 🛡️ ЗАЩИТА ОТ РЕКУРСИИ - если уже логируем, выходим
    guard !isLoggingInProgress else { return }
    isLoggingInProgress = true
    defer { isLoggingInProgress = false }
    
    guard level.priority >= maxLogLevel.priority else { return }
    
    // ... остальной код без изменений
}
```

**Изменения:**
- ✅ Добавить приватное свойство `isLoggingInProgress`
- ✅ Добавить проверку в начале метода `log()`
- ✅ Использовать `defer` для сброса флага

**Почему важно:**
- Защита от повторных вызовов log()
- Единообразие с другими логгерами

---

## ✅ ЭТАП 3: ТЕСТИРОВАНИЕ

### **ЗАДАЧА 7: Проверить компиляцию проекта**

**Действия:**
1. Открыть проект в Xcode
2. Выбрать схему сборки (Debug и Release)
3. Запустить компиляцию (`Cmd+B`)
4. Проверить отсутствие ошибок компиляции
5. Проверить отсутствие предупреждений

**Ожидаемый результат:**
- ✅ Проект компилируется без ошибок
- ✅ Нет критических предупреждений

---

### **ЗАДАЧА 8: Проверить работу логирования**

**Действия:**
1. Запустить приложение в симуляторе (DEBUG)
2. Проверить что логи отображаются в консоли Xcode
3. Проверить что VisualLogger показывает логи на экране
4. Проверить что нет рекурсии (приложение не крашится)
5. Собрать RELEASE версию и проверить что нет os_log вызовов

**Ожидаемый результат:**
- ✅ Логи отображаются в DEBUG
- ✅ В RELEASE нет os_log вызовов (только print)
- ✅ Нет рекурсии и крашей

---

## 📊 ПРИОРИТЕТЫ И ПОСЛЕДОВАТЕЛЬНОСТЬ

### **Критические (делать первыми):**
1. ✅ Задача 1: Отключить os_log в RELEASE
2. ✅ Задача 2: Создать функцию removeEmoji()
3. ✅ Задача 3: Применить removeEmoji() перед os_log
4. ✅ Задача 4: Убрать эмодзи из NetworkManager os_log

### **Важные (делать после критических):**
5. ✅ Задача 5: Добавить защиту в VisualLogger
6. ✅ Задача 6: Добавить защиту в MasterLogger

### **Тестирование (делать в конце):**
7. ✅ Задача 7: Проверить компиляцию
8. ✅ Задача 8: Проверить работу логирования

---

## 🎯 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После реализации всех задач:

1. ✅ **os_log отключен в RELEASE** - нет рекурсии в TestFlight
2. ✅ **Эмодзи убраны из os_log** - безопасная обработка строк
3. ✅ **Защита от рекурсии на всех уровнях** - дополнительная безопасность
4. ✅ **Логирование работает корректно** - в DEBUG и RELEASE

---

## 📝 ЗАМЕТКИ

- Все изменения должны быть протестированы в DEBUG и RELEASE
- Важно сохранить информативность логов без эмодзи
- print() безопасен и может содержать эмодзи
- os_log должен использоваться только в DEBUG и без эмодзи

---

**Дата создания:** 2026-03-09  
**Автор:** AI Assistant  
**Версия:** 1.0
