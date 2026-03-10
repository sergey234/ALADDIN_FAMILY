# 🚨 BUILD 103: КРИТИЧЕСКИЙ АНАЛИЗ КРАША

**Дата:** 2026-03-11  
**Build:** 103  
**Статус:** ❌ **КРАШ ПРОДОЛЖАЕТСЯ**

---

## 📋 ОПИСАНИЕ ПРОБЛЕМЫ

**Краш происходит:**
- При нажатии на тумблер на странице "Защита ALADDIN"
- При нажатии на кнопку "Сохранить" в настройках компонентов

**Тип краша:**
- `EXC_BAD_ACCESS (SIGBUS)`
- `Thread stack size exceeded due to excessive recursion`
- `Dictionary.resize` в background thread (`com.apple.root.user-initiated-qos.cooperative`)

---

## 🔍 АНАЛИЗ СТЕК ТРЕЙСА

### Thread 2/6 (Crashed):
```
0   libsystem_malloc.dylib         _xzm_xzone_malloc_tiny + 0
1   libswiftCore.dylib             swift::swift_slowAllocTyped(...)
2   libswiftCore.dylib             swift_allocObject
3   libswiftCore.dylib             static _DictionaryStorage.allocate(...)
4   libswiftCore.dylib             static _DictionaryStorage.resize(...)
5   ALADDIN                         0x10314072c  // Dictionary создается здесь
6   ALADDIN                         0x10313c800  // Рекурсия начинается здесь
7   ALADDIN                         0x10313c164
8   ALADDIN                         0x103246004  // Рекурсия продолжается
9-15 ALADDIN                        0x103246300  // Рекурсия (повторяется 7 раз)
```

**Вывод:** Dictionary создается в background thread и вызывает рекурсию при resize.

---

## 🎯 НАЙДЕННЫЕ ПРИЧИНЫ КРАША

### ❌ ПРИЧИНА 1: Вызовы аналитики в `toggleComponent` без явного `await MainActor.run`

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`  
**Строки:** 322-325, 340

**Проблема:**
```swift
// ✅ BUILD 102: Автоматически на main thread благодаря @MainActor
componentAnalytics.trackComponentToggle(
    componentId: componentId,
    enabled: newValue
)
```

**Почему это проблема:**
- Хотя `ComponentAnalytics` имеет `@MainActor`, вызов из `async` функции `toggleComponent` может выполняться в background thread
- Swift Concurrency может "наследовать" контекст выполнения из `Task {}`
- Dictionary literal `["component_id": ..., "enabled": ..., "timestamp": ...]` создается **ДО** переключения на main thread

**Решение:**
```swift
await MainActor.run {
    componentAnalytics.trackComponentToggle(
        componentId: componentId,
        enabled: newValue
    )
}
```

---

### ❌ ПРИЧИНА 2: Создание Dictionary для `ComponentConfiguration` в background thread

**Файлы:**
- `Shared/Components/Modals/NetworkSecuritySettingsModal.swift` (строки 172-183)
- `Shared/Components/Modals/PhishingProtectionSettingsModal.swift` (строки 169-180)
- `ViewModels/NetworkSecuritySettingsViewModel.swift` (строки 124-135)
- `ViewModels/PhishingSettingsViewModel.swift` (строки 145-156)

**Проблема:**
```swift
Task {
    // ...
    let config = ComponentConfiguration(
        isEnabled: isComponentEnabled,
        priority: .normal,
        additionalSettings: [
            "blockUnsafeNetworks": AnyCodable(blockUnsafeNetworks),
            "warnOnPublicWiFi": AnyCodable(warnOnPublicWiFi),
            // ... еще Dictionary создается здесь
        ]
    )
    // ...
}
```

**Почему это проблема:**
- `Task {}` создает background thread
- Dictionary literal `additionalSettings` создается в background thread
- Это вызывает рекурсию `Dictionary.resize`

**Решение:**
```swift
Task {
    // ...
    let config = await MainActor.run {
        ComponentConfiguration(
            isEnabled: isComponentEnabled,
            priority: .normal,
            additionalSettings: [
                "blockUnsafeNetworks": AnyCodable(blockUnsafeNetworks),
                "warnOnPublicWiFi": AnyCodable(warnOnPublicWiFi),
                // ...
            ]
        )
    }
    // ...
}
```

---

### ❌ ПРИЧИНА 3: Вызовы `trackComponentSettingsSaved` без явного `await MainActor.run`

**Файлы:** Все модальные окна настроек компонентов

**Проблема:**
- Если `trackComponentSettingsSaved` вызывается из `Task {}`, Dictionary создается в background thread
- Нужно проверить все места вызова и обернуть в `await MainActor.run {}`

---

### ❌ ПРИЧИНА 4: `toastManager.showSuccess/showError` может вызываться из background thread

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`  
**Строки:** 328-331, 341

**Проблема:**
```swift
toastManager.showSuccess("Компонент обновлен")
```

**Почему это проблема:**
- `ToastManager` может создавать Dictionary для внутренних операций
- Вызов из `async` функции может выполняться в background thread

**Решение:**
```swift
await MainActor.run {
    toastManager.showSuccess("Компонент обновлен")
}
```

---

## 🔬 ДЕТАЛЬНЫЙ АНАЛИЗ КАЖДОЙ ПРИЧИНЫ

### Причина 1: Почему `@MainActor` не помогает в `async` функции?

**Проблема:**
- `@MainActor` на классе гарантирует, что методы класса выполняются на main thread
- НО: если метод вызывается из `async` функции, которая выполняется в background thread, Swift Concurrency может "наследовать" контекст
- Dictionary literal создается **ДО** вызова метода, поэтому он создается в background thread

**Пример:**
```swift
@MainActor
class ComponentAnalytics {
    func trackComponentToggle(componentId: String, enabled: Bool) {
        // Dictionary создается здесь
        let parameters: [String: Any] = [
            "component_id": componentId,
            "enabled": enabled,
            "timestamp": Date().timeIntervalSince1970
        ]
        // ...
    }
}

// В NetworkProtectionViewModel:
async func toggleComponent(...) {
    // Вызов из async функции
    componentAnalytics.trackComponentToggle(...) // ❌ Dictionary может создаться в background thread
}
```

**Решение:**
```swift
async func toggleComponent(...) {
    await MainActor.run {
        componentAnalytics.trackComponentToggle(...) // ✅ Dictionary создается на main thread
    }
}
```

---

### Причина 2: Почему `Task {}` создает background thread?

**Проблема:**
- `Task {}` создает новый async контекст
- По умолчанию он может выполняться в background thread (особенно если вызывается из UI)
- Dictionary literal создается в этом контексте

**Пример:**
```swift
Task {
    // Это выполняется в background thread
    let config = ComponentConfiguration(
        additionalSettings: [
            "key": value  // ❌ Dictionary создается в background thread
        ]
    )
}
```

**Решение:**
```swift
Task {
    let config = await MainActor.run {
        ComponentConfiguration(
            additionalSettings: [
                "key": value  // ✅ Dictionary создается на main thread
            ]
        )
    }
}
```

---

## 📊 СПИСОК ВСЕХ ФАЙЛОВ С ПРОБЛЕМАМИ

### Высокий приоритет (вызывают краш):

1. **`ViewModels/NetworkProtectionViewModel.swift`**
   - Строки 322-325: `componentAnalytics.trackComponentToggle()` без `await MainActor.run`
   - Строки 328-331: `toastManager.showSuccess()` без `await MainActor.run`
   - Строки 340: `componentAnalytics.trackComponentError()` без `await MainActor.run`
   - Строки 341: `toastManager.showError()` без `await MainActor.run`

2. **`Shared/Components/Modals/NetworkSecuritySettingsModal.swift`**
   - Строки 172-183: Создание `ComponentConfiguration` с Dictionary в `Task {}`

3. **`Shared/Components/Modals/PhishingProtectionSettingsModal.swift`**
   - Строки 169-180: Создание `ComponentConfiguration` с Dictionary в `Task {}`

4. **`ViewModels/NetworkSecuritySettingsViewModel.swift`**
   - Строки 124-135: Создание `ComponentConfiguration` с Dictionary в `Task {}`

5. **`ViewModels/PhishingSettingsViewModel.swift`**
   - Строки 145-156: Создание `ComponentConfiguration` с Dictionary в `Task {}`

### Средний приоритет (потенциальные проблемы):

6. **`Shared/Components/Modals/MobileSecuritySettingsModal.swift`**
   - Проверить создание `ComponentConfiguration` в `Task {}`

7. **`ViewModels/IncidentResponseSettingsViewModel.swift`**
   - Проверить создание `ComponentConfiguration` в `Task {}`

8. **Все другие модальные окна настроек компонентов**
   - Проверить вызовы `trackComponentSettingsSaved`

---

## ✅ ПЛАН ИСПРАВЛЕНИЙ

### Шаг 1: Исправить `NetworkProtectionViewModel.swift`

```swift
// Успешное обновление
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

// В catch блоке:
await MainActor.run {
    updateClosure(!newValue)
    componentAnalytics.trackComponentError(componentId: componentId, error: error)
    toastManager.showError("Ошибка: \(error.localizedDescription)")
}
```

### Шаг 2: Исправить все модальные окна настроек

```swift
Task {
    // ...
    let config = await MainActor.run {
        ComponentConfiguration(
            isEnabled: isComponentEnabled,
            priority: .normal,
            additionalSettings: [
                "key": AnyCodable(value),
                // ...
            ]
        )
    }
    // ...
}
```

### Шаг 3: Проверить все вызовы `trackComponentSettingsSaved`

Обернуть все вызовы в `await MainActor.run {}`.

---

## 🎯 ИТОГОВЫЙ ВЫВОД

**Основная проблема:** Dictionary создается в background thread, что вызывает рекурсию `Dictionary.resize`.

**Причины:**
1. Вызовы аналитики из `async` функции без явного `await MainActor.run`
2. Создание Dictionary для `ComponentConfiguration` в `Task {}`
3. Вызовы `toastManager` из `async` функции без явного `await MainActor.run`

**Решение:** Обернуть все создания Dictionary и вызовы аналитики в `await MainActor.run {}`.

---

**ГОТОВ К ИСПРАВЛЕНИЮ!** 🚀
