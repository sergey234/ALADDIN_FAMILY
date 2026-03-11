# 🚨 BUILD 104: КРИТИЧЕСКИЙ АНАЛИЗ КРАША ПРИ ПЕРЕХОДЕ НА СТРАНИЦУ

**Дата краша:** 2026-03-11 12:12:08  
**Build:** 104  
**Статус:** 🔴 **КРИТИЧЕСКАЯ ПРОБЛЕМА - КРАШ В MAIN THREAD!**

---

## 📊 АНАЛИЗ КРАША

### Основная информация:

**Exception Type:** `EXC_BAD_ACCESS (SIGSEGV)`  
**Exception Message:** `Thread stack size exceeded due to excessive recursion`  
**Thread:** Thread 0 - `Dispatch queue: com.apple.main-thread` (**MAIN THREAD!**)

**КРИТИЧЕСКОЕ ОТЛИЧИЕ ОТ ПРЕДЫДУЩИХ КРАШЕЙ:**
- BUILD 101-103: Рекурсия в **background thread** (Thread 2, 6, 12)
- BUILD 104: Рекурсия в **MAIN THREAD** (Thread 0)!

**Когда происходит краш:**
1. При **первом переходе** на страницу "Защита АЛАДДИН"
2. При **втором заходе** на страницу и переключении тумблеров

---

## 🔍 АНАЛИЗ STACK TRACE

### Thread 0 (Crashed - MAIN THREAD):

```
0   libswiftCore.dylib             swift::swift_slowAllocTyped(...) + 8
1   libswiftCore.dylib             swift_allocObject + 136
2   libswiftCore.dylib             static _DictionaryStorage.allocate(...) + 272
3   libswiftCore.dylib             static _DictionaryStorage.resize(...) + 40
4   ALADDIN                        0x103047f8c  // Dictionary создается здесь
5   ALADDIN                        0x103044060  // Dictionary operation
6   ALADDIN                        0x1030439c4  // Рекурсия начинается здесь
7   ALADDIN                        0x10314d864  // Рекурсивный вызов
8   ALADDIN                        0x10314dfac  // Рекурсивный вызов
9   ALADDIN                        0x10314dfbc  // РЕКУРСИЯ! (повторяется много раз)
10  ALADDIN                        0x10314dfbc  // РЕКУРСИЯ!
11  ALADDIN                        0x10314dfbc  // РЕКУРСИЯ!
12  ALADDIN                        0x10314dfbc  // РЕКУРСИЯ!
13  ALADDIN                        0x10314dfbc  // РЕКУРСИЯ!
14  ALADDIN                        0x10314dfbc  // РЕКУРСИЯ!
15  ALADDIN                        0x10300ecb0  // Возможно: SwiftUI View update
16  ALADDIN                        0x102d68f35  // Возможно: SwiftUI body
17  ALADDIN                        0x1030432dd  // Возможно: View recreation
18  ALADDIN                        0x102d68f35  // Возможно: SwiftUI body
19  libswift_Concurrency.dylib      completeTaskWithClosure(...) + 1
```

**Вывод:**
- Рекурсия происходит в **main thread** (Thread 0)
- Dictionary создается и вызывает рекурсию при resize
- Адрес `0x10314dfbc` повторяется много раз - это рекурсивный вызов
- Рекурсия связана с SwiftUI View обновлением (строки 15-18)

---

## 🔍 НАЙДЕННЫЕ ПРИЧИНЫ КРАША

### ❌ ПРИЧИНА 1: Рекурсия в `NetworkProtectionViewModel.init()` через `Task {}`

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`  
**Строки:** 51-64

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

**Что происходит:**
1. View создается → `NetworkProtectionViewModel.init()` вызывается
2. `Task {}` запускает `loadComponentStatuses()`
3. `loadComponentStatuses()` обновляет `@Published` свойства (10 свойств)
4. Обновление `@Published` вызывает обновление View
5. SwiftUI может пересоздать View
6. `init()` вызывается снова
7. `Task {}` создается снова
8. **РЕКУРСИЯ!**

**Почему это проблема:**
- `Task {}` в `init()` создается синхронно при инициализации
- Если View пересоздается из-за обновления `@Published`, `init()` вызывается снова
- Это создает бесконечный цикл рекурсии

---

### ❌ ПРИЧИНА 2: Множественные вызовы `.onAppear` с созданием Dictionary

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
2. `trackComponentScreenView()` создает Dictionary:
   ```swift
   let parameters: [String: Any] = [
       "screen_name": screenName,
       "component_count": componentCount,
       "timestamp": Date().timeIntervalSince1970
   ]
   ```
3. Если View пересоздается многократно, `.onAppear` вызывается многократно
4. Dictionary создается многократно в main thread
5. При рекурсии Dictionary пытается изменить размер многократно
6. **РЕКУРСИЯ!**

**Почему это проблема:**
- `.onAppear` может вызываться многократно при пересоздании View
- Нет защиты от повторного вызова
- Dictionary создается каждый раз заново

---

### ❌ ПРИЧИНА 3: `updateStatusForComponent()` использует `Task { @MainActor in }` внутри `@MainActor` класса

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`  
**Строки:** 241-242

**Проблема:**
```swift
@MainActor
class NetworkProtectionViewModel: ObservableObject {
    // ...
    private func updateStatusForComponent(componentId: String, isEnabled: Bool) {
        Task { @MainActor in  // ❌ ПРОБЛЕМА!
            switch componentId {
            case "crash_detection_agent":
                self.crashDetectionEnabled = isEnabled
            // ...
            }
        }
    }
}
```

**Что происходит:**
1. Класс уже имеет `@MainActor`
2. Метод вызывается из `loadComponentStatuses()` который уже на `@MainActor`
3. `Task { @MainActor in }` создает новый Task, даже если мы уже на main thread
4. При рекурсии это может создавать множественные Tasks
5. Каждый Task обновляет `@Published` свойства
6. Это вызывает обновление View
7. View пересоздается
8. **РЕКУРСИЯ!**

**Почему это проблема:**
- `Task { @MainActor in }` внутри `@MainActor` метода создает ненужный Task
- Это может вызывать проблемы при рекурсии
- Обновление `@Published` должно быть синхронным, а не через Task

---

### ❌ ПРИЧИНА 4: `loadDemoModeStatuses()` использует `await MainActor.run {}` внутри `@MainActor` метода

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`  
**Строки:** 88-100

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

**Что происходит:**
1. Метод уже на `@MainActor`
2. `await MainActor.run {}` создает ненужный переход на main thread
3. При рекурсии это может вызывать проблемы
4. `updateStatusForComponent()` внутри создает еще один `Task { @MainActor in }`
5. Это создает множественные Tasks
6. **РЕКУРСИЯ!**

---

### ❌ ПРИЧИНА 5: Отсутствие защиты от повторной загрузки статусов

**Проблема:**
- Нет флага для предотвращения повторной загрузки статусов
- Если View пересоздается, `init()` вызывается снова
- `loadComponentStatuses()` вызывается снова
- Это может вызывать рекурсию

---

## 🔬 ДЕТАЛЬНЫЙ АНАЛИЗ КАЖДОЙ ПРИЧИНЫ

### Причина 1: Почему `Task {}` в `init()` вызывает рекурсию?

**Механизм рекурсии:**
```
1. View создается
   ↓
2. NetworkProtectionViewModel.init() вызывается
   ↓
3. Task { await loadComponentStatuses() } создается
   ↓
4. loadComponentStatuses() обновляет @Published свойства (10 свойств)
   ↓
5. SwiftUI получает уведомление об изменении @Published
   ↓
6. SwiftUI обновляет View
   ↓
7. SwiftUI может пересоздать View (если есть изменения в структуре)
   ↓
8. NetworkProtectionViewModel.init() вызывается СНОВА
   ↓
9. Task { await loadComponentStatuses() } создается СНОВА
   ↓
10. РЕКУРСИЯ!
```

**Почему это происходит:**
- SwiftUI может пересоздать View при обновлении `@Published` свойств
- Особенно если обновляется много свойств одновременно (10 свойств)
- `Task {}` в `init()` создается синхронно, что может вызывать проблемы

---

### Причина 2: Почему `.onAppear` вызывается многократно?

**Механизм:**
- `.onAppear` вызывается каждый раз, когда View появляется в иерархии
- Если View пересоздается, `.onAppear` вызывается снова
- Нет защиты от повторного вызова
- `trackComponentScreenView()` создает Dictionary каждый раз

**Почему это проблема:**
- Dictionary создается в main thread при каждом вызове
- При рекурсии это может вызывать проблемы с `Dictionary.resize`

---

### Причина 3: Почему `Task { @MainActor in }` внутри `@MainActor` метода вызывает проблемы?

**Проблема:**
- Класс уже имеет `@MainActor`
- Метод уже выполняется на main thread
- `Task { @MainActor in }` создает новый Task, даже если мы уже на main thread
- Это может вызывать проблемы при рекурсии

**Правильное решение:**
- Если метод уже на `@MainActor`, не нужно создавать `Task { @MainActor in }`
- Обновление `@Published` должно быть синхронным

---

## 📊 СПИСОК ВСЕХ ПРОБЛЕМ

### Критические проблемы (вызывают краш):

1. **`NetworkProtectionViewModel.init()` - `Task {}` в init()**
   - Строки 61-63: `Task { await loadComponentStatuses() }`
   - Вызывает рекурсию при пересоздании View

2. **`updateStatusForComponent()` - `Task { @MainActor in }` внутри `@MainActor` метода**
   - Строка 242: `Task { @MainActor in }`
   - Создает ненужный Task при обновлении `@Published`

3. **`.onAppear` - множественные вызовы `trackComponentScreenView()`**
   - Строки 365-371: Нет защиты от повторного вызова
   - Dictionary создается при каждом вызове

4. **`loadDemoModeStatuses()` - `await MainActor.run {}` внутри `@MainActor` метода**
   - Строка 94: `await MainActor.run {}`
   - Создает ненужный переход на main thread

5. **Отсутствие защиты от повторной загрузки статусов**
   - Нет флага для предотвращения повторной загрузки

---

## ✅ РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ

### Приоритет 1: Критический

**1. Убрать `Task {}` из `init()` и загружать статусы в `.onAppear`**

**Проблема:**
```swift
init(...) {
    // ...
    Task {  // ❌ УБРАТЬ!
        await loadComponentStatuses()
    }
}
```

**Решение:**
```swift
init(...) {
    self.statusService = statusService
    self.configurationService = configurationService
    self.retryManager = retryManager
    // ✅ УБРАЛИ Task {} из init()
}

// В NetworkProtectionScreen:
.onAppear {
    // ✅ Загружаем статусы только один раз
    if !viewModel.hasLoadedStatuses {
        Task {
            await viewModel.loadComponentStatuses()
        }
    }
    
    // Отследить просмотр экрана с компонентами
    ComponentAnalytics.shared.trackComponentScreenView(
        screenName: "NetworkProtectionScreen",
        componentCount: 10
    )
}
```

---

**2. Убрать `Task { @MainActor in }` из `updateStatusForComponent()`**

**Проблема:**
```swift
private func updateStatusForComponent(componentId: String, isEnabled: Bool) {
    Task { @MainActor in  // ❌ УБРАТЬ!
        switch componentId {
        case "crash_detection_agent":
            self.crashDetectionEnabled = isEnabled
        // ...
        }
    }
}
```

**Решение:**
```swift
private func updateStatusForComponent(componentId: String, isEnabled: Bool) {
    // ✅ УБРАЛИ Task { @MainActor in } - метод уже на @MainActor
    switch componentId {
    case "crash_detection_agent":
        self.crashDetectionEnabled = isEnabled
    case "roadside_assistance_agent":
        self.roadsideAssistanceEnabled = isEnabled
    // ... остальные компоненты
    }
}
```

---

**3. Убрать `await MainActor.run {}` из `loadDemoModeStatuses()` и `loadProductionModeStatuses()`**

**Проблема:**
```swift
private func loadDemoModeStatuses(...) async {
    for item in prioritizedItems {
        let isEnabled = UserDefaults.standard.bool(forKey: userDefaultsKey)
        
        await MainActor.run {  // ❌ УБРАТЬ!
            self.updateStatusForComponent(componentId: item.id, isEnabled: isEnabled)
        }
    }
}
```

**Решение:**
```swift
private func loadDemoModeStatuses(...) async {
    // ✅ УБРАЛИ await MainActor.run {} - метод уже на @MainActor
    for item in prioritizedItems {
        let isEnabled = UserDefaults.standard.bool(forKey: userDefaultsKey)
        self.updateStatusForComponent(componentId: item.id, isEnabled: isEnabled)
    }
}
```

---

**4. Добавить защиту от повторного вызова в `.onAppear`**

**Проблема:**
```swift
.onAppear {
    ComponentAnalytics.shared.trackComponentScreenView(...)  // ❌ Вызывается многократно
}
```

**Решение:**
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

**5. Добавить флаг для предотвращения повторной загрузки статусов**

**Решение:**
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

## 🎯 ИТОГОВЫЙ ВЫВОД

**Основная проблема:** Рекурсия в main thread из-за:
1. `Task {}` в `init()` вызывает пересоздание View
2. `Task { @MainActor in }` внутри `@MainActor` метода создает ненужные Tasks
3. `await MainActor.run {}` внутри `@MainActor` метода создает ненужные переходы
4. Множественные вызовы `.onAppear` без защиты
5. Отсутствие защиты от повторной загрузки статусов

**Решение:** 
1. Убрать `Task {}` из `init()`
2. Убрать `Task { @MainActor in }` из `updateStatusForComponent()`
3. Убрать `await MainActor.run {}` из методов загрузки
4. Добавить защиту от повторного вызова в `.onAppear`
5. Добавить флаг для предотвращения повторной загрузки статусов

---

**Статус:** 🔴 **КРИТИЧЕСКАЯ ПРОБЛЕМА - НУЖНЫ НЕМЕДЛЕННЫЕ ИСПРАВЛЕНИЯ**  
**Рекомендация:** Исправить все 5 проблем немедленно
