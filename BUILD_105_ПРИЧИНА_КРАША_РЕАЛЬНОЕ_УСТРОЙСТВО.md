# 🚨 BUILD 105: ПРИЧИНА КРАША НА РЕАЛЬНОМ УСТРОЙСТВЕ

**Дата:** 2026-03-11  
**Build:** 105  
**Проблема:** Тумблеры работают на симуляторе, но краш на реальном устройстве

---

## 🎯 ГЛАВНАЯ ПРИЧИНА

### Почему на симуляторе работает, а на реальном устройстве краш:

**Основная проблема:** `DispatchQueue.main.async` не гарантирует **немедленное** выполнение на main thread. Dictionary может создаваться **ДО** переключения на main thread, особенно на реальном устройстве из-за различий в производительности и таймингах.

---

## 🔍 ДЕТАЛЬНЫЙ АНАЛИЗ

### 1. Различия в производительности

**Симулятор:**
- Более мощный процессор (Mac)
- Больше памяти
- Медленнее выполнение (есть время для правильного переключения потоков)
- Менее строгая проверка thread safety

**Реальное устройство:**
- Ограниченные ресурсы
- Меньше памяти
- Быстрее выполнение (может не успеть переключиться на main thread)
- Более строгая проверка thread safety

---

### 2. Проблема с `DispatchQueue.main.async`

**Текущий код:**
```swift
DispatchQueue.main.async { [self] in
    self.componentAnalytics.trackComponentToggle(...)
}
```

**Что происходит:**

1. **На симуляторе:**
   - Выполнение медленнее
   - Есть время для переключения на main thread
   - Dictionary создается на main thread
   - ✅ Работает

2. **На реальном устройстве:**
   - Выполнение быстрее
   - `DispatchQueue.main.async` добавляет задачу в очередь
   - Задача выполняется **асинхронно** (не сразу!)
   - Dictionary может создаваться **ДО** выполнения задачи на main thread
   - ❌ Краш!

---

### 3. Проблема с `ComponentAnalytics`

**Код `ComponentAnalytics`:**
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
        analyticsManager.trackEvent("component_toggle", parameters: parameters)
    }
}
```

**Проблема:**
- Класс имеет `@MainActor`
- НО: Если метод вызывается из `async` функции `toggleComponent()`, которая выполняется на background thread
- `DispatchQueue.main.async` добавляет задачу в очередь, но Dictionary может создаваться **ДО** переключения на main thread
- На реальном устройстве это происходит быстрее, чем на симуляторе

---

## 🎯 РЕШЕНИЕ

### Использовать `Task { @MainActor in }` вместо `DispatchQueue.main.async`

**Почему это лучше:**

1. ✅ `Task { @MainActor in }` гарантирует выполнение на main actor **немедленно**
2. ✅ Dictionary создается на main thread автоматически
3. ✅ Работает одинаково на симуляторе и реальном устройстве
4. ✅ Современный подход Swift Concurrency
5. ✅ Более надежный для async функций

**Код:**
```swift
// ✅ РЕКОМЕНДУЕТСЯ:
Task { @MainActor in
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
let errorToReport = error
Task { @MainActor in
    componentAnalytics.trackComponentError(componentId: componentId, error: errorToReport)
    toastManager.showError("Ошибка: \(errorToReport.localizedDescription)")
}
```

---

## 📋 ПЛАН ИСПРАВЛЕНИЯ

### Шаг 1: Заменить `DispatchQueue.main.async` на `Task { @MainActor in }`
- В успешном обновлении (строки 325-336)
- В обработке ошибки (строки 347-350)

### Шаг 2: Протестировать на реальном устройстве
- Проверить переключение тумблеров
- Убедиться, что нет крашей

---

## 🎯 ИТОГОВЫЙ ВЫВОД

**Проблема:** `DispatchQueue.main.async` не гарантирует немедленное выполнение на main thread. Dictionary может создаваться на background thread, особенно на реальном устройстве из-за различий в производительности.

**Решение:** Использовать `Task { @MainActor in }` вместо `DispatchQueue.main.async` для гарантии выполнения на main actor и создания Dictionary на main thread.

---

**Статус:** 🔴 **ТРЕБУЕТСЯ ИСПРАВЛЕНИЕ**  
**Рекомендация:** Заменить `DispatchQueue.main.async` на `Task { @MainActor in }`
