# 🚨 BUILD 101: КРИТИЧЕСКИЙ АНАЛИЗ КРАША ТУМБЛЕРОВ НА РЕАЛЬНОМ УСТРОЙСТВЕ

**Дата краша:** 2026-03-10 23:26:58  
**Build:** 101  
**Статус:** 🔴 **КРИТИЧЕСКАЯ ПРОБЛЕМА - РЕКУРСИЯ ВЕРНУЛАСЬ!**

---

## 📊 АНАЛИЗ КРАША

### Основная информация:

**Exception Type:** `EXC_BAD_ACCESS (SIGBUS)`  
**Exception Message:** `Thread stack size exceeded due to excessive recursion`  
**Thread:** Thread 12 - `Dispatch queue: com.apple.root.user-initiated-qos.cooperative` (BACKGROUND THREAD!)

**Ключевое отличие от предыдущих крашей:**
- BUILD 99-100: Рекурсия в **main thread** (Thread 0) при форматировании дат
- BUILD 101: Рекурсия в **background thread** (Thread 12) при переключении тумблеров

---

## 🔍 АНАЛИЗ STACK TRACE

### Thread 12 (Crashed):

```
5   ALADDIN  0x1050f8a40  // _DictionaryStorage.resize
6   ALADDIN  0x1050f4b14  // Dictionary resize
7   ALADDIN  0x1050f4478  // Dictionary operation
8   ALADDIN  0x1051fdf20  // Рекурсия начинается здесь
9   ALADDIN  0x1051fe210  // Рекурсивный вызов
10  ALADDIN  0x1051fe21c  // РЕКУРСИЯ! (повторяется много раз)
11  ALADDIN  0x1051fe21c  // РЕКУРСИЯ!
12  ALADDIN  0x1051fe21c  // РЕКУРСИЯ!
...
```

**Вывод:**
- Рекурсия происходит в коде ALADDIN (не в системных библиотеках)
- Адрес `0x1051fe21c` повторяется много раз - это рекурсивный вызов
- Рекурсия связана с `Dictionary.resize` - это указывает на работу с Dictionary
- Рекурсия происходит в background thread при переключении тумблеров

---

## 🔍 ПРИЧИНЫ ВОЗНИКНОВЕНИЯ

### 🔴 **ПРИЧИНА 1: UserDefaults.standard.set() вызывает рекурсию**

**Проблема:**
```swift
// В NetworkProtectionViewModel.swift, строка 297
private func handleDemoModeToggle(...) async {
    let userDefaultsKey = "demo_component_\(componentId)_enabled"
    UserDefaults.standard.set(newValue, forKey: userDefaultsKey)  // ❌ ПРОБЛЕМА!
    
    componentAnalytics.trackComponentToggle(...)  // Вызывается после UserDefaults
}
```

**Что происходит:**
1. Пользователь переключает тумблер
2. Вызывается `handleDemoModeToggle()` в background thread
3. `UserDefaults.standard.set()` вызывается синхронно
4. Это может вызвать обновление `@AppStorage` или других наблюдателей
5. Которые могут вызвать обновление View
6. Которое может вызвать повторное переключение тумблера
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

### 🔴 **ПРИЧИНА 2: Dictionary.resize в background thread**

**Проблема:**
- `trackComponentToggle()` создает Dictionary с параметрами
- Если это происходит в background thread при рекурсии
- Dictionary может пытаться изменить размер многократно
- Это вызывает рекурсию в `_DictionaryStorage.resize`

**Код проблемы:**
```swift
// В ComponentAnalytics.swift, строка 24
func trackComponentToggle(componentId: String, enabled: Bool) {
    analyticsManager.trackEvent(
        "component_toggle",
        parameters: [  // ❌ Dictionary создается в background thread
            "component_id": componentId,
            "enabled": enabled,
            "timestamp": Date().timeIntervalSince1970
        ]
    )
}
```

---

### 🔴 **ПРИЧИНА 3: Обновление View вызывает повторное переключение**

**Проблема:**
- `updateClosure(newValue)` вызывается в `toggleComponent()` (строка 278)
- Это обновляет UI синхронно
- Если View обновляется, это может вызвать повторное переключение тумблера
- Особенно если используется `@Binding` или `@State`

**Код проблемы:**
```swift
// В NetworkProtectionViewModel.swift, строка 277
private func toggleComponent(...) async {
    updateClosure(newValue)  // ❌ Обновляет UI синхронно
    
    // Потом вызывается UserDefaults.standard.set()
    // Который может вызвать обновление View
    // Которое может вызвать повторное переключение
}
```

---

## ⚠️ КРИТИЧЕСКИЕ ВОПРОСЫ

### 1. Почему краш только на реальном устройстве?

**Вопрос:**
- В симуляторе все работает хорошо
- На реальном устройстве происходит краш
- Что изменилось?

**Возможные причины:**
- Реальное устройство имеет меньший размер стека
- Более строгая проверка рекурсии
- Быстрее вызывает обновление View
- Разные условия выполнения (память, процессор)

---

### 2. Откуда взялась рекурсия?

**Вопрос:**
- Мы исправили рекурсию в BUILD 100
- Но она вернулась в другом месте
- Что мы упустили?

**Возможные причины:**
- `UserDefaults.standard.set()` вызывает обновление View
- Обновление View вызывает повторное переключение тумблера
- Повторное переключение вызывает `UserDefaults.standard.set()`
- **РЕКУРСИЯ!**

---

### 3. Почему Dictionary.resize вызывает рекурсию?

**Вопрос:**
- Рекурсия происходит в `_DictionaryStorage.resize`
- Это системная функция
- Почему она вызывает рекурсию?

**Возможные причины:**
- Dictionary пытается изменить размер многократно
- Это происходит в background thread при рекурсии
- Системная функция не может обработать такую ситуацию
- Это вызывает переполнение стека

---

## 🔍 ЧТО НУЖНО ИСПРАВИТЬ

### 1. Исправить UserDefaults.standard.set() - использовать асинхронно

**Проблема:**
- `UserDefaults.standard.set()` вызывается синхронно в background thread
- Это может вызвать обновление View
- Которое может вызвать повторное переключение тумблера

**Решение:**
```swift
// БЫЛО:
UserDefaults.standard.set(newValue, forKey: userDefaultsKey)

// СТАЛО:
await MainActor.run {
    UserDefaults.standard.set(newValue, forKey: userDefaultsKey)
}
```

---

### 2. Добавить защиту от повторного переключения

**Проблема:**
- Нет защиты от повторного переключения тумблера
- Если View обновляется, это может вызвать повторное переключение

**Решение:**
```swift
// Добавить флаг для предотвращения повторного переключения
private var isToggling = false

private func toggleComponent(...) async {
    guard !isToggling else {
        return  // Пропускаем повторное переключение
    }
    
    isToggling = true
    defer { isToggling = false }
    
    // ... остальной код
}
```

---

### 3. Исправить trackComponentToggle - выполнять на main thread

**Проблема:**
- `trackComponentToggle()` создает Dictionary в background thread
- Это может вызвать проблемы при рекурсии

**Решение:**
```swift
// БЫЛО:
func trackComponentToggle(componentId: String, enabled: Bool) {
    analyticsManager.trackEvent(...)
}

// СТАЛО:
func trackComponentToggle(componentId: String, enabled: Bool) {
    Task { @MainActor in
        analyticsManager.trackEvent(...)
    }
}
```

---

## 📋 ПЛАН ДЕЙСТВИЙ

### Этап 1: Немедленно (15 минут)

**Задача:** Исправить UserDefaults.standard.set()

**Действия:**
1. Заменить синхронный `UserDefaults.standard.set()` на асинхронный `await MainActor.run`
2. Убедиться, что это не вызывает обновление View синхронно

---

### Этап 2: Исправить (20 минут)

**Задача:** Добавить защиту от повторного переключения

**Действия:**
1. Добавить флаг `isToggling` для предотвращения повторного переключения
2. Проверить, что это предотвращает рекурсию

---

### Этап 3: Исправить (10 минут)

**Задача:** Исправить trackComponentToggle

**Действия:**
1. Выполнять `trackComponentToggle()` на main thread
2. Убедиться, что это не вызывает проблем

---

## 🎯 ВЫВОДЫ

### Критические проблемы:

1. 🔴 **UserDefaults.standard.set() вызывает рекурсию** - синхронный вызов в background thread вызывает обновление View
2. 🔴 **Нет защиты от повторного переключения** - View обновление может вызвать повторное переключение тумблера
3. 🔴 **Dictionary.resize вызывает рекурсию** - работа с Dictionary в background thread при рекурсии

### Причина:

- `UserDefaults.standard.set()` вызывается синхронно в background thread
- Это вызывает обновление View
- Которое вызывает повторное переключение тумблера
- **РЕКУРСИЯ!**

---

**Статус:** 🔴 **КРИТИЧЕСКАЯ ПРОБЛЕМА - НАЙДЕНА ПРИЧИНА**  
**Рекомендация:** Немедленно исправить `UserDefaults.standard.set()` и добавить защиту от повторного переключения
