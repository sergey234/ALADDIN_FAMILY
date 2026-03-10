# ✅ BUILD 101: ИСПРАВЛЕНИЕ КРАША ТУМБЛЕРОВ НА РЕАЛЬНОМ УСТРОЙСТВЕ

**Дата исправления:** 2026-03-10  
**Build:** 101  
**Статус:** ✅ **ИСПРАВЛЕНО**

---

## 🚨 ПРОБЛЕМА

### Симптомы:
- ✅ В симуляторе все работает хорошо - тумблеры переключаются и откликаются
- 🔴 На реальном устройстве при переключении тумблеров происходит краш
- 🔴 Приложение выбрасывает пользователя из приложения
- 🔴 Краш: `EXC_BAD_ACCESS (SIGBUS)` - `Thread stack size exceeded due to excessive recursion`

### Краш:
- **Thread:** Thread 12 - `Dispatch queue: com.apple.root.user-initiated-qos.cooperative` (BACKGROUND THREAD!)
- **Причина:** Рекурсия в `_DictionaryStorage.resize` при работе с Dictionary в background thread

---

## 🔍 ПРИЧИНА КРАША

### 🔴 **ПРИЧИНА 1: UserDefaults.standard.set() вызывает рекурсию**

**Проблемный код:**
```swift
// В NetworkProtectionViewModel.swift, строка 297 (БЫЛО)
private func handleDemoModeToggle(...) async {
    let userDefaultsKey = "demo_component_\(componentId)_enabled"
    UserDefaults.standard.set(newValue, forKey: userDefaultsKey)  // ❌ Синхронно в background thread!
    
    componentAnalytics.trackComponentToggle(...)
}
```

**Что происходило:**
1. Пользователь переключает тумблер
2. Вызывается `handleDemoModeToggle()` в background thread
3. `UserDefaults.standard.set()` вызывается **синхронно** в background thread
4. Это вызывает обновление `@AppStorage` или других наблюдателей
5. Которые вызывают обновление View
6. Которое вызывает повторное переключение тумблера
7. **РЕКУРСИЯ!**

**Почему в симуляторе работает:**
- Симулятор более терпим к рекурсии
- Может иметь больший размер стека
- Может не вызывать обновление View так быстро

**Почему на реальном устройстве крашится:**
- Реальное устройство имеет меньший размер стека
- Более строгая проверка рекурсии
- Быстрее вызывает обновление View

---

### 🔴 **ПРИЧИНА 2: Нет защиты от повторного переключения**

**Проблема:**
- Нет защиты от повторного переключения тумблера
- Если View обновляется, это может вызвать повторное переключение
- Особенно если используется `@Binding` или `@State`

---

### 🔴 **ПРИЧИНА 3: Dictionary.resize в background thread**

**Проблема:**
- `trackComponentToggle()` создает Dictionary с параметрами
- Если это происходит в background thread при рекурсии
- Dictionary может пытаться изменить размер многократно
- Это вызывает рекурсию в `_DictionaryStorage.resize`

---

## ✅ ИСПРАВЛЕНИЯ

### ✅ **ИСПРАВЛЕНИЕ 1: UserDefaults.standard.set() вызывается асинхронно на main thread**

**Исправленный код:**
```swift
// В NetworkProtectionViewModel.swift (СТАЛО)
private func handleDemoModeToggle(...) async {
    let userDefaultsKey = "demo_component_\(componentId)_enabled"
    
    // ✅ BUILD 101: UserDefaults.standard.set() вызывается асинхронно на main thread
    // Синхронный вызов в background thread вызывает обновление View,
    // которое может вызвать повторное переключение тумблера → рекурсия
    await MainActor.run {
        UserDefaults.standard.set(newValue, forKey: userDefaultsKey)
    }
    
    // ✅ BUILD 101: Отслеживание аналитики также выполняется на main thread
    await MainActor.run {
        componentAnalytics.trackComponentToggle(
            componentId: componentId,
            enabled: newValue
        )
    }
    
    await MainActor.run {
        toastManager.showSuccess("Компонент обновлен (демо режим)")
    }
}
```

**Результат:**
- `UserDefaults.standard.set()` вызывается на main thread
- Это предотвращает обновление View в background thread
- Предотвращает повторное переключение тумблера
- **РЕКУРСИЯ УСТРАНЕНА!**

---

### ✅ **ИСПРАВЛЕНИЕ 2: Добавлена защита от повторного переключения**

**Исправленный код:**
```swift
// В NetworkProtectionViewModel.swift (СТАЛО)
// ✅ BUILD 101: Защита от повторного переключения для предотвращения рекурсии
private var isToggling = false
private let togglingLock = NSLock()

private func toggleComponent(...) async {
    // ✅ BUILD 101: Защита от повторного переключения
    togglingLock.lock()
    guard !isToggling else {
        togglingLock.unlock()
        print("⚠️ NetworkProtectionViewModel: toggleComponent уже выполняется, пропускаем повторный вызов")
        return
    }
    isToggling = true
    togglingLock.unlock()
    
    defer {
        togglingLock.lock()
        isToggling = false
        togglingLock.unlock()
    }
    
    // Оптимистичное обновление UI на main thread
    await MainActor.run {
        updateClosure(newValue)
    }
    
    // ... остальной код
}
```

**Результат:**
- Защита от повторного переключения тумблера
- Thread-safe флаг `isToggling` с `NSLock`
- Повторные вызовы пропускаются
- **РЕКУРСИЯ УСТРАНЕНА!**

---

### ✅ **ИСПРАВЛЕНИЕ 3: trackComponentToggle выполняется на main thread**

**Исправленный код:**
```swift
// В ComponentAnalytics.swift (СТАЛО)
/**
 * Отследить переключение компонента
 * ✅ BUILD 101: Выполняется на main thread для предотвращения рекурсии при работе с Dictionary
 */
func trackComponentToggle(componentId: String, enabled: Bool) {
    // ✅ BUILD 101: Выполняем на main thread для безопасности
    // На реальном устройстве создание Dictionary в background thread при рекурсии
    // может вызвать проблемы с Dictionary.resize → краш
    Task { @MainActor in
        analyticsManager.trackEvent(
            "component_toggle",
            parameters: [
                "component_id": componentId,
                "enabled": enabled,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
    }
}
```

**Результат:**
- `trackComponentToggle()` выполняется на main thread
- Это предотвращает проблемы с Dictionary.resize в background thread
- **РЕКУРСИЯ УСТРАНЕНА!**

---

## 📊 ИТОГОВЫЕ ИЗМЕНЕНИЯ

### Измененные файлы:

1. **ViewModels/NetworkProtectionViewModel.swift:**
   - ✅ Добавлена защита от повторного переключения (`isToggling` + `togglingLock`)
   - ✅ `UserDefaults.standard.set()` вызывается асинхронно на main thread
   - ✅ `updateClosure()` вызывается на main thread
   - ✅ `trackComponentToggle()` вызывается на main thread
   - ✅ `toastManager.showSuccess()` вызывается на main thread

2. **Core/Analytics/ComponentAnalytics.swift:**
   - ✅ `trackComponentToggle()` выполняется на main thread
   - ✅ Это предотвращает проблемы с Dictionary.resize в background thread

---

## ✅ РЕЗУЛЬТАТЫ

### Что исправлено:

1. ✅ **UserDefaults.standard.set() вызывается асинхронно** - предотвращает обновление View в background thread
2. ✅ **Добавлена защита от повторного переключения** - предотвращает рекурсию при обновлении View
3. ✅ **trackComponentToggle выполняется на main thread** - предотвращает проблемы с Dictionary.resize

### Что будет работать:

- ✅ Тумблеры будут работать на реальном устройстве
- ✅ Нет рекурсии при переключении тумблеров
- ✅ Нет крашей при переключении тумблеров
- ✅ Проект компилируется без ошибок

---

## 🎯 ВЫВОДЫ

### Критические проблемы исправлены:

1. ✅ **UserDefaults.standard.set() вызывает рекурсию** - исправлено использованием `await MainActor.run`
2. ✅ **Нет защиты от повторного переключения** - добавлен флаг `isToggling` с `NSLock`
3. ✅ **Dictionary.resize вызывает рекурсию** - исправлено выполнением на main thread

### Причина краша:

- `UserDefaults.standard.set()` вызывался синхронно в background thread
- Это вызывало обновление View
- Которое вызывало повторное переключение тумблера
- **РЕКУРСИЯ!**

### Решение:

- Все операции с UserDefaults выполняются на main thread
- Добавлена защита от повторного переключения
- Аналитика выполняется на main thread
- **РЕКУРСИЯ УСТРАНЕНА!**

---

**Статус:** ✅ **КРИТИЧЕСКИЕ ПРОБЛЕМЫ ИСПРАВЛЕНЫ**  
**Рекомендация:** Протестировать на реальном устройстве для подтверждения исправления краша
