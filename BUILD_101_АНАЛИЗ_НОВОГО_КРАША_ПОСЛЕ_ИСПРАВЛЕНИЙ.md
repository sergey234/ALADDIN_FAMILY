# 🔍 BUILD 101: АНАЛИЗ НОВОГО КРАША ПОСЛЕ ИСПРАВЛЕНИЙ

**Дата краша:** 2026-03-10 23:47:23  
**Build:** 101  
**Статус:** 🔴 **КРАШ ПРОДОЛЖАЕТСЯ - НУЖНЫ ДОПОЛНИТЕЛЬНЫЕ ИСПРАВЛЕНИЯ**

---

## 📊 АНАЛИЗ КРАША

### Основная информация:

**Exception Type:** `EXC_BAD_ACCESS (SIGBUS)`  
**Exception Message:** `Thread stack size exceeded due to excessive recursion`  
**Thread:** Thread 2 - `Dispatch queue: com.apple.root.user-initiated-qos.cooperative` (BACKGROUND THREAD!)

**Ключевое отличие от предыдущего краша:**
- Предыдущий краш: Рекурсия в `_DictionaryStorage.resize` при переключении тумблеров
- Новый краш: **ТА ЖЕ РЕКУРСИЯ** - адрес `0x100f4a21c` повторяется много раз

---

## 🔍 АНАЛИЗ STACK TRACE

### Thread 2 (Crashed):

```
3   libswiftCore.dylib  _DictionaryStorage.allocate(scale:age:seed:) + 272
4   libswiftCore.dylib  _DictionaryStorage.resize(original:capacity:move:) + 40
5   ALADDIN            0x100e44a40  // Dictionary resize
6   ALADDIN            0x100e40b14  // Dictionary operation
7   ALADDIN            0x100e40478  // Dictionary operation
8   ALADDIN            0x100f49f20  // Рекурсия начинается здесь
9   ALADDIN            0x100f4a210  // Рекурсивный вызов
10  ALADDIN            0x100f4a21c  // РЕКУРСИЯ! (повторяется много раз)
11  ALADDIN            0x100f4a21c  // РЕКУРСИЯ!
12  ALADDIN            0x100f4a21c  // РЕКУРСИЯ!
13  ALADDIN            0x100f4a21c  // РЕКУРСИЯ!
14  ALADDIN            0x100f4a21c  // РЕКУРСИЯ!
15  ALADDIN            0x100f4a21c  // РЕКУРСИЯ!
```

**Вывод:**
- Рекурсия происходит в том же месте (`0x100f4a21c`)
- Это тот же адрес, что и в предыдущем краше
- Рекурсия связана с `Dictionary.resize` - это указывает на работу с Dictionary
- Рекурсия происходит в background thread при переключении тумблеров

---

## ⚠️ ПРОБЛЕМА: ИСПРАВЛЕНИЯ НЕ ПОМОГЛИ ПОЛНОСТЬЮ

### 🔴 **ПРОБЛЕМА 1: Task { @MainActor in } все еще создает Dictionary в background thread**

**Проблемный код:**
```swift
// В ComponentAnalytics.swift (ТЕКУЩИЙ КОД)
func trackComponentToggle(componentId: String, enabled: Bool) {
    Task { @MainActor in
        analyticsManager.trackEvent(
            "component_toggle",
            parameters: [  // ❌ Dictionary создается ДО перехода на main thread!
                "component_id": componentId,
                "enabled": enabled,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
    }
}
```

**Что происходит:**
1. `trackComponentToggle()` вызывается в background thread
2. `Task { @MainActor in }` создается, но Dictionary создается **ДО** перехода на main thread
3. Dictionary создается в background thread
4. При рекурсии Dictionary пытается изменить размер многократно
5. **РЕКУРСИЯ!**

**Почему это проблема:**
- `Task { @MainActor in }` не гарантирует, что код внутри выполнится сразу на main thread
- Dictionary создается в момент вызова функции (в background thread)
- Только код внутри `Task` выполняется на main thread, но Dictionary уже создан

---

### 🔴 **ПРОБЛЕМА 2: trackSettingToggle может вызывать рекурсию**

**Проблема:**
- `SmartToggleRow` вызывает `trackSettingToggle()` в `.onChange`
- Это может вызываться синхронно при обновлении View
- Если View обновляется из-за UserDefaults, это может вызвать повторное переключение

**Код проблемы:**
```swift
// В SmartToggleRow.swift
Toggle("", isOn: $isOn)
    .onChange(of: isOn) { newValue in
        componentAnalytics.trackSettingToggle(...)  // ❌ Может вызываться синхронно
        onValueChanged?(newValue)
    }
```

---

### 🔴 **ПРОБЛЕМА 3: Возможна рекурсия в других местах**

**Проблема:**
- Могут быть другие места, где вызывается `trackComponentToggle()` или `trackSettingToggle()`
- Они могут вызываться синхронно в background thread
- Это может вызвать рекурсию

---

## 🔍 ЧТО НУЖНО ИСПРАВИТЬ

### ✅ **ИСПРАВЛЕНИЕ 1: Создавать Dictionary на main thread**

**Проблема:**
- Dictionary создается в background thread до перехода на main thread

**Решение:**
```swift
// БЫЛО:
func trackComponentToggle(componentId: String, enabled: Bool) {
    Task { @MainActor in
        analyticsManager.trackEvent(
            "component_toggle",
            parameters: [  // ❌ Dictionary создается в background thread
                "component_id": componentId,
                "enabled": enabled,
                "timestamp": Date().timeIntervalSince1970
            ]
        )
    }
}

// СТАЛО:
func trackComponentToggle(componentId: String, enabled: Bool) {
    // ✅ Создаем параметры на main thread ДО создания Dictionary
    Task { @MainActor in
        let parameters: [String: Any] = [
            "component_id": componentId,
            "enabled": enabled,
            "timestamp": Date().timeIntervalSince1970
        ]
        analyticsManager.trackEvent("component_toggle", parameters: parameters)
    }
}
```

**Или лучше:**
```swift
// Еще лучше - использовать MainActor.run для гарантированного выполнения на main thread
func trackComponentToggle(componentId: String, enabled: Bool) {
    Task {
        await MainActor.run {
            let parameters: [String: Any] = [
                "component_id": componentId,
                "enabled": enabled,
                "timestamp": Date().timeIntervalSince1970
            ]
            analyticsManager.trackEvent("component_toggle", parameters: parameters)
        }
    }
}
```

---

### ✅ **ИСПРАВЛЕНИЕ 2: Исправить trackSettingToggle**

**Проблема:**
- `trackSettingToggle()` может вызываться синхронно в `.onChange`

**Решение:**
```swift
// В ComponentAnalytics.swift
func trackSettingToggle(componentId: String, settingKey: String, enabled: Bool) {
    Task {
        await MainActor.run {
            let parameters: [String: Any] = [
                "component_id": componentId,
                "setting_key": settingKey,
                "enabled": enabled,
                "timestamp": Date().timeIntervalSince1970
            ]
            analyticsManager.trackEvent("component_setting_toggle", parameters: parameters)
        }
    }
}
```

---

### ✅ **ИСПРАВЛЕНИЕ 3: Проверить все места вызова**

**Проблема:**
- Могут быть другие места, где вызывается аналитика синхронно

**Решение:**
- Найти все места вызова `trackComponentToggle()` и `trackSettingToggle()`
- Убедиться, что они не вызываются синхронно в background thread
- Добавить защиту от повторного вызова, если нужно

---

## 📋 РЕКОМЕНДАЦИИ

### Приоритет 1: Высокий

**1. Исправить создание Dictionary на main thread**

**Действия:**
- Изменить `trackComponentToggle()` - создавать Dictionary на main thread
- Изменить `trackSettingToggle()` - создавать Dictionary на main thread
- Использовать `await MainActor.run` для гарантированного выполнения на main thread

---

### Приоритет 2: Средний

**2. Проверить все места вызова аналитики**

**Действия:**
- Найти все места вызова `trackComponentToggle()` и `trackSettingToggle()`
- Убедиться, что они не вызываются синхронно в background thread
- Добавить защиту от повторного вызова, если нужно

---

### Приоритет 3: Низкий

**3. Добавить дополнительную защиту**

**Действия:**
- Добавить флаг для предотвращения повторного вызова аналитики
- Добавить логирование для диагностики рекурсии
- Добавить мониторинг производительности

---

## 🎯 ВЫВОДЫ

### Критические проблемы:

1. 🔴 **Task { @MainActor in } не гарантирует создание Dictionary на main thread** - Dictionary создается в background thread до перехода на main thread
2. 🔴 **trackSettingToggle может вызывать рекурсию** - вызывается синхронно в `.onChange`
3. 🔴 **Возможна рекурсия в других местах** - могут быть другие места вызова аналитики

### Причина краша:

- `Task { @MainActor in }` создает Task, но Dictionary создается **ДО** перехода на main thread
- Dictionary создается в background thread
- При рекурсии Dictionary пытается изменить размер многократно
- **РЕКУРСИЯ!**

### Решение:

- Использовать `await MainActor.run` для гарантированного выполнения на main thread
- Создавать Dictionary на main thread **ДО** передачи в `trackEvent()`
- Проверить все места вызова аналитики

---

**Статус:** 🔴 **КРАШ ПРОДОЛЖАЕТСЯ - НУЖНЫ ДОПОЛНИТЕЛЬНЫЕ ИСПРАВЛЕНИЯ**  
**Рекомендация:** Исправить создание Dictionary на main thread и проверить все места вызова аналитики
