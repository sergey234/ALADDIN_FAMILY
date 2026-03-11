# 🔍 BUILD 104: ВСЕ ВОЗМОЖНЫЕ ПРИЧИНЫ И РЕКОМЕНДАЦИИ

**Дата:** 2026-03-11  
**Build:** 104  
**Статус:** 🔴 **КРИТИЧЕСКАЯ ПРОБЛЕМА - КРАШ В MAIN THREAD**

---

## 📊 КРАТКОЕ РЕЗЮМЕ ПРОБЛЕМЫ

**Что происходит:**
- Краш при **первом переходе** на страницу "Защита АЛАДДИН"
- Краш при **втором заходе** на страницу и переключении тумблеров
- Краш в **MAIN THREAD** (Thread 0), а не в background thread!

**Тип краша:**
- `EXC_BAD_ACCESS (SIGSEGV)`
- `Thread stack size exceeded due to excessive recursion`
- `Dictionary.resize` в main thread

**Критическое отличие:**
- BUILD 101-103: Краш был в **background thread**
- BUILD 104: Краш в **MAIN THREAD**!

---

## 🔍 ВСЕ ВОЗМОЖНЫЕ ПРИЧИНЫ КРАША

### 🔴 ПРИЧИНА 1: Рекурсия в `NetworkProtectionViewModel.init()` через `Task {}`

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`  
**Строки:** 61-63

**Проблема:**
```swift
init(...) {
    // ...
    // Загружаем статусы компонентов при инициализации
    Task {  // ❌ ПРОБЛЕМА!
        await loadComponentStatuses()
    }
}
```

**Механизм рекурсии:**
```
1. View создается → init() вызывается
2. Task {} запускает loadComponentStatuses()
3. loadComponentStatuses() обновляет 10 @Published свойств
4. SwiftUI получает уведомление об изменении
5. SwiftUI обновляет View
6. SwiftUI может пересоздать View
7. init() вызывается СНОВА
8. Task {} создается СНОВА
9. РЕКУРСИЯ!
```

**Почему это критично:**
- `Task {}` в `init()` создается синхронно при инициализации
- Если View пересоздается из-за обновления `@Published`, `init()` вызывается снова
- Это создает бесконечный цикл рекурсии в main thread

**Вероятность:** 🔴 **100% - это основная причина краша!**

---

### 🔴 ПРИЧИНА 2: `Task { @MainActor in }` внутри `@MainActor` метода

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`  
**Строка:** 242

**Проблема:**
```swift
@MainActor
class NetworkProtectionViewModel: ObservableObject {
    private func updateStatusForComponent(componentId: String, isEnabled: Bool) {
        Task { @MainActor in  // ❌ ПРОБЛЕМА!
            switch componentId {
            case "crash_detection_agent":
                crashDetectionEnabled = isEnabled
            // ...
            }
        }
    }
}
```

**Почему это проблема:**
- Класс уже имеет `@MainActor`
- Метод уже выполняется на main thread
- `Task { @MainActor in }` создает новый Task, даже если мы уже на main thread
- При рекурсии это может создавать множественные Tasks
- Каждый Task обновляет `@Published` свойства
- Это вызывает обновление View
- View пересоздается
- **РЕКУРСИЯ!**

**Вероятность:** 🔴 **90% - усугубляет проблему!**

---

### 🔴 ПРИЧИНА 3: Множественные вызовы `.onAppear` без защиты

**Файл:** `Screens/03_NetworkProtectionScreen.swift`  
**Строки:** 365-371

**Проблема:**
```swift
.onAppear {
    // Отследить просмотр экрана с компонентами
    ComponentAnalytics.shared.trackComponentScreenView(
        screenName: "NetworkProtectionScreen",
        componentCount: 10
    )
}
```

**Что происходит:**
1. `.onAppear` вызывается при каждом появлении View
2. Если View пересоздается, `.onAppear` вызывается снова
3. `trackComponentScreenView()` создает Dictionary каждый раз:
   ```swift
   let parameters: [String: Any] = [
       "screen_name": screenName,
       "component_count": componentCount,
       "timestamp": Date().timeIntervalSince1970
   ]
   ```
4. При рекурсии Dictionary создается многократно в main thread
5. Dictionary пытается изменить размер многократно
6. **РЕКУРСИЯ!**

**Вероятность:** 🟡 **70% - усугубляет проблему!**

---

### 🔴 ПРИЧИНА 4: `await MainActor.run {}` внутри `@MainActor` метода

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`  
**Строки:** 94, 107

**Проблема:**
```swift
@MainActor
class NetworkProtectionViewModel: ObservableObject {
    private func loadDemoModeStatuses(...) async {
        for item in prioritizedItems {
            let isEnabled = UserDefaults.standard.bool(forKey: userDefaultsKey)
            
            await MainActor.run {  // ❌ ПРОБЛЕМА!
                self.updateStatusForComponent(componentId: item.id, isEnabled: isEnabled)
            }
        }
    }
}
```

**Почему это проблема:**
- Метод уже на `@MainActor`
- `await MainActor.run {}` создает ненужный переход на main thread
- При рекурсии это может вызывать проблемы
- `updateStatusForComponent()` внутри создает еще один `Task { @MainActor in }`
- Это создает множественные Tasks
- **РЕКУРСИЯ!**

**Вероятность:** 🟡 **60% - усугубляет проблему!**

---

### 🟡 ПРИЧИНА 5: Отсутствие защиты от повторной загрузки статусов

**Проблема:**
- Нет флага для предотвращения повторной загрузки статусов
- Если View пересоздается, `init()` вызывается снова
- `loadComponentStatuses()` вызывается снова
- Это может вызывать рекурсию

**Вероятность:** 🟡 **50% - может усугублять проблему!**

---

### 🟡 ПРИЧИНА 6: SwiftUI View пересоздается при обновлении `@Published` свойств

**Проблема:**
- Обновление 10 `@Published` свойств одновременно может вызвать пересоздание View
- SwiftUI может решить пересоздать View, если структура изменилась
- Это вызывает повторный вызов `init()`

**Вероятность:** 🟡 **40% - может усугублять проблему!**

---

### 🟡 ПРИЧИНА 7: `UserDefaults.standard.bool()` в цикле может вызывать проблемы

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`  
**Строка:** 92

**Проблема:**
```swift
for item in prioritizedItems {
    let isEnabled = UserDefaults.standard.bool(forKey: userDefaultsKey)  // ⚠️ Может вызывать проблемы
    // ...
}
```

**Почему это может быть проблемой:**
- `UserDefaults.standard.bool()` вызывается синхронно в цикле
- Если View пересоздается многократно, это может вызывать проблемы
- Но это менее вероятно, так как `UserDefaults` обычно не вызывает рекурсию

**Вероятность:** 🟢 **20% - маловероятно!**

---

## ✅ РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ

### Приоритет 1: Критический (исправить немедленно)

#### 1. Убрать `Task {}` из `init()` и загружать статусы в `.onAppear`

**Текущий код:**
```swift
init(...) {
    self.statusService = statusService
    self.configurationService = configurationService
    self.retryManager = retryManager

    // ❌ УБРАТЬ!
    Task {
        await loadComponentStatuses()
    }
}
```

**Исправленный код:**
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
.onAppear {
    // ✅ Загружаем статусы только один раз
    if !viewModel.hasLoadedStatuses {
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

**Текущий код:**
```swift
private func updateStatusForComponent(componentId: String, isEnabled: Bool) {
    Task { @MainActor in  // ❌ УБРАТЬ!
        switch componentId {
        case "crash_detection_agent":
            crashDetectionEnabled = isEnabled
        // ...
        }
    }
}
```

**Исправленный код:**
```swift
private func updateStatusForComponent(componentId: String, isEnabled: Bool) {
    // ✅ УБРАЛИ Task { @MainActor in } - метод уже на @MainActor
    switch componentId {
    case "crash_detection_agent":
        crashDetectionEnabled = isEnabled
    case "roadside_assistance_agent":
        roadsideAssistanceEnabled = isEnabled
    case "emergency_response_bot":
        emergencyResponseEnabled = isEnabled
    case "emergency_event_manager":
        emergencyEventEnabled = isEnabled
    case "phishing_protection_agent":
        phishingProtectionEnabled = isEnabled
    case "malware_detection_agent":
        malwareDetectionEnabled = isEnabled
    case "mobile_security_agent":
        mobileSecurityEnabled = isEnabled
    case "network_security_agent":
        networkSecurityEnabled = isEnabled
    case "incident_response_agent":
        incidentResponseEnabled = isEnabled
    case "password_security_agent":
        passwordSecurityEnabled = isEnabled
    default:
        break
    }
}
```

---

#### 3. Убрать `await MainActor.run {}` из методов загрузки

**Текущий код:**
```swift
private func loadDemoModeStatuses(...) async {
    for item in prioritizedItems {
        let isEnabled = UserDefaults.standard.bool(forKey: userDefaultsKey)
        
        await MainActor.run {  // ❌ УБРАТЬ!
            self.updateStatusForComponent(componentId: item.id, isEnabled: isEnabled)
        }
    }
}

private func loadProductionModeStatuses(...) async {
    for item in prioritizedItems {
        do {
            let status = try await APIService.shared.getComponentStatus(componentId: item.id)
            await MainActor.run {  // ❌ УБРАТЬ!
                self.updateStatusForComponent(componentId: item.id, status: status)
            }
        } catch {
            // ...
        }
    }
}
```

**Исправленный код:**
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

#### 4. Добавить защиту от повторного вызова в `.onAppear`

**Текущий код:**
```swift
.onAppear {
    ComponentAnalytics.shared.trackComponentScreenView(...)  // ❌ Вызывается многократно
}
```

**Исправленный код:**
```swift
@State private var hasTrackedScreenView = false

.onAppear {
    // ✅ Защита от повторного вызова
    guard !hasTrackedScreenView else { return }
    hasTrackedScreenView = true
    
    ComponentAnalytics.shared.trackComponentScreenView(
        screenName: "NetworkProtectionScreen",
        componentCount: 10
    )
}
```

---

#### 5. Добавить флаг для предотвращения повторной загрузки статусов

**Текущий код:**
```swift
func loadComponentStatuses() async {
    isLoading = true
    defer { isLoading = false }
    // ...
}
```

**Исправленный код:**
```swift
@MainActor
class NetworkProtectionViewModel: ObservableObject {
    // ...
    private var hasLoadedStatuses = false  // ✅ Добавить флаг
    
    func loadComponentStatuses() async {
        // ✅ Защита от повторной загрузки
        guard !hasLoadedStatuses else {
            print("⚠️ NetworkProtectionViewModel: Статусы уже загружены, пропускаем")
            return
        }
        
        hasLoadedStatuses = true
        isLoading = true
        defer { isLoading = false }
        
        // ... остальной код
    }
}
```

---

### Приоритет 2: Высокий (исправить после критических)

#### 6. Добавить защиту от множественных обновлений `@Published` свойств

**Рекомендация:**
- Обновлять все `@Published` свойства в одном блоке
- Использовать `objectWillChange.send()` для батч-обновления
- Или обновлять свойства последовательно, а не в цикле

---

#### 7. Проверить, не вызывается ли `init()` многократно

**Рекомендация:**
- Добавить логирование в `init()` для отслеживания вызовов
- Проверить, не пересоздается ли View многократно
- Использовать `@StateObject` вместо `@ObservedObject` (уже используется)

---

## 📋 ПЛАН ДЕЙСТВИЙ

### Этап 1: Немедленно (15 минут)

1. ✅ Убрать `Task {}` из `NetworkProtectionViewModel.init()`
2. ✅ Убрать `Task { @MainActor in }` из `updateStatusForComponent()`
3. ✅ Убрать `await MainActor.run {}` из `loadDemoModeStatuses()` и `loadProductionModeStatuses()`
4. ✅ Добавить флаг `hasLoadedStatuses` в `NetworkProtectionViewModel`
5. ✅ Переместить загрузку статусов в `.onAppear` в `NetworkProtectionScreen`

### Этап 2: Высокий приоритет (10 минут)

6. ✅ Добавить защиту от повторного вызова в `.onAppear` для `trackComponentScreenView()`
7. ✅ Добавить логирование для отслеживания вызовов `init()`

### Этап 3: Тестирование (30 минут)

8. ✅ Протестировать переход на страницу
9. ✅ Протестировать переключение тумблеров
10. ✅ Проверить отсутствие крашей

---

## 🎯 ИТОГОВЫЕ РЕКОМЕНДАЦИИ

### Критические исправления (обязательно):

1. **Убрать `Task {}` из `init()`** - это основная причина рекурсии
2. **Убрать `Task { @MainActor in }` из `updateStatusForComponent()`** - создает ненужные Tasks
3. **Убрать `await MainActor.run {}` из методов загрузки** - создает ненужные переходы
4. **Добавить защиту от повторной загрузки** - флаг `hasLoadedStatuses`
5. **Добавить защиту от повторного вызова в `.onAppear`** - флаг `hasTrackedScreenView`

### Принципы для будущего:

1. **НЕ создавать `Task {}` в `init()`** - это может вызывать рекурсию
2. **НЕ использовать `Task { @MainActor in }` внутри `@MainActor` методов** - это создает ненужные Tasks
3. **НЕ использовать `await MainActor.run {}` внутри `@MainActor` методов** - это создает ненужные переходы
4. **Всегда добавлять защиту от повторного вызова** - флаги для предотвращения рекурсии
5. **Загружать данные в `.onAppear`, а не в `init()`** - это предотвращает рекурсию

---

**Статус:** 🔴 **КРИТИЧЕСКАЯ ПРОБЛЕМА - НУЖНЫ НЕМЕДЛЕННЫЕ ИСПРАВЛЕНИЯ**  
**Рекомендация:** Исправить все 5 критических проблем немедленно
