# 🚨 BUILD 104: ФИНАЛЬНЫЙ АНАЛИЗ И ПЛАН ДЕЙСТВИЙ

**Дата:** 2026-03-11  
**Build:** 104  
**Статус:** 🔴 **КРИТИЧЕСКАЯ ПРОБЛЕМА - ДВА РАЗНЫХ КРАША!**

---

## 📊 СВОДКА ПРОБЛЕМ

### У нас ДВЕ разные проблемы:

1. **Краш при переходе на страницу** (Thread 0 - main thread)
   - Причина: `Task {}` в `NetworkProtectionViewModel.init()`
   - Решение: Убрать `Task {}` из `init()`, загружать в `.onAppear`

2. **Краш при переключении тумблеров** (Thread 2 - background thread)
   - Причина: Dictionary создается в background thread
   - Решение: Убедиться, что Dictionary создается на main thread

---

## 🔍 ДЕТАЛЬНЫЙ АНАЛИЗ КРАША ПРИ ПЕРЕКЛЮЧЕНИИ ТУМБЛЕРОВ

### Stack Trace показывает:

```
Thread 2 (Crashed - BACKGROUND THREAD):
6   ALADDIN                        0x1007dff8c  // Dictionary создается здесь
7   ALADDIN                        0x1007dc060  // Dictionary operation
8   ALADDIN                        0x1007db9c4  // Рекурсия начинается здесь
9   ALADDIN                        0x1008e5864  // Рекурсивный вызов
10  ALADDIN                        0x1008e5b54  // Рекурсивный вызов
11-16 ALADDIN                      0x1008e5b60  // РЕКУРСИЯ! (повторяется 6 раз)
17  ALADDIN                        0x100716ebc  // Возможно: toggleComponent
18  ALADDIN                        0x1007e4aed  // Возможно: Task или async функция
```

**Вывод:** Рекурсия происходит в `toggleComponent` или связанных методах.

---

## 🔍 НАЙДЕННЫЕ ПРИЧИНЫ КРАША ПРИ ПЕРЕКЛЮЧЕНИИ ТУМБЛЕРОВ

### ❌ ПРИЧИНА 1: `componentAnalytics.trackComponentToggle()` вызывается из `async` функции

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`  
**Строки:** 322-325

**Проблема:**
```swift
@MainActor
class NetworkProtectionViewModel: ObservableObject {
    private func toggleComponent(...) async {
        // ...
        // ✅ BUILD 102: Автоматически на main thread благодаря @MainActor
        componentAnalytics.trackComponentToggle(
            componentId: componentId,
            enabled: newValue
        )
    }
}
```

**Что происходит:**
1. `toggleComponent` - это `async` функция в `@MainActor` классе
2. Хотя класс имеет `@MainActor`, `async` функция может выполняться в background thread
3. `componentAnalytics.trackComponentToggle()` вызывается из `async` функции
4. Внутри `trackComponentToggle()` создается Dictionary:
   ```swift
   let parameters: [String: Any] = [
       "component_id": componentId,
       "enabled": enabled,
       "timestamp": Date().timeIntervalSince1970
   ]
   ```
5. Если `async` функция выполняется в background thread, Dictionary создается в background thread
6. **РЕКУРСИЯ!**

**Почему это проблема:**
- `@MainActor` на классе гарантирует, что методы выполняются на main thread
- НО: `async` функции могут выполняться в background thread, если вызываются из `Task {}`
- Dictionary создается **ДО** перехода на main thread

---

### ❌ ПРИЧИНА 2: `Task { @MainActor in }` в UI не гарантирует создание Dictionary на main thread

**Файл:** `Screens/03_NetworkProtectionScreen.swift`  
**Строки:** 210, 257, 267, и т.д.

**Проблема:**
```swift
onToggle: { newValue in Task { @MainActor in await viewModel.toggleCrashDetection(newValue) } }
```

**Что происходит:**
1. `onToggle` вызывается из SwiftUI (может быть в background thread)
2. `Task { @MainActor in }` создается
3. НО: `viewModel.toggleCrashDetection()` вызывается **ДО** входа в блок `@MainActor`
4. Внутри `toggleCrashDetection()` → `toggleComponent()` → `trackComponentToggle()`
5. Dictionary создается в background thread
6. **РЕКУРСИЯ!**

**Почему это проблема:**
- `Task { @MainActor in }` гарантирует выполнение блока на main thread
- НО: вызов метода может происходить **ДО** входа в блок
- Dictionary создается внутри метода, который может выполняться в background thread

---

### ❌ ПРИЧИНА 3: `await MainActor.run {}` внутри `@MainActor` метода

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`  
**Строка:** 314

**Проблема:**
```swift
@MainActor
class NetworkProtectionViewModel: ObservableObject {
    private func toggleComponent(...) async {
        // ...
        await MainActor.run {  // ❌ ПРОБЛЕМА!
            let userDefaultsKey = "demo_component_\(componentId)_enabled"
            UserDefaults.standard.set(newValue, forKey: userDefaultsKey)
        }
    }
}
```

**Почему это проблема:**
- Метод уже на `@MainActor`
- `await MainActor.run {}` создает ненужный переход
- Может вызывать проблемы при рекурсии

---

## ✅ РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ

### Приоритет 1: Критический (исправить немедленно)

#### 1. Убрать `Task {}` из `init()` и загружать статусы в `.onAppear`

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`  
**Строки:** 61-63

**Исправление:**
```swift
init(...) {
    self.statusService = statusService
    self.configurationService = configurationService
    self.retryManager = retryManager
    // ✅ УБРАЛИ Task {} из init()
}
```

**В NetworkProtectionScreen:**
```swift
@State private var hasLoadedStatuses = false

.onAppear {
    // ✅ Загружаем статусы только один раз
    if !hasLoadedStatuses {
        hasLoadedStatuses = true
        Task {
            await viewModel.loadComponentStatuses()
        }
    }
    
    // Отследить просмотр экрана с компонентами (с защитой)
    if !hasTrackedScreenView {
        hasTrackedScreenView = true
        ComponentAnalytics.shared.trackComponentScreenView(
            screenName: "NetworkProtectionScreen",
            componentCount: 10
        )
    }
}
```

---

#### 2. Убрать `Task { @MainActor in }` из `updateStatusForComponent()`

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`  
**Строка:** 242

**Исправление:**
```swift
private func updateStatusForComponent(componentId: String, isEnabled: Bool) {
    // ✅ УБРАЛИ Task { @MainActor in } - метод уже на @MainActor
    switch componentId {
    case "crash_detection_agent":
        crashDetectionEnabled = isEnabled
    // ... остальные компоненты
    }
}
```

---

#### 3. Убрать `await MainActor.run {}` из методов загрузки

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`  
**Строки:** 94, 107

**Исправление:**
```swift
private func loadDemoModeStatuses(...) async {
    // ✅ УБРАЛИ await MainActor.run {} - метод уже на @MainActor
    for item in prioritizedItems {
        let isEnabled = UserDefaults.standard.bool(forKey: userDefaultsKey)
        self.updateStatusForComponent(componentId: item.id, isEnabled: isEnabled)
    }
}

private func loadProductionModeStatuses(...) async {
    // ✅ УБРАЛИ await MainActor.run {} - метод уже на @MainActor
    for item in prioritizedItems {
        do {
            let status = try await APIService.shared.getComponentStatus(componentId: item.id)
            self.updateStatusForComponent(componentId: item.id, status: status)
        } catch {
            print("⚠️ Ошибка загрузки статуса для \(item.id): \(error.localizedDescription)")
        }
    }
}
```

---

#### 4. Исправить `toggleComponent` - обернуть вызовы аналитики в `await MainActor.run {}`

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`  
**Строки:** 322-325, 340

**Проблема:**
- `componentAnalytics.trackComponentToggle()` вызывается из `async` функции
- Dictionary может создаваться в background thread

**Исправление:**
```swift
private func toggleComponent(...) async {
    // ... защита от повторного переключения ...
    
    // ✅ BUILD 102: Оптимистичное обновление UI
    updateClosure(newValue)

    do {
        // ... обновление статуса ...
        
        // ✅ BUILD 104: Явно оборачиваем вызовы аналитики в await MainActor.run {}
        await MainActor.run {
            componentAnalytics.trackComponentToggle(
                componentId: componentId,
                enabled: newValue
            )
            
            if AppConfig.authToken == nil {
                toastManager.showSuccess("Компонент обновлен (демо режим)")
            } else {
                toastManager.showSuccess("Компонент обновлен")
            }
        }
    } catch {
        // Откат изменений при ошибке
        updateClosure(!newValue)
        
        // ✅ BUILD 104: Явно оборачиваем вызовы аналитики в await MainActor.run {}
        await MainActor.run {
            componentAnalytics.trackComponentError(componentId: componentId, error: error)
            toastManager.showError("Ошибка: \(error.localizedDescription)")
        }
    }
}
```

---

#### 5. Убрать `await MainActor.run {}` из `toggleComponent` для UserDefaults

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`  
**Строка:** 314

**Исправление:**
```swift
// ❌ Было:
await MainActor.run {
    let userDefaultsKey = "demo_component_\(componentId)_enabled"
    UserDefaults.standard.set(newValue, forKey: userDefaultsKey)
}

// ✅ Стало:
// ✅ BUILD 104: УБРАЛИ await MainActor.run {} - метод уже на @MainActor
let userDefaultsKey = "demo_component_\(componentId)_enabled"
UserDefaults.standard.set(newValue, forKey: userDefaultsKey)
```

---

## 📋 ПОДРОБНЫЙ ПЛАН ДЕЙСТВИЙ

### ЭТАП 1: Исправить краш при переходе на страницу (15 минут)

**Задача 1.1:** Убрать `Task {}` из `NetworkProtectionViewModel.init()`
- Файл: `ViewModels/NetworkProtectionViewModel.swift`
- Строки: 61-63
- Действие: Удалить `Task { await loadComponentStatuses() }`

**Задача 1.2:** Убрать `Task { @MainActor in }` из `updateStatusForComponent()`
- Файл: `ViewModels/NetworkProtectionViewModel.swift`
- Строка: 242
- Действие: Удалить `Task { @MainActor in }`, оставить только `switch`

**Задача 1.3:** Убрать `await MainActor.run {}` из `loadDemoModeStatuses()`
- Файл: `ViewModels/NetworkProtectionViewModel.swift`
- Строка: 94
- Действие: Удалить `await MainActor.run {}`, оставить прямой вызов

**Задача 1.4:** Убрать `await MainActor.run {}` из `loadProductionModeStatuses()`
- Файл: `ViewModels/NetworkProtectionViewModel.swift`
- Строка: 107
- Действие: Удалить `await MainActor.run {}`, оставить прямой вызов

**Задача 1.5:** Добавить флаг `hasLoadedStatuses` в `NetworkProtectionViewModel`
- Файл: `ViewModels/NetworkProtectionViewModel.swift`
- Действие: Добавить `private var hasLoadedStatuses = false` и проверку в `loadComponentStatuses()`

**Задача 1.6:** Переместить загрузку статусов в `.onAppear` в `NetworkProtectionScreen`
- Файл: `Screens/03_NetworkProtectionScreen.swift`
- Строки: 365-371
- Действие: Добавить загрузку статусов в `.onAppear` с защитой от повторного вызова

**Задача 1.7:** Добавить защиту от повторного вызова в `.onAppear` для `trackComponentScreenView()`
- Файл: `Screens/03_NetworkProtectionScreen.swift`
- Строки: 365-371
- Действие: Добавить флаг `hasTrackedScreenView` и проверку

---

### ЭТАП 2: Исправить краш при переключении тумблеров (20 минут)

**Задача 2.1:** Обернуть вызовы аналитики в `await MainActor.run {}` в `toggleComponent`
- Файл: `ViewModels/NetworkProtectionViewModel.swift`
- Строки: 322-325, 340
- Действие: Обернуть `componentAnalytics.trackComponentToggle()` и `trackComponentError()` в `await MainActor.run {}`

**Задача 2.2:** Обернуть вызовы `toastManager` в `await MainActor.run {}` в `toggleComponent`
- Файл: `ViewModels/NetworkProtectionViewModel.swift`
- Строки: 328-331, 341
- Действие: Обернуть `toastManager.showSuccess()` и `showError()` в `await MainActor.run {}`

**Задача 2.3:** Убрать `await MainActor.run {}` из `toggleComponent` для UserDefaults
- Файл: `ViewModels/NetworkProtectionViewModel.swift`
- Строка: 314
- Действие: Удалить `await MainActor.run {}`, оставить прямой вызов

---

### ЭТАП 3: Тестирование (30 минут)

**Задача 3.1:** Протестировать переход на страницу
- Проверить отсутствие краша при первом переходе
- Проверить отсутствие краша при повторном переходе

**Задача 3.2:** Протестировать переключение тумблеров
- Проверить отсутствие краша при переключении каждого тумблера
- Проверить работу в demo режиме
- Проверить работу в production режиме

**Задача 3.3:** Проверить отсутствие крашей
- Запустить приложение на реальном устройстве
- Проверить все сценарии использования

---

## 🎯 ИТОГОВЫЙ ВЫВОД

**У нас ДВЕ разные проблемы:**

1. **Краш при переходе на страницу** (main thread)
   - Причина: `Task {}` в `init()` вызывает пересоздание View
   - Решение: Убрать `Task {}` из `init()`, загружать в `.onAppear`

2. **Краш при переключении тумблеров** (background thread)
   - Причина: Dictionary создается в background thread в `toggleComponent`
   - Решение: Обернуть вызовы аналитики в `await MainActor.run {}`

**Всего исправлений:** 10 задач

---

**Статус:** 🔴 **КРИТИЧЕСКАЯ ПРОБЛЕМА - НУЖНЫ НЕМЕДЛЕННЫЕ ИСПРАВЛЕНИЯ**  
**Рекомендация:** Исправить все 10 задач немедленно
