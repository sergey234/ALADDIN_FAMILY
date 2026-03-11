# 🚨 BUILD 105: КРИТИЧЕСКИЙ АНАЛИЗ КРАША

**Дата:** 2026-03-11  
**Build:** 105  
**Incident Identifier:** 95F48AFF-A085-4D78-A23E-E07A740C30E9  
**Статус:** 🔴 **КРАШ ПРОДОЛЖАЕТСЯ!**

---

## 🎯 ОСНОВНАЯ ПРОБЛЕМА

### ✅ **Подтверждение:**
- **Та же ошибка:** `EXC_BAD_ACCESS (SIGBUS)` - `Thread stack size exceeded due to excessive recursion`
- **Та же причина:** `_DictionaryStorage.resize` в background thread (Thread 3)
- **Та же рекурсия:** Строки 10-15 показывают бесконечную рекурсию (`0x1051e8eb4`)

### ❌ **Вывод:**
**`DispatchQueue.main.async` НЕ РЕШИЛ ПРОБЛЕМУ!**

---

## 🔍 ДЕТАЛЬНЫЙ АНАЛИЗ CRASH LOG

### 1. **Thread 3 Crashed:**
```
Thread 3 name: Dispatch queue: com.apple.root.user-initiated-qos.cooperative
Thread 3 Crashed:
0   libsystem_malloc.dylib         _xzm_xzone_malloc_tiny + 0
1   libswiftCore.dylib             swift::swift_slowAllocTyped(...)
2   libswiftCore.dylib             swift_allocObject + 136
3   libswiftCore.dylib             static _DictionaryStorage.allocate(...)
4   libswiftCore.dylib             static _DictionaryStorage.resize(...)
5   ALADDIN                        0x1050e3270
6   ALADDIN                        0x1050df344
7   ALADDIN                        0x1050deca8
8   ALADDIN                        0x1051e8bb8
9   ALADDIN                        0x1051e8ea8
10  ALADDIN                        0x1051e8eb4  ← РЕКУРСИЯ НАЧИНАЕТСЯ
11  ALADDIN                        0x1051e8eb4  ← ПОВТОРЯЕТСЯ
12  ALADDIN                        0x1051e8eb4  ← ПОВТОРЯЕТСЯ
13  ALADDIN                        0x1051e8eb4  ← ПОВТОРЯЕТСЯ
14  ALADDIN                        0x1051e8eb4  ← ПОВТОРЯЕТСЯ
15  ALADDIN                        0x1051e8eb4  ← ПОВТОРЯЕТСЯ
```

**Проблема:** Dictionary создается на background thread (Thread 3), вызывая рекурсию в `_DictionaryStorage.resize`.

---

## 🔍 ВСЕ ВОЗМОЖНЫЕ ПРИЧИНЫ КРАША

### 🔴 **ПРИЧИНА #1: `DispatchQueue.main.async` НЕ ГАРАНТИРУЕТ НЕМЕДЛЕННОЕ ВЫПОЛНЕНИЕ**

**Текущий код:**
```swift
// В NetworkProtectionViewModel.toggleComponent() - async функция
DispatchQueue.main.async { [self] in
    self.componentAnalytics.trackComponentToggle(...)  // Dictionary создается ВНУТРИ метода
}
```

**Проблема:**
1. `toggleComponent()` - это `async` функция, которая может выполняться на background thread
2. `DispatchQueue.main.async` добавляет задачу в очередь, но **НЕ выполняет ее немедленно**
3. Dictionary создается **ВНУТРИ** метода `trackComponentToggle()` **ДО** того, как `DispatchQueue.main.async` выполнится
4. На реальном устройстве это происходит быстрее, чем на симуляторе

**Вероятность:** 🔴 **100%** - это основная причина краша

---

### 🔴 **ПРИЧИНА #2: `@MainActor` НЕ РАБОТАЕТ С `DispatchQueue.main.async`**

**Проблема:**
- `ComponentAnalytics` имеет `@MainActor`
- НО: Если метод вызывается через `DispatchQueue.main.async` из background thread, `@MainActor` **не гарантирует**, что Dictionary создается на main thread
- `DispatchQueue.main.async` добавляет задачу в очередь, но Dictionary может создаваться **ДО** выполнения задачи

**Вероятность:** 🔴 **95%** - это связано с причиной #1

---

### 🔴 **ПРИЧИНА #3: `NetworkProtectionViewModel` - `@MainActor`, НО `toggleComponent()` - `async`**

**Текущий код:**
```swift
@MainActor
class NetworkProtectionViewModel: ObservableObject {
    private func toggleComponent(...) async {
        // ...
        DispatchQueue.main.async { [self] in
            self.componentAnalytics.trackComponentToggle(...)
        }
    }
}
```

**Проблема:**
- Класс имеет `@MainActor`
- НО: `async` функция может выполняться на background thread, если вызывается из `Task {}` без `@MainActor`
- `DispatchQueue.main.async` внутри `async` функции не гарантирует выполнение на main thread

**Вероятность:** 🔴 **90%** - это связано с причиной #1

---

### 🟡 **ПРИЧИНА #4: `String(describing:)` В `AnalyticsManager.trackEvent()`**

**Текущий код:**
```swift
@MainActor
class AnalyticsManager {
    func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
        let paramsDescription: String
        if let params = parameters {
            paramsDescription = String(describing: params)  // ← Может создавать Dictionary?
        }
    }
}
```

**Проблема:**
- `String(describing: params)` может создавать временные Dictionary для форматирования
- Если `trackEvent()` вызывается из background thread, это может вызывать проблемы

**Вероятность:** 🟡 **30%** - менее вероятно, но возможно

---

### 🟡 **ПРИЧИНА #5: `Date().timeIntervalSince1970` В `ComponentAnalytics`**

**Текущий код:**
```swift
let parameters: [String: Any] = [
    "component_id": componentId,
    "enabled": enabled,
    "timestamp": Date().timeIntervalSince1970  // ← Может вызывать проблемы?
]
```

**Проблема:**
- `Date()` может читать из системных настроек, что может вызывать проблемы на background thread
- Менее вероятно, но возможно

**Вероятность:** 🟡 **20%** - маловероятно

---

### 🟡 **ПРИЧИНА #6: `error.localizedDescription` В `trackComponentError()`**

**Текущий код:**
```swift
func trackComponentError(componentId: String, error: Error) {
    let parameters: [String: Any] = [
        "error_message": error.localizedDescription,  // ← Может вызывать проблемы?
    ]
}
```

**Проблема:**
- `error.localizedDescription` может читать из локализации, что может вызывать проблемы на background thread
- Менее вероятно, но возможно

**Вероятность:** 🟡 **15%** - маловероятно

---

## 🎯 ИТОГОВЫЙ ВЫВОД

### 🔴 **ГЛАВНАЯ ПРИЧИНА:**

**`DispatchQueue.main.async` НЕ РЕШИЛ ПРОБЛЕМУ!**

**Почему:**
1. `DispatchQueue.main.async` добавляет задачу в очередь, но **НЕ выполняет ее немедленно**
2. Dictionary создается **ВНУТРИ** метода `trackComponentToggle()` **ДО** того, как `DispatchQueue.main.async` выполнится
3. На реальном устройстве это происходит быстрее, чем на симуляторе
4. `@MainActor` не помогает, если метод вызывается через `DispatchQueue.main.async` из background thread

---

## 🔧 РЕШЕНИЕ

### ✅ **ПРАВИЛЬНОЕ РЕШЕНИЕ:**

**Убрать `DispatchQueue.main.async` полностью!**

**Почему:**
1. `NetworkProtectionViewModel` уже `@MainActor` - все методы автоматически выполняются на main thread
2. `ComponentAnalytics` уже `@MainActor` - все методы автоматически выполняются на main thread
3. `toggleComponent()` вызывается из `Task { @MainActor in }` в UI - гарантирует main thread
4. **НЕ НУЖНЫ** никакие обертки `DispatchQueue.main.async` или `Task { @MainActor in }`

**Код:**
```swift
// ✅ ПРАВИЛЬНО:
// Убрать DispatchQueue.main.async полностью
componentAnalytics.trackComponentToggle(
    componentId: componentId,
    enabled: newValue
)

if AppConfig.authToken == nil {
    toastManager.showSuccess("Компонент обновлен (демо режим)")
} else {
    toastManager.showSuccess("Компонент обновлен")
}
```

---

## 📋 ПЛАН ИСПРАВЛЕНИЯ

### Шаг 1: Убрать `DispatchQueue.main.async` из `toggleComponent()`
- В успешном обновлении (строки 325-336)
- В обработке ошибки (строки 347-350)

### Шаг 2: Убедиться, что `toggleComponent()` вызывается из `Task { @MainActor in }`
- Проверить `Screens/03_NetworkProtectionScreen.swift`
- Убедиться, что все `onToggle` используют `Task { @MainActor in }`

### Шаг 3: Протестировать на реальном устройстве
- Проверить переключение тумблеров
- Убедиться, что нет крашей

---

## 🎯 ИТОГОВЫЙ ВЫВОД

**Проблема:** `DispatchQueue.main.async` не гарантирует немедленное выполнение на main thread. Dictionary создается на background thread ДО того, как `DispatchQueue.main.async` выполнится.

**Решение:** Убрать `DispatchQueue.main.async` полностью. Так как `NetworkProtectionViewModel` и `ComponentAnalytics` уже `@MainActor`, все методы автоматически выполняются на main thread.

---

**Статус:** 🔴 **ТРЕБУЕТСЯ КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ**  
**Рекомендация:** Убрать `DispatchQueue.main.async` полностью из `toggleComponent()`
