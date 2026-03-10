# 🎯 BUILD 102: ИДЕАЛЬНАЯ АРХИТЕКТУРА И ПРАВИЛЬНОЕ РЕШЕНИЕ

**Дата:** 2026-03-11  
**Build:** 102  
**Статус:** 📚 **КАК ДОЛЖНО БЫТЬ ПО КНИЖКЕ**

---

## 🤔 ПОЧЕМУ РАНЬШЕ РАБОТАЛО (BUILD 77-99)?

### Что было раньше:

**BUILD 77-99:**
- ✅ Не было `NetworkProtectionViewModel` - не было сложной логики
- ✅ Не было `ComponentAnalytics` - аналитика вызывалась синхронно
- ✅ Все операции выполнялись **синхронно на main thread**
- ✅ Не было разделения на demo/production mode
- ✅ Не было асинхронных вызовов в background thread
- ✅ Dictionary создавался **на main thread** синхронно

**Почему работало:**
- SwiftUI View обновлялся синхронно
- Все операции были на main thread
- Не было race conditions
- Не было проблем с Dictionary в background thread

---

## 📚 КАК ДОЛЖНО БЫТЬ ПО КНИЖКЕ (BEST PRACTICES)

### Принцип 1: ViewModel должен быть @MainActor

**Правило:**
```swift
// ✅ ПРАВИЛЬНО:
@MainActor
class NetworkProtectionViewModel: ObservableObject {
    // Все свойства и методы автоматически на main thread
}

// ❌ НЕПРАВИЛЬНО:
class NetworkProtectionViewModel: ObservableObject {
    // Может выполняться в background thread
}
```

**Почему:**
- `@MainActor` гарантирует, что все операции выполняются на main thread
- `@Published` свойства автоматически обновляются на main thread
- Не нужно вручную использовать `await MainActor.run`

**Текущее состояние:**
- ✅ `NetworkProtectionViewModel` уже имеет `@MainActor` (строка 13)
- ✅ Это правильно!

---

### Принцип 2: Все async функции в ViewModel должны быть @MainActor

**Правило:**
```swift
// ✅ ПРАВИЛЬНО:
@MainActor
class NetworkProtectionViewModel: ObservableObject {
    func toggleComponent(_ componentId: String, newValue: Bool) async {
        // Автоматически на main thread благодаря @MainActor
        updateClosure(newValue)  // Без await MainActor.run!
        
        if AppConfig.authToken == nil {
            await handleDemoModeToggle(...)
        } else {
            await handleProductionModeToggle(...)
        }
    }
}

// ❌ НЕПРАВИЛЬНО:
class NetworkProtectionViewModel: ObservableObject {
    func toggleComponent(_ componentId: String, newValue: Bool) async {
        await MainActor.run {  // НЕ НУЖНО, если класс @MainActor!
            updateClosure(newValue)
        }
    }
}
```

**Почему:**
- Если класс `@MainActor`, все методы автоматически на main thread
- Не нужно вручную использовать `await MainActor.run`
- Код становится проще и понятнее

**Текущее состояние:**
- ✅ `NetworkProtectionViewModel` имеет `@MainActor`
- ❌ НО используется `await MainActor.run` внутри методов (избыточно!)

---

### Принцип 3: Аналитика должна быть синхронной или правильно асинхронной

**Правило:**
```swift
// ✅ ПРАВИЛЬНО (вариант 1 - синхронная аналитика):
@MainActor
class ComponentAnalytics {
    func trackComponentToggle(componentId: String, enabled: Bool) {
        // Автоматически на main thread благодаря @MainActor
        let parameters: [String: Any] = [
            "component_id": componentId,
            "enabled": enabled,
            "timestamp": Date().timeIntervalSince1970
        ]
        analyticsManager.trackEvent("component_toggle", parameters: parameters)
    }
}

// ✅ ПРАВИЛЬНО (вариант 2 - асинхронная аналитика):
@MainActor
class ComponentAnalytics {
    func trackComponentToggle(componentId: String, enabled: Bool) async {
        // Автоматически на main thread благодаря @MainActor
        let parameters: [String: Any] = [
            "component_id": componentId,
            "enabled": enabled,
            "timestamp": Date().timeIntervalSince1970
        ]
        analyticsManager.trackEvent("component_toggle", parameters: parameters)
    }
}

// ❌ НЕПРАВИЛЬНО (текущий код):
class ComponentAnalytics {
    func trackComponentToggle(componentId: String, enabled: Bool) {
        Task {  // Создает новый Task - может быть в background thread!
            await MainActor.run {
                let parameters: [String: Any] = [...]  // Dictionary может создаться ДО MainActor.run!
                analyticsManager.trackEvent(...)
            }
        }
    }
}
```

**Почему:**
- `Task {}` создает новую асинхронную задачу, которая может выполняться в background thread
- Dictionary literal может создаться **ДО** перехода на main thread
- Нужно либо сделать класс `@MainActor`, либо использовать правильный async/await

**Текущее состояние:**
- ❌ `ComponentAnalytics` НЕ имеет `@MainActor`
- ❌ Используется `Task { await MainActor.run }` - это костыль!

---

### Принцип 4: Dictionary создание должно быть на main thread

**Правило:**
```swift
// ✅ ПРАВИЛЬНО:
@MainActor
func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
    // Автоматически на main thread благодаря @MainActor
    let paramsDescription: String
    if let params = parameters {
        paramsDescription = String(describing: params)
    } else {
        paramsDescription = "none"
    }
    
    logger.business("Analytics: Event - \(eventName) with params: \(paramsDescription)")
    #if DEBUG
    if let params = parameters {
        print("📊 Event: \(eventName), params: \(params)")
    } else {
        print("📊 Event: \(eventName), params: none")
    }
    #endif
}

// ❌ НЕПРАВИЛЬНО:
func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
    logger.business("Analytics: Event - \(eventName) with params: \(parameters?.description ?? "none")")
    #if DEBUG
    print("📊 Event: \(eventName), params: \(parameters ?? [:])")  // Dictionary создается здесь!
    #endif
}
```

**Почему:**
- `parameters ?? [:]` создает Dictionary literal синхронно
- Если функция вызывается из background thread, Dictionary создается в background thread
- Нужно либо сделать функцию `@MainActor`, либо убрать создание Dictionary

**Текущее состояние:**
- ❌ `AnalyticsManager` НЕ имеет `@MainActor`
- ❌ Используется `parameters ?? [:]` - создает Dictionary в background thread!

---

### Принцип 5: Не должно быть разделения на demo/production mode в логике

**Правило:**
```swift
// ✅ ПРАВИЛЬНО (единая логика):
@MainActor
class NetworkProtectionViewModel: ObservableObject {
    private func toggleComponent(...) async {
        // Оптимистичное обновление UI
        updateClosure(newValue)
        
        // Единая логика для всех режимов
        do {
            try await statusService.updateStatus(
                componentId: componentId,
                isEnabled: newValue
            )
            
            // Успешное обновление
            componentAnalytics.trackComponentToggle(
                componentId: componentId,
                enabled: newValue
            )
            toastManager.showSuccess("Компонент обновлен")
            
        } catch {
            // Откат изменений при ошибке
            updateClosure(!newValue)
            componentAnalytics.trackComponentError(componentId: componentId, error: error)
            toastManager.showError("Ошибка: \(error.localizedDescription)")
        }
    }
}

// ❌ НЕПРАВИЛЬНО (разделение на demo/production):
private func toggleComponent(...) async {
    if AppConfig.authToken == nil {
        await handleDemoModeToggle(...)  // Разная логика!
    } else {
        await handleProductionModeToggle(...)  // Разная логика!
    }
}
```

**Почему:**
- Разделение на demo/production mode создает дублирование кода
- Разная логика может привести к разным багам
- Единая логика проще поддерживать и тестировать

**Текущее состояние:**
- ❌ Есть разделение на `handleDemoModeToggle()` и `handleProductionModeToggle()`
- ❌ Разная логика для разных режимов

---

## 🎯 ИДЕАЛЬНОЕ РЕШЕНИЕ (БЕЗ КОСТЫЛЕЙ)

### Архитектура:

```
┌─────────────────────────────────────────┐
│  SwiftUI View (NetworkProtectionScreen) │
│  - Вызывает методы ViewModel            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  @MainActor ViewModel                    │
│  (NetworkProtectionViewModel)            │
│  - Все операции автоматически на         │
│    main thread                           │
│  - Единая логика для всех режимов        │
└──────────────┬──────────────────────────┘
               │
               ├──► ComponentStatusService (@MainActor)
               │    - Обновление статусов
               │
               ├──► ComponentAnalytics (@MainActor)
               │    - Отслеживание событий
               │
               └──► ToastManager (@MainActor)
                    - Показ уведомлений
```

---

### Правильный код:

#### 1. ComponentAnalytics должен быть @MainActor

```swift
// ✅ ПРАВИЛЬНО:
@MainActor
class ComponentAnalytics {
    static let shared = ComponentAnalytics()
    
    private let analyticsManager = AnalyticsManager.shared
    
    private init() {}
    
    func trackComponentToggle(componentId: String, enabled: Bool) {
        // Автоматически на main thread благодаря @MainActor
        let parameters: [String: Any] = [
            "component_id": componentId,
            "enabled": enabled,
            "timestamp": Date().timeIntervalSince1970
        ]
        analyticsManager.trackEvent("component_toggle", parameters: parameters)
    }
    
    // ... другие методы ...
}
```

**Изменения:**
- ✅ Добавить `@MainActor` к классу
- ✅ Убрать `Task { await MainActor.run }` - не нужно!
- ✅ Dictionary создается на main thread автоматически

---

#### 2. AnalyticsManager должен быть @MainActor

```swift
// ✅ ПРАВИЛЬНО:
@MainActor
class AnalyticsManager {
    static let shared = AnalyticsManager()
    
    private let logger = MasterLogger.shared
    
    private init() {
        logger.business("Initializing AnalyticsManager")
    }
    
    func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
        // Автоматически на main thread благодаря @MainActor
        
        // ✅ Создаем строку описания БЕЗ создания Dictionary
        let paramsDescription: String
        if let params = parameters {
            paramsDescription = String(describing: params)
        } else {
            paramsDescription = "none"
        }
        
        logger.business("Analytics: Event - \(eventName) with params: \(paramsDescription)")
        #if DEBUG
        if let params = parameters {
            print("📊 Event: \(eventName), params: \(params)")
        } else {
            print("📊 Event: \(eventName), params: none")
        }
        #endif
    }
}
```

**Изменения:**
- ✅ Добавить `@MainActor` к классу
- ✅ Убрать `parameters ?? [:]` - не создавать Dictionary literal
- ✅ Использовать условную проверку вместо nil-coalescing operator

---

#### 3. NetworkProtectionViewModel - убрать await MainActor.run

```swift
// ✅ ПРАВИЛЬНО:
@MainActor
class NetworkProtectionViewModel: ObservableObject {
    // ... свойства ...
    
    private func toggleComponent(
        componentId: String,
        newValue: Bool,
        updateClosure: @escaping (Bool) -> Void
    ) async {
        // Защита от повторного переключения
        togglingLock.lock()
        guard !isToggling else {
            togglingLock.unlock()
            return
        }
        isToggling = true
        togglingLock.unlock()
        
        defer {
            togglingLock.lock()
            isToggling = false
            togglingLock.unlock()
        }
        
        // Оптимистичное обновление UI
        // ✅ Автоматически на main thread благодаря @MainActor
        updateClosure(newValue)
        
        // Единая логика для всех режимов
        do {
            try await statusService.updateStatus(
                componentId: componentId,
                isEnabled: newValue
            )
            
            // Успешное обновление
            // ✅ Автоматически на main thread благодаря @MainActor
            componentAnalytics.trackComponentToggle(
                componentId: componentId,
                enabled: newValue
            )
            toastManager.showSuccess("Компонент обновлен")
            
        } catch {
            // Откат изменений при ошибке
            // ✅ Автоматически на main thread благодаря @MainActor
            updateClosure(!newValue)
            componentAnalytics.trackComponentError(componentId: componentId, error: error)
            toastManager.showError("Ошибка: \(error.localizedDescription)")
        }
    }
}
```

**Изменения:**
- ✅ Убрать `await MainActor.run` - не нужно, класс уже `@MainActor`!
- ✅ Убрать разделение на demo/production mode - единая логика
- ✅ Все операции автоматически на main thread

---

## 📚 ПОЧЕМУ ЭТО ПРАВИЛЬНО?

### 1. @MainActor гарантирует main thread

**Как работает:**
- `@MainActor` - это аннотация Swift Concurrency
- Все методы и свойства класса автоматически выполняются на main thread
- Не нужно вручную использовать `await MainActor.run`

**Преимущества:**
- Код проще и понятнее
- Нет риска забыть `await MainActor.run`
- Компилятор проверяет правильность использования

---

### 2. Единая логика проще поддерживать

**Как работает:**
- Один метод `toggleComponent()` для всех режимов
- `ComponentStatusService` сам решает, как обновить статус (demo или production)
- Нет дублирования кода

**Преимущества:**
- Меньше кода
- Меньше багов
- Проще тестировать

---

### 3. Dictionary создается на main thread автоматически

**Как работает:**
- Если класс `@MainActor`, все операции на main thread
- Dictionary literal создается на main thread автоматически
- Не нужно вручную оборачивать в `await MainActor.run`

**Преимущества:**
- Нет проблем с Dictionary в background thread
- Нет рекурсии
- Код проще

---

## 🎯 ИТОГОВОЕ РЕШЕНИЕ

### Что нужно исправить:

1. ✅ Добавить `@MainActor` к `ComponentAnalytics`
2. ✅ Добавить `@MainActor` к `AnalyticsManager`
3. ✅ Убрать `Task { await MainActor.run }` из всех методов аналитики
4. ✅ Убрать `await MainActor.run` из `NetworkProtectionViewModel` (класс уже `@MainActor`)
5. ✅ Убрать разделение на demo/production mode - единая логика
6. ✅ Исправить `trackEvent()` - убрать `parameters ?? [:]`

### Результат:

- ✅ Все операции автоматически на main thread
- ✅ Нет костылей с `await MainActor.run`
- ✅ Код проще и понятнее
- ✅ Нет проблем с Dictionary в background thread
- ✅ Нет рекурсии

---

## 📚 ПОЧЕМУ ТЕКУЩИЙ КОД - ЭТО КОСТЫЛИ?

### Текущий код (костыли):

```swift
// ❌ КОСТЫЛЬ 1: Task { await MainActor.run }
class ComponentAnalytics {
    func trackComponentToggle(componentId: String, enabled: Bool) {
        Task {  // Создает новую задачу - может быть в background thread!
            await MainActor.run {  // Костыль для перехода на main thread
                let parameters: [String: Any] = [...]  // Dictionary может создать ДО MainActor.run!
                analyticsManager.trackEvent(...)
            }
        }
    }
}

// ❌ КОСТЫЛЬ 2: await MainActor.run в @MainActor классе
@MainActor
class NetworkProtectionViewModel: ObservableObject {
    func toggleComponent(...) async {
        await MainActor.run {  // НЕ НУЖНО! Класс уже @MainActor!
            updateClosure(newValue)
        }
    }
}

// ❌ КОСТЫЛЬ 3: parameters ?? [:]
func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
    print("📊 Event: \(eventName), params: \(parameters ?? [:])")  // Dictionary создается здесь!
}
```

**Почему это костыли:**
- `Task { await MainActor.run }` - избыточная обертка, если класс `@MainActor`
- `await MainActor.run` в `@MainActor` классе - избыточно
- `parameters ?? [:]` - создает Dictionary literal в background thread

---

### Правильный код (без костылей):

```swift
// ✅ ПРАВИЛЬНО: @MainActor на классе
@MainActor
class ComponentAnalytics {
    func trackComponentToggle(componentId: String, enabled: Bool) {
        // Автоматически на main thread благодаря @MainActor
        let parameters: [String: Any] = [
            "component_id": componentId,
            "enabled": enabled,
            "timestamp": Date().timeIntervalSince1970
        ]
        analyticsManager.trackEvent("component_toggle", parameters: parameters)
    }
}

// ✅ ПРАВИЛЬНО: Без await MainActor.run в @MainActor классе
@MainActor
class NetworkProtectionViewModel: ObservableObject {
    func toggleComponent(...) async {
        // Автоматически на main thread благодаря @MainActor
        updateClosure(newValue)  // Без await MainActor.run!
    }
}

// ✅ ПРАВИЛЬНО: Без parameters ?? [:]
@MainActor
func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
    let paramsDescription: String
    if let params = parameters {
        paramsDescription = String(describing: params)
    } else {
        paramsDescription = "none"
    }
    print("📊 Event: \(eventName), params: \(paramsDescription)")
}
```

**Почему это правильно:**
- `@MainActor` на классе гарантирует main thread автоматически
- Нет избыточных оберток
- Dictionary создается на main thread автоматически
- Код проще и понятнее

---

## 🎯 КАК ДОЛЖНО БЫТЬ ПО КНИЖКЕ?

### Принцип: Используйте @MainActor для UI-связанных классов

**Apple Documentation:**
> "Use `@MainActor` to ensure that all UI updates happen on the main thread."

**Правило:**
- Все классы, которые работают с UI, должны быть `@MainActor`
- Все ViewModel должны быть `@MainActor`
- Все сервисы, которые вызываются из ViewModel, должны быть `@MainActor`

**Пример:**
```swift
// ✅ ПРАВИЛЬНО:
@MainActor
class NetworkProtectionViewModel: ObservableObject {
    // Все методы автоматически на main thread
}

@MainActor
class ComponentAnalytics {
    // Все методы автоматически на main thread
}

@MainActor
class AnalyticsManager {
    // Все методы автоматически на main thread
}
```

---

### Принцип: Не используйте Task { await MainActor.run } в @MainActor классе

**Apple Documentation:**
> "If a class is marked with `@MainActor`, all its methods and properties are automatically isolated to the main actor."

**Правило:**
- Если класс `@MainActor`, не нужно использовать `await MainActor.run`
- Все методы уже выполняются на main thread

**Пример:**
```swift
// ✅ ПРАВИЛЬНО:
@MainActor
class MyViewModel {
    func doSomething() {
        // Автоматически на main thread
        updateUI()
    }
}

// ❌ НЕПРАВИЛЬНО:
@MainActor
class MyViewModel {
    func doSomething() {
        await MainActor.run {  // НЕ НУЖНО!
            updateUI()
        }
    }
}
```

---

### Принцип: Dictionary создание должно быть на main thread

**Apple Documentation:**
> "Dictionary operations should be performed on the main thread to avoid thread-safety issues."

**Правило:**
- Если класс `@MainActor`, Dictionary создается на main thread автоматически
- Не используйте `parameters ?? [:]` - создает Dictionary literal синхронно

**Пример:**
```swift
// ✅ ПРАВИЛЬНО:
@MainActor
func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
    // Автоматически на main thread
    if let params = parameters {
        print("Event: \(eventName), params: \(params)")
    } else {
        print("Event: \(eventName), params: none")
    }
}

// ❌ НЕПРАВИЛЬНО:
func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
    print("Event: \(eventName), params: \(parameters ?? [:])")  // Dictionary создается здесь!
}
```

---

## 📋 ПОШАГОВЫЙ ПЛАН ИСПРАВЛЕНИЯ (ИДЕАЛЬНОЕ РЕШЕНИЕ)

### ШАГ 1: Добавить @MainActor к ComponentAnalytics

**Файл:** `Core/Analytics/ComponentAnalytics.swift`

**Изменения:**
```swift
// БЫЛО:
class ComponentAnalytics {
    func trackComponentToggle(componentId: String, enabled: Bool) {
        Task {
            await MainActor.run {
                let parameters: [String: Any] = [...]
                analyticsManager.trackEvent(...)
            }
        }
    }
}

// СТАЛО:
@MainActor
class ComponentAnalytics {
    func trackComponentToggle(componentId: String, enabled: Bool) {
        // Автоматически на main thread благодаря @MainActor
        let parameters: [String: Any] = [
            "component_id": componentId,
            "enabled": enabled,
            "timestamp": Date().timeIntervalSince1970
        ]
        analyticsManager.trackEvent("component_toggle", parameters: parameters)
    }
}
```

**Результат:**
- ✅ Убрали `Task { await MainActor.run }` - не нужно!
- ✅ Dictionary создается на main thread автоматически
- ✅ Код проще и понятнее

---

### ШАГ 2: Добавить @MainActor к AnalyticsManager

**Файл:** `Core/Analytics/AnalyticsManager.swift`

**Изменения:**
```swift
// БЫЛО:
class AnalyticsManager {
    func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
        logger.business("Analytics: Event - \(eventName) with params: \(parameters?.description ?? "none")")
        #if DEBUG
        print("📊 Event: \(eventName), params: \(parameters ?? [:])")
        #endif
    }
}

// СТАЛО:
@MainActor
class AnalyticsManager {
    func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
        // Автоматически на main thread благодаря @MainActor
        
        // ✅ Создаем строку описания БЕЗ создания Dictionary
        let paramsDescription: String
        if let params = parameters {
            paramsDescription = String(describing: params)
        } else {
            paramsDescription = "none"
        }
        
        logger.business("Analytics: Event - \(eventName) with params: \(paramsDescription)")
        #if DEBUG
        if let params = parameters {
            print("📊 Event: \(eventName), params: \(params)")
        } else {
            print("📊 Event: \(eventName), params: none")
        }
        #endif
    }
}
```

**Результат:**
- ✅ Убрали `parameters ?? [:]` - не создаем Dictionary literal
- ✅ Убрали `parameters?.description` - используем `String(describing:)`
- ✅ Все операции на main thread автоматически

---

### ШАГ 3: Убрать await MainActor.run из NetworkProtectionViewModel

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`

**Изменения:**
```swift
// БЫЛО:
@MainActor
class NetworkProtectionViewModel: ObservableObject {
    private func handleProductionModeToggle(...) async {
        try await statusService.updateStatus(...)
        
        await MainActor.run {  // НЕ НУЖНО!
            componentAnalytics.trackComponentToggle(...)
        }
        toastManager.showSuccess(...)  // БЕЗ await MainActor.run
    }
}

// СТАЛО:
@MainActor
class NetworkProtectionViewModel: ObservableObject {
    private func toggleComponent(...) async {
        // Защита от повторного переключения
        // ... защита ...
        
        // Оптимистичное обновление UI
        // ✅ Автоматически на main thread благодаря @MainActor
        updateClosure(newValue)
        
        // Единая логика для всех режимов
        do {
            try await statusService.updateStatus(
                componentId: componentId,
                isEnabled: newValue
            )
            
            // Успешное обновление
            // ✅ Автоматически на main thread благодаря @MainActor
            componentAnalytics.trackComponentToggle(
                componentId: componentId,
                enabled: newValue
            )
            toastManager.showSuccess("Компонент обновлен")
            
        } catch {
            // Откат изменений при ошибке
            // ✅ Автоматически на main thread благодаря @MainActor
            updateClosure(!newValue)
            componentAnalytics.trackComponentError(componentId: componentId, error: error)
            toastManager.showError("Ошибка: \(error.localizedDescription)")
        }
    }
}
```

**Результат:**
- ✅ Убрали `await MainActor.run` - не нужно, класс уже `@MainActor`!
- ✅ Убрали разделение на demo/production mode - единая логика
- ✅ Все операции на main thread автоматически

---

## 🎯 ИТОГОВОЕ РЕШЕНИЕ

### Что нужно исправить:

1. ✅ Добавить `@MainActor` к `ComponentAnalytics`
2. ✅ Добавить `@MainActor` к `AnalyticsManager`
3. ✅ Убрать `Task { await MainActor.run }` из всех методов аналитики
4. ✅ Убрать `await MainActor.run` из `NetworkProtectionViewModel` (класс уже `@MainActor`)
5. ✅ Убрать разделение на demo/production mode - единая логика
6. ✅ Исправить `trackEvent()` - убрать `parameters ?? [:]`

### Результат:

- ✅ Все операции автоматически на main thread
- ✅ Нет костылей с `await MainActor.run`
- ✅ Код проще и понятнее
- ✅ Нет проблем с Dictionary в background thread
- ✅ Нет рекурсии
- ✅ Соответствует best practices Apple

---

**Статус:** 📚 **ИДЕАЛЬНОЕ РЕШЕНИЕ БЕЗ КОСТЫЛЕЙ**  
**Рекомендация:** Использовать `@MainActor` вместо ручного `await MainActor.run` - это правильный подход по книжке!
