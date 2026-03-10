# 🔍 BUILD 94 - ПЛАН ДИАГНОСТИКИ КРАШЕЙ НА РЕАЛЬНОМ УСТРОЙСТВЕ

## 📊 ЧТО УЖЕ СДЕЛАНО

### ✅ 1. Глобальный Exception Handler
**Файл:** `AppDelegate.swift:9-49` и `ALADDINApp.swift:151-160`
- ✅ `NSSetUncaughtExceptionHandler` установлен
- ✅ Сохранение крашей в UserDefaults
- ✅ Сохранение крашей в файлы (`crash_log.txt`, `crash_stack_trace.txt`)
- ✅ Отправка крашей на сервер (`/api/crash-detection/report`)

**Статус:** ✅ Работает

---

### ✅ 2. Visual Logger
**Файл:** `Core/Utilities/VisualLogger.swift`
- ✅ Отображение логов на экране (в DEBUG режиме)
- ✅ Сохранение логов в UserDefaults
- ✅ Восстановление логов после краша
- ✅ Копирование логов в буфер обмена

**Статус:** ✅ Работает, но только в DEBUG

---

### ✅ 3. Master Logger
**Файл:** `Core/Utilities/MasterLogger.swift`
- ✅ `os_log()` для production логирования
- ✅ Разные уровни логирования (TRACE, DEBUG, INFO, WARN, ERROR, FATAL)
- ✅ Интеграция с VisualLogger

**Статус:** ✅ Работает

---

### ✅ 4. Performance Monitor
**Файл:** `Core/Monitoring/PerformanceMonitor.swift`
- ✅ Мониторинг FPS
- ✅ Мониторинг памяти (каждые 30 секунд)
- ✅ Отслеживание времени загрузки экранов
- ✅ Отправка метрик на сервер

**Статус:** ✅ Работает

---

### ✅ 5. Debug функции
**Файл:** `ALADDINApp.swift:936-1066`
- ✅ `getCrashLogs()` - получение логов из UserDefaults
- ✅ `getCrashLogsFromFiles()` - получение логов из файлов
- ✅ `getAllCrashLogs()` - получение всех логов
- ✅ `clearCrashLogs()` - очистка логов

**Статус:** ✅ Работает

---

## 🔴 ЧТО НУЖНО ДОБАВИТЬ ДЛЯ РЕАЛЬНОГО УСТРОЙСТВА

### 🔴 ПРОБЛЕМА: Разница между симулятором и реальным устройством

**Почему краш только на реальном устройстве:**
1. **Меньше памяти** - реальное устройство имеет ограниченную память
2. **Меньше stack size** - stack может быть меньше на реальном устройстве
3. **Медленнее UserDefaults** - чтение/запись медленнее на реальном устройстве
4. **Разное поведение потоков** - threading работает по-другому
5. **Memory pressure** - система может убить приложение при нехватке памяти

---

## 🛠️ ПЛАН ДОПОЛНИТЕЛЬНОЙ ДИАГНОСТИКИ

### ✅ ЭТАП 1: Добавить Memory Warning Handler

**Цель:** Отслеживать предупреждения о нехватке памяти

**Что добавить:**
```swift
// В AppDelegate.swift
func applicationDidReceiveMemoryWarning(_ application: UIApplication) {
    let memoryUsage = getMemoryUsageMB()
    let crashLog = """
    🚨 MEMORY WARNING!
    Memory Usage: \(memoryUsage) MB
    Time: \(Date())
    """
    
    // Сохраняем в UserDefaults
    UserDefaults.standard.set(crashLog, forKey: "memory_warning_log")
    UserDefaults.standard.set(Date().timeIntervalSince1970, forKey: "memory_warning_timestamp")
    
    // Отправляем на сервер
    sendMemoryWarningToServer(memoryUsage: memoryUsage)
    
    print("🚨 MEMORY WARNING: \(memoryUsage) MB")
}
```

**Файл:** `AppDelegate.swift`

---

### ✅ ЭТАП 2: Добавить Stack Size Monitoring

**Цель:** Отслеживать использование stack перед крашем

**Что добавить:**
```swift
// В ALADDINApp.swift или отдельный файл
func checkStackSize() {
    var stackSize: UInt = 0
    pthread_attr_t attr
    pthread_attr_init(&attr)
    pthread_attr_getstacksize(&attr, &stackSize)
    pthread_attr_destroy(&attr)
    
    let stackSizeKB = stackSize / 1024
    let crashLog = """
    📊 STACK SIZE CHECK
    Stack Size: \(stackSizeKB) KB
    Time: \(Date())
    """
    
    UserDefaults.standard.set(stackSizeKB, forKey: "last_stack_size_kb")
    print("📊 Stack Size: \(stackSizeKB) KB")
}
```

**Файл:** Новый файл `Core/Diagnostics/StackSizeMonitor.swift`

---

### ✅ ЭТАП 3: Добавить UserDefaults Performance Monitoring

**Цель:** Отслеживать медленные операции с UserDefaults

**Что добавить:**
```swift
// Обертка для UserDefaults с мониторингом
class MonitoredUserDefaults {
    static let standard = UserDefaults.standard
    
    static func monitoredGet<T>(key: String, defaultValue: T) -> T {
        let startTime = Date()
        let result = standard.object(forKey: key) as? T ?? defaultValue
        let duration = Date().timeIntervalSince(startTime)
        
        if duration > 0.1 { // Если операция заняла больше 100ms
            let log = """
            ⚠️ SLOW UserDefaults READ
            Key: \(key)
            Duration: \(duration * 1000) ms
            Time: \(Date())
            """
            UserDefaults.standard.set(log, forKey: "slow_userdefaults_log")
            print("⚠️ SLOW UserDefaults READ: \(key) took \(duration * 1000) ms")
        }
        
        return result
    }
    
    static func monitoredSet(_ value: Any?, forKey key: String) {
        let startTime = Date()
        standard.set(value, forKey: key)
        let duration = Date().timeIntervalSince(startTime)
        
        if duration > 0.1 {
            let log = """
            ⚠️ SLOW UserDefaults WRITE
            Key: \(key)
            Duration: \(duration * 1000) ms
            Time: \(Date())
            """
            UserDefaults.standard.set(log, forKey: "slow_userdefaults_log")
            print("⚠️ SLOW UserDefaults WRITE: \(key) took \(duration * 1000) ms")
        }
    }
}
```

**Файл:** Новый файл `Core/Diagnostics/MonitoredUserDefaults.swift`

---

### ✅ ЭТАП 4: Добавить Thread Monitoring

**Цель:** Отслеживать создание потоков и их stack size

**Что добавить:**
```swift
// В AppDelegate или отдельный файл
func monitorThreads() {
    let threadCount = Thread.activeThreadCount
    let mainThreadStackSize = getMainThreadStackSize()
    
    let log = """
    📊 THREAD MONITORING
    Active Threads: \(threadCount)
    Main Thread Stack Size: \(mainThreadStackSize) KB
    Time: \(Date())
    """
    
    UserDefaults.standard.set(log, forKey: "thread_monitoring_log")
    print("📊 Threads: \(threadCount), Main Stack: \(mainThreadStackSize) KB")
}
```

**Файл:** Новый файл `Core/Diagnostics/ThreadMonitor.swift`

---

### ✅ ЭТАП 5: Добавить Recursion Depth Monitoring

**Цель:** Отслеживать глубину рекурсии перед крашем

**Что добавить:**
```swift
// Глобальный счетчик глубины рекурсии
var recursionDepth: Int = 0
let maxRecursionDepth = 100

func checkRecursionDepth(function: String) {
    recursionDepth += 1
    
    if recursionDepth > maxRecursionDepth {
        let log = """
        🔴 EXCESSIVE RECURSION DETECTED!
        Function: \(function)
        Depth: \(recursionDepth)
        Time: \(Date())
        """
        
        UserDefaults.standard.set(log, forKey: "excessive_recursion_log")
        UserDefaults.standard.set(recursionDepth, forKey: "last_recursion_depth")
        
        print("🔴 EXCESSIVE RECURSION: \(function) depth=\(recursionDepth)")
    }
    
    defer { recursionDepth -= 1 }
}
```

**Файл:** Новый файл `Core/Diagnostics/RecursionMonitor.swift`

---

### ✅ ЭТАП 6: Добавить @AppStorage Access Monitoring

**Цель:** Отслеживать все обращения к @AppStorage

**Что добавить:**
```swift
// Обертка для @AppStorage с мониторингом
@propertyWrapper
struct MonitoredAppStorage<T> {
    private let key: String
    private let defaultValue: T
    
    @State private var value: T
    
    init(_ key: String, defaultValue: T) {
        self.key = key
        self.defaultValue = defaultValue
        self._value = State(initialValue: UserDefaults.standard.object(forKey: key) as? T ?? defaultValue)
    }
    
    var wrappedValue: T {
        get {
            let startTime = Date()
            let result = UserDefaults.standard.object(forKey: key) as? T ?? defaultValue
            let duration = Date().timeIntervalSince(startTime)
            
            if duration > 0.05 {
                let log = """
                ⚠️ SLOW @AppStorage READ
                Key: \(key)
                Duration: \(duration * 1000) ms
                Time: \(Date())
                """
                UserDefaults.standard.set(log, forKey: "slow_appstorage_log")
                print("⚠️ SLOW @AppStorage READ: \(key) took \(duration * 1000) ms")
            }
            
            return result
        }
        set {
            let startTime = Date()
            UserDefaults.standard.set(newValue, forKey: key)
            let duration = Date().timeIntervalSince(startTime)
            
            if duration > 0.05 {
                let log = """
                ⚠️ SLOW @AppStorage WRITE
                Key: \(key)
                Duration: \(duration * 1000) ms
                Time: \(Date())
                """
                UserDefaults.standard.set(log, forKey: "slow_appstorage_log")
                print("⚠️ SLOW @AppStorage WRITE: \(key) took \(duration * 1000) ms")
            }
        }
    }
}
```

**Файл:** Новый файл `Core/Diagnostics/MonitoredAppStorage.swift`

---

### ✅ ЭТАП 7: Добавить Pre-Crash State Saving

**Цель:** Сохранять состояние приложения перед крашем

**Что добавить:**
```swift
// В AppDelegate или отдельный файл
func savePreCrashState() {
    let state = [
        "memory_usage_mb": getMemoryUsageMB(),
        "active_threads": Thread.activeThreadCount,
        "stack_size_kb": getMainThreadStackSize(),
        "timestamp": Date().timeIntervalSince1970,
        "screen": navigationManager.currentScreen.rawValue,
        "app_state": UIApplication.shared.applicationState.rawValue
    ]
    
    if let data = try? JSONSerialization.data(withJSONObject: state) {
        UserDefaults.standard.set(data, forKey: "pre_crash_state")
        UserDefaults.standard.synchronize()
    }
}

// Вызывать периодически (каждые 5 секунд)
Timer.scheduledTimer(withTimeInterval: 5.0, repeats: true) { _ in
    savePreCrashState()
}
```

**Файл:** Новый файл `Core/Diagnostics/PreCrashStateSaver.swift`

---

### ✅ ЭТАП 8: Улучшить Visual Logger для Production

**Цель:** Показывать логи на экране даже в RELEASE режиме (опционально)

**Что добавить:**
```swift
// В VisualLogger.swift
#if DEBUG
// Показываем всегда в DEBUG
#else
// В RELEASE показываем только если включен флаг
if UserDefaults.standard.bool(forKey: "enable_visual_logging_release") {
    // Показываем логи
}
#endif
```

**Файл:** `Core/Utilities/VisualLogger.swift`

---

### ✅ ЭТАП 9: Добавить Crash Report Viewer в Settings

**Цель:** Позволить пользователю просматривать краши в приложении

**Что добавить:**
```swift
// В SettingsScreen.swift
Section("Диагностика") {
    Button("Просмотреть логи крашей") {
        showCrashLogs = true
    }
    Button("Отправить логи на сервер") {
        sendCrashLogsToServer()
    }
}
.sheet(isPresented: $showCrashLogs) {
    CrashLogsView()
}
```

**Файл:** Новый файл `Screens/CrashLogsView.swift`

---

### ✅ ЭТАП 10: Добавить Symbolication для Stack Traces

**Цель:** Расшифровать адреса в stack trace в читаемые имена функций

**Что добавить:**
```swift
// Использовать atos для symbolication
func symbolicateStackTrace(_ stackTrace: [String]) -> [String] {
    // Запустить atos для каждого адреса
    // Вернуть расшифрованные имена функций
}
```

**Файл:** Новый файл `Core/Diagnostics/Symbolicator.swift`

---

## 📊 ПРИОРИТЕТЫ РЕАЛИЗАЦИИ

### 🔴 КРИТИЧНО (делать первым):
1. ✅ **Memory Warning Handler** - отслеживать нехватку памяти
2. ✅ **Pre-Crash State Saving** - сохранять состояние перед крашем
3. ✅ **UserDefaults Performance Monitoring** - отслеживать медленные операции

### 🟡 ВАЖНО (делать вторым):
4. ✅ **Stack Size Monitoring** - отслеживать использование stack
5. ✅ **Recursion Depth Monitoring** - отслеживать глубину рекурсии
6. ✅ **Thread Monitoring** - отслеживать потоки

### 🟢 ЖЕЛАТЕЛЬНО (делать третьим):
7. ✅ **@AppStorage Access Monitoring** - отслеживать обращения к @AppStorage
8. ✅ **Crash Report Viewer** - просмотр крашей в приложении
9. ✅ **Symbolication** - расшифровка stack traces
10. ✅ **Visual Logger для Production** - показывать логи в RELEASE

---

## 🎯 ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ

После реализации всех этапов:
- ✅ Будем знать точную причину краша на реальном устройстве
- ✅ Будем видеть состояние памяти перед крашем
- ✅ Будем видеть медленные операции с UserDefaults
- ✅ Будем видеть глубину рекурсии перед крашем
- ✅ Будем видеть использование stack перед крашем

---

## 📝 СЛЕДУЮЩИЕ ШАГИ

1. Реализовать критические этапы (1-3)
2. Протестировать на реальном устройстве
3. Собрать данные о крашах
4. Проанализировать данные
5. Исправить найденные проблемы
