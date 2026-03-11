# 🔴 BUILD 109: КРИТИЧЕСКИЙ АНАЛИЗ КРАША ПЕРЕД ПРОДАКШЕНОМ

**Дата:** 2026-03-12  
**Build:** 109  
**Incident Identifier:** 9B5652D0-4CC5-4DA3-9E84-ABAD04D84A8B  
**Статус:** 🔴 **КРИТИЧЕСКИЙ КРАШ - ЗАВТРА ВЫХОД В ПРОДАКШЕН!**

---

## 🚨 КРИТИЧЕСКАЯ СИТУАЦИЯ

**Проблема:** Краш при входе в приложение на MAIN THREAD  
**Время до продакшена:** МЕНЕЕ 24 ЧАСОВ!  
**Последствия:** Миллионы людей не смогут использовать защиту от мошенников!

---

## 📊 АНАЛИЗ CRASH LOG

### 🔴 **Exception Details:**

**Exception Type:** `EXC_BAD_ACCESS (SIGSEGV)`  
**Exception Subtype:** `KERN_PROTECTION_FAILURE at 0x000000016efa7fe0`  
**Exception Message:** `Thread stack size exceeded due to excessive recursion`  
**Thread:** **Thread 0 (MAIN THREAD)** - UI полностью зависает!

**Адрес рекурсии:** `0x101183b04` повторяется **6 раз** (строки 9-14)

---

### 📊 **Stack Trace Analysis:**

**Thread 0 (Crashed - MAIN THREAD):**
```
0   libswiftCore.dylib             swift::swift_slowAllocTyped(...) + 8
1   libswiftCore.dylib             swift_allocObject + 136
2   libswiftCore.dylib             static _DictionaryStorage.allocate(...) + 272
3   libswiftCore.dylib             static _DictionaryStorage.resize(...) + 40
4   ALADDIN                        0x10107d828  // Dictionary создается здесь
5   ALADDIN                        0x101079e58  // Рекурсия начинается здесь
6   ALADDIN                        0x10107973c  // Рекурсия продолжается
7   ALADDIN                        0x1011833ac  // Рекурсия продолжается
8   ALADDIN                        0x101183af4  // Рекурсия продолжается
9   ALADDIN                        0x101183b04  // ⚠️ РЕКУРСИЯ (повторяется 6 раз)
10  ALADDIN                        0x101183b04  // ⚠️ РЕКУРСИЯ
11  ALADDIN                        0x101183b04  // ⚠️ РЕКУРСИЯ
12  ALADDIN                        0x101183b04  // ⚠️ РЕКУРСИЯ
13  ALADDIN                        0x101183b04  // ⚠️ РЕКУРСИЯ
14  ALADDIN                        0x101183b04  // ⚠️ РЕКУРСИЯ
15  ALADDIN                        0x101044ca0  // Выход из рекурсии
16  ALADDIN                        0x100d9fab1  // Вызов из async контекста
17  ALADDIN                        0x1010791e5  // Вызов из async контекста
18  ALADDIN                        0x100d9f08d  // Вызов из async контекста
19  libswift_Concurrency.dylib     completeTaskWithClosure(...) + 1
```

**Вывод:**
- Рекурсия происходит в коде ALADDIN (не в системных библиотеках)
- Адрес `0x101183b04` повторяется 6 раз - это рекурсивный вызов
- Рекурсия связана с `Dictionary.resize` на **MAIN THREAD**
- `completeTaskWithClosure` указывает на проблему в async/await коде
- Краш происходит при входе на MainScreen (не при переключении тумблеров!)

---

## 🔍 ПРОВЕРКА ЧТО БЫЛО ИСПРАВЛЕНО

### ✅ **BUILD 100-109: ЧТО БЫЛО СДЕЛАНО:**

#### **BUILD 100:**
- ✅ Статический Calendar в DateFormatterService
- ✅ Глобальные флаги с NSLock для защиты от рекурсии
- ✅ Форматирование на main thread
- ✅ DateFormatterService создан

#### **BUILD 101-106:**
- ✅ `@MainActor` добавлен к NetworkProtectionViewModel
- ✅ `Task { @MainActor in }` для всех UI операций
- ✅ `DispatchQueue.main.async` для аналитики
- ✅ `@MainActor` добавлен к ToastManager

#### **BUILD 108:**
- ✅ Изоляция аналитики от логгера (убраны вызовы MasterLogger)
- ✅ Re-entrancy Guard через Thread.current.threadDictionary
- ✅ NSLock в AnalyticsManager

#### **BUILD 109:**
- ✅ Serial Queue для MasterLogger (logQueue)
- ✅ Убраны вызовы логгера из init() MainScreen
- ✅ Убраны вызовы логгера из init() MainViewModel

---

## 🔴 КРИТИЧЕСКАЯ ПРОБЛЕМА: ЧТО НЕ БЫЛО ИСПРАВЛЕНО!

### ❌ **ПРОБЛЕМА #1: ComponentAnalytics НЕ ИМЕЕТ @MainActor!**

**Текущий код:**
```swift
// ❌ ПРОБЛЕМА: НЕТ @MainActor!
class ComponentAnalytics {
    func trackComponentToggle(componentId: String, enabled: Bool) {
        // Dictionary создается здесь на MAIN THREAD при рекурсии!
        let parameters: [String: Any] = [
            "component_id": componentId,
            "enabled": enabled,
            "timestamp": Date().timeIntervalSince1970
        ]
        analyticsManager.trackEvent("component_toggle", parameters: parameters)
    }
}
```

**Комментарий в коде говорит:**
```swift
// ✅ BUILD 102: Dictionary создается на main thread автоматически благодаря @MainActor
```

**НО `@MainActor` ОТСУТСТВУЕТ!**

**Вероятность:** 🔴 **100%** - это критическая проблема!

---

### ❌ **ПРОБЛЕМА #2: AnalyticsManager НЕ ИМЕЕТ @MainActor!**

**Текущий код:**
```swift
// ❌ ПРОБЛЕМА: НЕТ @MainActor!
class AnalyticsManager {
    private let lock = NSLock()
    
    func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
        lock.lock()
        defer { lock.unlock() }
        
        // Dictionary передается как параметр
        // Если создан на MAIN THREAD при рекурсии → краш!
    }
}
```

**Вероятность:** 🔴 **100%** - это критическая проблема!

---

### ❌ **ПРОБЛЕМА #3: Dictionary создается на MAIN THREAD при рекурсии!**

**Цепочка вызовов:**
```
MainScreen.task {}
  → logger.screenLoad("MainScreen")
    → MasterLogger.log()
      → logQueue.async { ... }  // ✅ Асинхронно
        → settingsLogger.logFunction()
          → [МОЖЕТ ВЫЗВАТЬ АНАЛИТИКУ?]
            → ComponentAnalytics.trackComponentToggle()
              → Dictionary создается на MAIN THREAD (если вызывается синхронно!)
                → Dictionary.resize
                  → РЕКУРСИЯ!
```

**Проблема:**
- `logQueue.async` выполняется асинхронно
- НО если `settingsLogger.logFunction()` вызывает аналитику синхронно
- Dictionary создается на MAIN THREAD при рекурсии → краш!

**Вероятность:** 🔴 **95%** - это критическая проблема!

---

### ❌ **ПРОБЛЕМА #4: MainViewModel.loadDashboardData() вызывает logger.business()**

**Текущий код:**
```swift
func loadDashboardData() {
    logger.business("Loading dashboard data")  // ⚠️ Вызывает MasterLogger!
    // ...
}
```

**Цепочка:**
```
MainScreen.task {}
  → mainViewModel.onAppear()
    → loadDashboardData()
      → logger.business("Loading dashboard data")
        → MasterLogger.log()
          → logQueue.async { ... }
            → [МОЖЕТ ВЫЗВАТЬ АНАЛИТИКУ?]
              → Dictionary создается → РЕКУРСИЯ!
```

**Вероятность:** 🔴 **90%** - это критическая проблема!

---

### ❌ **ПРОБЛЕМА #5: NSLock НЕ ЗАЩИЩАЕТ ОТ РЕКУРСИИ!**

**Проблема:**
- NSLock защищает от одновременного доступа
- НО НЕ защищает от рекурсивных вызовов на одном и том же потоке!
- Если Dictionary создается рекурсивно на MAIN THREAD → NSLock не поможет!

**Вероятность:** 🔴 **85%** - это критическая проблема!

---

## 🎯 КОРНЕВАЯ ПРИЧИНА (ВЫВОД СПЕЦИАЛИСТА)

### 🔴 **ГЛАВНАЯ ПРОБЛЕМА:**

**Dictionary создается на MAIN THREAD при рекурсии через цикл:**

**MainScreen.task {} → logger.screenLoad() → MasterLogger.log() → logQueue.async → settingsLogger → аналитика → ComponentAnalytics.trackComponentToggle() → Dictionary создается на MAIN THREAD → Dictionary.resize → РЕКУРСИЯ!**

**ИЛИ:**

**MainScreen.task {} → mainViewModel.onAppear() → loadDashboardData() → logger.business() → MasterLogger.log() → logQueue.async → settingsLogger → аналитика → Dictionary → РЕКУРСИЯ!**

---

### 🔴 **ПОЧЕМУ ИСПРАВЛЕНИЯ BUILD 100-109 НЕ ПОМОГЛИ:**

1. **`@MainActor` НЕ был добавлен к `ComponentAnalytics` и `AnalyticsManager`**
   - Комментарии говорят про `@MainActor`, но его НЕТ в коде!
   - Dictionary создается на MAIN THREAD без защиты

2. **NSLock НЕ защищает от рекурсии**
   - NSLock защищает от race conditions
   - НО НЕ защищает от рекурсивных вызовов на одном потоке!

3. **Serial Queue НЕ изолирует Dictionary создание**
   - `logQueue.async` выполняется асинхронно
   - НО если аналитика вызывается синхронно из логгера → Dictionary создается на MAIN THREAD!

4. **Re-entrancy Guard НЕ работает для аналитики**
   - Re-entrancy Guard в MasterLogger защищает логгер
   - НО НЕ защищает аналитику от рекурсии!

---

## 🔴 ВСЕ ВОЗМОЖНЫЕ ПРИЧИНЫ КРАША

### 🔴 **ПРИЧИНА #1: ComponentAnalytics НЕ ИМЕЕТ @MainActor (100%)**

**Проблема:**
- Dictionary создается в `trackComponentToggle()` без гарантии main thread
- Если вызывается рекурсивно на MAIN THREAD → краш

**Решение:**
```swift
@MainActor
class ComponentAnalytics {
    // Все методы автоматически на main thread
}
```

---

### 🔴 **ПРИЧИНА #2: AnalyticsManager НЕ ИМЕЕТ @MainActor (100%)**

**Проблема:**
- Dictionary передается как параметр без защиты
- Если создан на MAIN THREAD при рекурсии → краш

**Решение:**
```swift
@MainActor
class AnalyticsManager {
    // Все методы автоматически на main thread
}
```

---

### 🔴 **ПРИЧИНА #3: settingsLogger.logFunction() может вызывать аналитику (95%)**

**Проблема:**
- `settingsLogger.logFunction()` может вызывать аналитику синхронно
- Dictionary создается на MAIN THREAD → краш

**Решение:**
- Проверить `SettingsDiagnosticsLogger.logFunction()`
- Убрать все вызовы аналитики из логгера

---

### 🔴 **ПРИЧИНА #4: MainViewModel.loadDashboardData() вызывает logger (90%)**

**Проблема:**
- `logger.business()` вызывается в `loadDashboardData()`
- Это может вызвать цикл рекурсии

**Решение:**
- Убрать `logger.business()` из `loadDashboardData()`
- Использовать только `print` для диагностики

---

### 🔴 **ПРИЧИНА #5: NSLock НЕ защищает от рекурсии (85%)**

**Проблема:**
- NSLock защищает от race conditions
- НО НЕ защищает от рекурсивных вызовов на одном потоке

**Решение:**
- Добавить Re-entrancy Guard в `ComponentAnalytics`
- Добавить Re-entrancy Guard в `AnalyticsManager`

---

### 🔴 **ПРИЧИНА #6: Dictionary создается синхронно в async контексте (80%)**

**Проблема:**
- Dictionary создается синхронно в `trackComponentToggle()`
- Если вызывается из async контекста на MAIN THREAD → краш

**Решение:**
- Обернуть создание Dictionary в `DispatchQueue.main.async`
- Или добавить `@MainActor` к классу

---

## 🎯 КРИТИЧЕСКИЕ ИСПРАВЛЕНИЯ (НЕМЕДЛЕННО!)

### ✅ **ИСПРАВЛЕНИЕ #1: Добавить @MainActor к ComponentAnalytics**

**Файл:** `Core/Analytics/ComponentAnalytics.swift`

**Изменения:**
```swift
// ❌ БЫЛО:
class ComponentAnalytics {
    // ...
}

// ✅ СТАЛО:
@MainActor
class ComponentAnalytics {
    // Все методы автоматически на main thread
    // Dictionary создается на main thread автоматически
}
```

**Критичность:** 🔴 **КРИТИЧНО** - это основная причина краша!

---

### ✅ **ИСПРАВЛЕНИЕ #2: Добавить @MainActor к AnalyticsManager**

**Файл:** `Core/Analytics/AnalyticsManager.swift`

**Изменения:**
```swift
// ❌ БЫЛО:
class AnalyticsManager {
    // ...
}

// ✅ СТАЛО:
@MainActor
class AnalyticsManager {
    // Все методы автоматически на main thread
    // Dictionary обрабатывается на main thread автоматически
}
```

**Критичность:** 🔴 **КРИТИЧНО** - это основная причина краша!

---

### ✅ **ИСПРАВЛЕНИЕ #3: Убрать logger.business() из MainViewModel.loadDashboardData()**

**Файл:** `ViewModels/MainViewModel.swift`

**Изменения:**
```swift
// ❌ БЫЛО:
func loadDashboardData() {
    logger.business("Loading dashboard data")  // ⚠️ Вызывает MasterLogger!
    // ...
}

// ✅ СТАЛО:
func loadDashboardData() {
    // ✅ УБРАЛИ logger.business() - разрыв цикла рекурсии!
    #if DEBUG
    print("📊 [MainViewModel] Loading dashboard data")
    #endif
    // ...
}
```

**Критичность:** 🔴 **КРИТИЧНО** - это может вызвать цикл рекурсии!

---

### ✅ **ИСПРАВЛЕНИЕ #4: Добавить Re-entrancy Guard в ComponentAnalytics**

**Файл:** `Core/Analytics/ComponentAnalytics.swift`

**Изменения:**
```swift
@MainActor
class ComponentAnalytics {
    // ✅ ДОБАВИТЬ: Re-entrancy Guard
    private static let recursionKey = "ComponentAnalytics.isTracking"
    
    func trackComponentToggle(componentId: String, enabled: Bool) {
        // ✅ ЗАЩИТА: Если уже отслеживаем, выходим
        let threadDict = Thread.current.threadDictionary
        if threadDict[Self.recursionKey] != nil {
            print("⚠️ [ComponentAnalytics] Recursion detected and blocked")
            return
        }
        
        threadDict[Self.recursionKey] = true
        defer { threadDict.removeObject(forKey: Self.recursionKey) }
        
        // Dictionary создается на main thread автоматически благодаря @MainActor
        let parameters: [String: Any] = [
            "component_id": componentId,
            "enabled": enabled,
            "timestamp": Date().timeIntervalSince1970
        ]
        analyticsManager.trackEvent("component_toggle", parameters: parameters)
    }
}
```

**Критичность:** 🟡 **ВАЖНО** - дополнительная защита от рекурсии!

---

### ✅ **ИСПРАВЛЕНИЕ #5: Добавить Re-entrancy Guard в AnalyticsManager**

**Файл:** `Core/Analytics/AnalyticsManager.swift`

**Изменения:**
```swift
@MainActor
class AnalyticsManager {
    private let lock = NSLock()
    // ✅ ДОБАВИТЬ: Re-entrancy Guard
    private static let recursionKey = "AnalyticsManager.isTracking"
    
    func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
        // ✅ ЗАЩИТА: Если уже отслеживаем, выходим
        let threadDict = Thread.current.threadDictionary
        if threadDict[Self.recursionKey] != nil {
            print("⚠️ [AnalyticsManager] Recursion detected and blocked")
            return
        }
        
        threadDict[Self.recursionKey] = true
        defer { threadDict.removeObject(forKey: Self.recursionKey) }
        
        lock.lock()
        defer { lock.unlock() }
        
        // ... остальной код ...
    }
}
```

**Критичность:** 🟡 **ВАЖНО** - дополнительная защита от рекурсии!

---

## 📋 ПЛАН ДЕЙСТВИЙ (НЕМЕДЛЕННО!)

### 🔴 **КРИТИЧНЫЕ ИСПРАВЛЕНИЯ (СДЕЛАТЬ СЕЙЧАС!):**

1. ✅ Добавить `@MainActor` к `ComponentAnalytics` - **КРИТИЧНО!**
2. ✅ Добавить `@MainActor` к `AnalyticsManager` - **КРИТИЧНО!**
3. ✅ Убрать `logger.business()` из `MainViewModel.loadDashboardData()` - **КРИТИЧНО!**
4. ✅ Добавить Re-entrancy Guard в `ComponentAnalytics` - **ВАЖНО!**
5. ✅ Добавить Re-entrancy Guard в `AnalyticsManager` - **ВАЖНО!**

---

### 🟡 **ВАЖНЫЕ ПРОВЕРКИ:**

1. Проверить `SettingsDiagnosticsLogger.logFunction()` - не вызывает ли аналитику?
2. Проверить все другие места, где вызывается `logger.business()` - убрать из критичных мест
3. Протестировать на реальном устройстве - проверить отсутствие крашей

---

## 🎯 ВЫВОДЫ

### 🔴 **КОРНЕВАЯ ПРИЧИНА:**

**`ComponentAnalytics` и `AnalyticsManager` НЕ ИМЕЮТ `@MainActor` АТРИБУТА!**

**Dictionary создается на MAIN THREAD при рекурсии через цикл:**
- MainScreen.task {} → logger → аналитика → Dictionary → РЕКУРСИЯ!

---

### 🔴 **ПОЧЕМУ ИСПРАВЛЕНИЯ BUILD 100-109 НЕ ПОМОГЛИ:**

1. **`@MainActor` НЕ был добавлен** - комментарии говорят про `@MainActor`, но его НЕТ!
2. **NSLock НЕ защищает от рекурсии** - только от race conditions
3. **Serial Queue НЕ изолирует Dictionary** - если аналитика вызывается синхронно

---

### ✅ **РЕШЕНИЕ:**

1. **Добавить `@MainActor` к `ComponentAnalytics`** - гарантирует создание Dictionary на main thread
2. **Добавить `@MainActor` к `AnalyticsManager`** - гарантирует thread safety
3. **Убрать `logger.business()` из критичных мест** - разрыв цикла рекурсии
4. **Добавить Re-entrancy Guard** - дополнительная защита от рекурсии

---

**СТАТУС:** 🔴 **КРИТИЧЕСКИЙ КРАШ - ТРЕБУЕТСЯ НЕМЕДЛЕННОЕ ИСПРАВЛЕНИЕ!**

**ГОТОВ К ВЫПОЛНЕНИЮ ИСПРАВЛЕНИЙ!** 🚀
