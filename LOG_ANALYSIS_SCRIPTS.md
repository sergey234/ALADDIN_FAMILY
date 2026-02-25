# 🔍 СКРИПТЫ АНАЛИЗА ЛОГОВ ДЛЯ XCODE

## 🎯 ГОТОВЫЕ СКРИПТЫ ДЛЯ АНАЛИЗА API

**Копируйте эти скрипты в Xcode debugger для мгновенного анализа**

---

## 📊 ОСНОВНОЙ АНАЛИЗАТОР API

### **Скрипт 1: Полный анализ всех API**
```swift
// В Xcode debugger выполните:
let logs = VisualLogger.shared.allLogsText
print("=== API ANALYSIS START ===")

// Разбор логов по типам
let lines = logs.components(separatedBy: "\n")
var apiRequests = 0
var apiResponses = 0
var successfulAPIs = 0
var failedAPIs = 0
var responseTimes: [Double] = []

for line in lines {
    if line.contains("➡️") && line.contains("REQUEST") {
        apiRequests += 1
        print("📤 REQUEST: \(line)")
    } else if line.contains("⬅️") && line.contains("RESPONSE") {
        apiResponses += 1

        // Проверка статуса
        if let statusRange = line.range(of: "status=") {
            let statusText = line[statusRange.upperBound...]
            if let statusCode = Int(statusText.prefix(3)) {
                if (200...299).contains(statusCode) {
                    successfulAPIs += 1
                    print("✅ SUCCESS: \(line)")
                } else {
                    failedAPIs += 1
                    print("❌ FAILED: \(line)")
                }
            }
        }
    } else if line.contains("📊") && line.contains("seconds") {
        // Извлечение времени ответа
        if let timeRange = line.range(of: "completed in "),
           let endRange = line.range(of: " seconds") {
            let timeText = line[timeRange.upperBound..<endRange.lowerBound]
            if let time = Double(timeText) {
                responseTimes.append(time)
            }
        }
    }
}

print("\n=== API ANALYSIS RESULTS ===")
print("📊 Total Requests: \(apiRequests)")
print("📊 Total Responses: \(apiResponses)")
print("✅ Successful APIs: \(successfulAPIs)")
print("❌ Failed APIs: \(failedAPIs)")
print("📈 Success Rate: \(String(format: "%.1f%%", Double(successfulAPIs) / Double(apiResponses) * 100))")

if !responseTimes.isEmpty {
    let avgTime = responseTimes.reduce(0, +) / Double(responseTimes.count)
    print("⏱️ Average Response Time: \(String(format: "%.2f", avgTime))s")
    print("🏃 Min Time: \(String(format: "%.2f", responseTimes.min() ?? 0))s")
    print("🐌 Max Time: \(String(format: "%.2f", responseTimes.max() ?? 0))s")
}

print("=== END ANALYSIS ===")
```

---

## 🔍 АНАЛИЗАТОР КОНКРЕТНЫХ API

### **Скрипт 2: Анализ конкретной endpoint**
```swift
// Замените "profile" на нужную endpoint
let targetEndpoint = "profile"

let logs = VisualLogger.shared.allLogsText
let lines = logs.components(separatedBy: "\n")

print("=== ANALYSIS FOR: \(targetEndpoint) ===")

for line in lines {
    if line.contains(targetEndpoint) {
        if line.contains("➡️") {
            print("📤 REQUEST: \(line)")
        } else if line.contains("⬅️") {
            print("📥 RESPONSE: \(line)")

            // Детальный анализ ответа
            if let statusRange = line.range(of: "status=") {
                let statusStr = String(line[statusRange.upperBound...].prefix(3))
                if let status = Int(statusStr) {
                    switch status {
                    case 200...299:
                        print("   ✅ SUCCESS (\(status))")
                    case 400...499:
                        print("   ⚠️ CLIENT ERROR (\(status))")
                    case 500...599:
                        print("   ❌ SERVER ERROR (\(status))")
                    default:
                        print("   ❓ UNKNOWN (\(status))")
                    }
                }
            }
        }
    }
}
```

---

## 📈 АНАЛИЗАТОР ПРОИЗВОДИТЕЛЬНОСТИ

### **Скрипт 3: Анализ производительности**
```swift
let logs = VisualLogger.shared.allLogsText
let lines = logs.components(separatedBy: "\n")

print("=== PERFORMANCE ANALYSIS ===")

var initTime: Double = 0
var apiResponseTimes: [Double] = []
var slowRequests: [(String, Double)] = []

for line in lines {
    if line.contains("App initialization completed in") {
        if let timeRange = line.range(of: "completed in "),
           let endRange = line.range(of: " seconds") {
            let timeText = String(line[timeRange.upperBound..<endRange.lowerBound])
            initTime = Double(timeText) ?? 0
        }
    } else if line.contains("📊") && line.contains("seconds") && !line.contains("App init") {
        // API response times
        if let timeRange = line.range(of: "in "),
           let endRange = line.range(of: " seconds") {
            let timeText = String(line[timeRange.upperBound..<endRange.lowerBound])
            if let time = Double(timeText) {
                apiResponseTimes.append(time)

                if time > 3.0 { // Медленные запросы
                    slowRequests.append((line, time))
                }
            }
        }
    }
}

print("🚀 App Init Time: \(String(format: "%.2f", initTime))s")
print("📊 API Requests: \(apiResponseTimes.count)")

if !apiResponseTimes.isEmpty {
    let avgTime = apiResponseTimes.reduce(0, +) / Double(apiResponseTimes.count)
    print("⏱️ Average API Time: \(String(format: "%.2f", avgTime))s")
    print("🏃 Fastest: \(String(format: "%.2f", apiResponseTimes.min() ?? 0))s")
    print("🐌 Slowest: \(String(format: "%.2f", apiResponseTimes.max() ?? 0))s")
}

if !slowRequests.isEmpty {
    print("\n🐌 SLOW REQUESTS (>3s):")
    for (request, time) in slowRequests {
        print("   \(String(format: "%.2f", time))s - \(request)")
    }
}

print("=== END PERFORMANCE ANALYSIS ===")
```

---

## 🔍 АНАЛИЗАТОР ОШИБОК

### **Скрипт 4: Поиск всех ошибок**
```swift
let logs = VisualLogger.shared.allLogsText
let lines = logs.components(separatedBy: "\n")

print("=== ERROR ANALYSIS ===")

var errors: [String] = []
var warnings: [String] = []
var networkErrors: [String] = []

for line in lines {
    if line.contains("❌") || line.contains("ERROR") {
        errors.append(line)
    } else if line.contains("⚠️") || line.contains("WARNING") {
        warnings.append(line)
    } else if line.contains("status=") {
        if let statusRange = line.range(of: "status=") {
            let statusStr = String(line[statusRange.upperBound...].prefix(3))
            if let status = Int(statusStr), status >= 400 {
                networkErrors.append(line)
            }
        }
    }
}

print("🚨 Critical Errors: \(errors.count)")
for error in errors {
    print("   \(error)")
}

print("\n⚠️ Warnings: \(warnings.count)")
for warning in warnings {
    print("   \(warning)")
}

print("\n🌐 Network Errors: \(networkErrors.count)")
for error in networkErrors {
    print("   \(error)")
}

print("\n=== RECOMMENDATIONS ===")
if errors.count > 0 {
    print("🔴 Fix critical errors immediately!")
}
if warnings.count > 5 {
    print("🟡 Review warnings for potential issues")
}
if networkErrors.count > 0 {
    print("🔵 Check network/API issues")
}
```

---

## 📊 СВОДНЫЙ ОТЧЕТ

### **Скрипт 5: Полный отчет о системе**
```swift
let logs = VisualLogger.shared.allLogsText
let lines = logs.components(separatedBy: "\n")

print("=== SYSTEM HEALTH REPORT ===")
print("Generated: \(Date())")

// Подсчет компонентов
var masterLoggerInit = false
var localizationReady = false
var storeManagerReady = false
var networkManagerReady = false
var userProfileLoaded = false
var pushNotificationsReady = false
var appInitTime: Double = 0

for line in lines {
    if line.contains("MasterLogger initialized") {
        masterLoggerInit = true
    } else if line.contains("LocalizationManager: Ready") {
        localizationReady = true
    } else if line.contains("StoreManager") && line.contains("initialized") {
        storeManagerReady = true
    } else if line.contains("NetworkManager.init: Завершен") {
        networkManagerReady = true
    } else if line.contains("UserProfileManager initialized") {
        userProfileLoaded = true
    } else if line.contains("Push notifications authorized") {
        pushNotificationsReady = true
    } else if line.contains("App initialization completed in") {
        if let timeRange = line.range(of: "completed in "),
           let endRange = line.range(of: " seconds") {
            let timeText = String(line[timeRange.upperBound..<endRange.lowerBound])
            appInitTime = Double(timeText) ?? 0
        }
    }
}

// Оценка здоровья системы
let components = [
    ("MasterLogger", masterLoggerInit),
    ("Localization", localizationReady),
    ("Store Manager", storeManagerReady),
    ("Network Manager", networkManagerReady),
    ("User Profile", userProfileLoaded),
    ("Push Notifications", pushNotificationsReady)
]

let healthyComponents = components.filter { $0.1 }.count
let totalComponents = components.count
let healthScore = Double(healthyComponents) / Double(totalComponents)

print("🏥 System Health: \(String(format: "%.0f%%", healthScore * 100)) (\(healthyComponents)/\(totalComponents))")

print("\n📋 Component Status:")
for (name, status) in components {
    let icon = status ? "✅" : "❌"
    print("   \(icon) \(name)")
}

print("\n⏱️ Performance:")
print("   App Init Time: \(String(format: "%.2f", appInitTime))s \(appInitTime < 3.0 ? "✅" : "🐌")")

print("\n🎯 Recommendations:")
if healthScore < 0.8 {
    print("   🔴 System health is poor - investigate failed components")
} else if healthScore >= 0.8 && healthScore < 1.0 {
    print("   🟡 Some components failed - check logs for details")
} else {
    print("   🟢 All systems operational")
}

if appInitTime > 5.0 {
    print("   🐌 App startup is slow - optimize initialization")
} else if appInitTime <= 2.0 {
    print("   🚀 Excellent startup performance")
}
```

---

## 🎯 ИСПОЛЬЗОВАНИЕ

### **Как запустить скрипт:**

1. **Запустите приложение** в Xcode
2. **Выполните действия** (логин, платежи, etc.)
3. **Остановите отладку** (Stop button)
4. **В Xcode Console** введите: `po [скрипт]`
5. **Скопируйте результат** для анализа

### **Пример запуска:**
```
// В Xcode Console:
po let logs = VisualLogger.shared.allLogsText; print("Total logs: \(logs.components(separatedBy: "\n").count)")
```

### **Горячие клавиши:**
- **Cmd+Shift+Y** - показать/hide Debug Console
- **po** - print object в debugger
- **p** - print primitive value

---

## 📈 АВТОМАТИЗАЦИЯ

### **Добавить в приложение:**
```swift
// В Settings добавить кнопку анализа
Button("🔍 Анализ системы") {
    let logs = VisualLogger.shared.allLogsText
    let report = generateHealthReport(logs)
    showReport(report)
}
```

---

## 🎉 РЕЗУЛЬТАТ

**Эти скрипты позволяют:**
- ✅ **Мгновенно анализировать** состояние всех API
- ✅ **Выявлять проблемы** производительности
- ✅ **Создавать отчеты** о здоровье системы
- ✅ **Отлаживать** проблемы без перезапуска

**Запустите любой скрипт в Xcode debugger - получите полный анализ системы за секунды!** 🚀🔍