# 🔍 BUILD 102: АНАЛИЗ ПРОДОЛЖАЮЩЕГОСЯ КРАША

**Дата краша:** 2026-03-11 00:35:17  
**Build:** 102  
**Статус:** 🔴 **КРАШ ПРОДОЛЖАЕТСЯ - НУЖЕН ГЛУБОКИЙ АНАЛИЗ**

---

## 📋 ИСТОРИЯ ИСПРАВЛЕНИЙ (BUILD 100 → BUILD 102)

### BUILD 100: Исправление рекурсии в DateFormatter

**Проблема:**
- Рекурсия в `DateFormatter.string()` в ICU библиотеке
- `Calendar.current` вызывал рекурсию через `UserDefaults`
- Рекурсия происходила в main thread

**Исправления:**
1. ✅ Добавлен статический `Calendar` в `displayFormatter`
2. ✅ Форматирование дат выполняется на main thread (`await MainActor.run`)
3. ✅ Создан `DateFormatterService` для централизованного управления форматтерами
4. ✅ Добавлены unit и integration тесты

**Результат:** ✅ Краш прекратился в BUILD 100

**НО:** В BUILD 100 был найден новый краш - старый код все еще использовался в `updateExpirationTextCache` (исправлено)

---

### BUILD 101: Новый краш при переключении тумблеров

**Проблема:**
- Рекурсия в `Dictionary.resize` в background thread
- Происходила при переключении тумблеров на реальном устройстве
- В симуляторе работало нормально

**Исправления:**
1. ✅ `UserDefaults.standard.set()` обернут в `await MainActor.run` (**только в demo mode**)
2. ✅ Добавлен флаг `isToggling` и `togglingLock` для защиты от повторного переключения
3. ✅ `trackComponentToggle()` обернут в `Task { @MainActor in }` (BUILD 101)
4. ✅ Все методы аналитики обернуты в `Task { await MainActor.run }` (BUILD 102)

**Результат:** ❌ Краш продолжился в BUILD 102

**Проблема:** В BUILD 101 исправили **только demo mode**, но **НЕ исправили production mode**!

---

### BUILD 102: Краш продолжается

**Проблема:**
- Та же рекурсия в `Dictionary.resize` в background thread
- Адрес `0x104e414d4` повторяется много раз (тот же адрес, что и в BUILD 101)

**Что было сделано:**
- ✅ Все методы аналитики обернуты в `Task { await MainActor.run }`
- ❌ НО краш продолжился из-за `parameters ?? [:]` в `trackEvent()`

**Результат:** ❌ Краш продолжается

---

## 📊 АНАЛИЗ КРАША

### Основная информация:

**Exception Type:** `EXC_BAD_ACCESS (SIGBUS)`  
**Exception Message:** `Thread stack size exceeded due to excessive recursion`  
**Thread:** Thread 6 - `Dispatch queue: com.apple.root.user-initiated-qos.cooperative` (BACKGROUND THREAD!)

**Ключевое отличие от предыдущих крашей:**
- BUILD 101: Рекурсия в `Dictionary.resize` при переключении тумблеров
- BUILD 102: **ТА ЖЕ РЕКУРСИЯ** - адрес `0x104e414d4` повторяется много раз

---

## 🔍 АНАЛИЗ STACK TRACE

### Thread 6 (Crashed):

```
3   libswiftCore.dylib  _DictionaryStorage.allocate(scale:age:seed:) + 272
4   libswiftCore.dylib  _DictionaryStorage.resize(original:capacity:move:) + 40
5   ALADDIN            0x104d3b8e8  // Dictionary resize
6   ALADDIN            0x104d379bc  // Dictionary operation
7   ALADDIN            0x104d37320  // Dictionary operation
8   ALADDIN            0x104e411d8  // Рекурсия начинается здесь
9   ALADDIN            0x104e414c8  // Рекурсивный вызов
10  ALADDIN            0x104e414d4  // РЕКУРСИЯ! (повторяется много раз)
11  ALADDIN            0x104e414d4  // РЕКУРСИЯ!
12  ALADDIN            0x104e414d4  // РЕКУРСИЯ!
13  ALADDIN            0x104e414d4  // РЕКУРСИЯ!
14  ALADDIN            0x104e414d4  // РЕКУРСИЯ!
15  ALADDIN            0x104e414d4  // РЕКУРСИЯ!
```

**Вывод:**
- Рекурсия происходит в том же месте (`0x104e414d4`)
- Это тот же адрес, что и в предыдущем краше (смещение изменилось из-за новой сборки)
- Рекурсия связана с `Dictionary.resize` - это указывает на работу с Dictionary
- Рекурсия происходит в background thread при переключении тумблеров

---

## ⚠️ ПРОБЛЕМА: ИСПРАВЛЕНИЯ НЕ ПОМОГЛИ

### 🔴 **ПРОБЛЕМА 1: Task { await MainActor.run } все еще может создавать Dictionary в background thread**

**Текущий код (ПОСЛЕ ИСПРАВЛЕНИЙ):**
```swift
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

**Что может происходить:**
1. `trackComponentToggle()` вызывается в background thread
2. `Task {}` создается, но это не гарантирует немедленное выполнение
3. Dictionary literal `[ ... ]` может создаваться **ДО** перехода на main thread
4. При рекурсии Dictionary пытается изменить размер многократно в background thread
5. **РЕКУРСИЯ!**

**Почему это может быть проблемой:**
- `Task {}` создает асинхронную задачу, но не гарантирует немедленное выполнение
- Dictionary literal может создаваться синхронно при вызове функции
- `await MainActor.run` выполняется асинхронно, но Dictionary уже может быть создан

---

### 🔴 **ПРОБЛЕМА 2: Dictionary создается в trackEvent() и logger.business()**

**Проблема:**
- `analyticsManager.trackEvent()` вызывает `logger.business()` с интерполяцией строки
- `parameters?.description` может создавать Dictionary для форматирования строки
- `print("📊 Event: \(eventName), params: \(parameters ?? [:])")` создает Dictionary literal `[:]` если parameters == nil
- Если это происходит в background thread, может быть проблема

**Код:**
```swift
// В AnalyticsManager.swift
func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
    logger.business("Analytics: Event - \(eventName) with params: \(parameters?.description ?? "none")")
    #if DEBUG
    print("📊 Event: \(eventName), params: \(parameters ?? [:])")  // ⚠️ Dictionary literal создается здесь!
    #endif
}
```

**Что может происходить:**
1. `trackEvent()` вызывается с Dictionary параметрами на main thread (из `await MainActor.run`)
2. НО `logger.business()` может выполняться в background thread
3. `parameters?.description` может создавать Dictionary для форматирования строки
4. `parameters ?? [:]` создает Dictionary literal `[:]` если parameters == nil
5. Если это происходит в background thread, может быть проблема
6. **РЕКУРСИЯ!**

---

### 🔴 **ПРОБЛЕМА 3: Возможна рекурсия в logger.business()**

**Проблема:**
- `logger.business()` может создавать Dictionary для логирования
- Если это происходит в background thread, может быть проблема
- Логирование может вызывать другие операции с Dictionary

---

### 🔴 **ПРОБЛЕМА 4: Несоответствие вызовов аналитики**

**Проблема:**
- В `NetworkProtectionViewModel.handleDemoModeToggle()` (строка 329) вызов обернут в `await MainActor.run`
- В `NetworkProtectionViewModel.handleProductionModeToggle()` (строка 354) вызов БЕЗ `await MainActor.run`
- Это несоответствие может вызывать проблемы

**Код:**
```swift
// Строка 329 - С await MainActor.run
await MainActor.run {
    componentAnalytics.trackComponentToggle(
        componentId: componentId,
        enabled: newValue
    )
}

// Строка 354 - БЕЗ await MainActor.run
componentAnalytics.trackComponentToggle(
    componentId: componentId,
    enabled: newValue
)
```

**Что может происходить:**
1. В production mode вызов происходит БЕЗ `await MainActor.run`
2. `trackComponentToggle()` создает `Task {}`, но это не гарантирует немедленное выполнение
3. Dictionary может создаваться в background thread
4. **РЕКУРСИЯ!**

---

## 🔍 ЧТО НУЖНО ПРОВЕРИТЬ

### 1. Проверить, действительно ли Dictionary создается на main thread

**Проверка:**
- Добавить логирование для проверки текущего потока
- Убедиться, что Dictionary создается на main thread
- Проверить, не создается ли Dictionary в background thread

---

### 2. Проверить trackEvent() и logger.business()

**Проверка:**
- Проверить, не создает ли `trackEvent()` Dictionary
- Проверить, не создает ли `logger.business()` Dictionary
- Убедиться, что все операции выполняются на main thread

---

### 3. Проверить все места вызова аналитики

**Проверка:**
- Найти все места вызова `trackComponentToggle()` и `trackSettingToggle()`
- Убедиться, что они не вызываются синхронно в критических местах
- Проверить, не вызываются ли они из background thread

---

### 4. Проверить рекурсию в других местах

**Проверка:**
- Проверить `NetworkProtectionViewModel.handleDemoModeToggle()`
- Проверить другие места, где может быть рекурсия
- Убедиться, что нет других источников рекурсии

---

## 📋 РЕКОМЕНДАЦИИ

### Приоритет 1: Критический

**1. Исправить trackEvent() - убрать создание Dictionary в background thread**

**Проблема:**
- `parameters ?? [:]` создает Dictionary literal в background thread
- `parameters?.description` может создавать Dictionary для форматирования строки

**Решение:**
```swift
// БЫЛО:
func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
    logger.business("Analytics: Event - \(eventName) with params: \(parameters?.description ?? "none")")
    #if DEBUG
    print("📊 Event: \(eventName), params: \(parameters ?? [:])")  // ⚠️ Dictionary создается здесь!
    #endif
}

// СТАЛО:
func trackEvent(_ eventName: String, parameters: [String: Any]? = nil) {
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
```

---

**2. Исправить trackComponentToggle() - использовать DispatchQueue.main.async**

**Проблема:**
- `Task { await MainActor.run }` может не гарантировать создание Dictionary на main thread
- Dictionary literal может создаваться синхронно при вызове функции

**Решение:**
```swift
// БЫЛО:
func trackComponentToggle(componentId: String, enabled: Bool) {
    Task {
        await MainActor.run {
            let parameters: [String: Any] = [...]
            analyticsManager.trackEvent(...)
        }
    }
}

// СТАЛО:
func trackComponentToggle(componentId: String, enabled: Bool) {
    // ✅ Всегда выполняем на main thread используя DispatchQueue.main.async
    DispatchQueue.main.async {
        let parameters: [String: Any] = [
            "component_id": componentId,
            "enabled": enabled,
            "timestamp": Date().timeIntervalSince1970
        ]
        analyticsManager.trackEvent("component_toggle", parameters: parameters)
    }
}
```

---

**3. Исправить NetworkProtectionViewModel - добавить await MainActor.run для production mode**

**Проблема:**
- В production mode вызов происходит БЕЗ `await MainActor.run`
- Это несоответствие может вызывать проблемы

**Решение:**
```swift
// БЫЛО (строка 354):
componentAnalytics.trackComponentToggle(
    componentId: componentId,
    enabled: newValue
)

// СТАЛО:
await MainActor.run {
    componentAnalytics.trackComponentToggle(
        componentId: componentId,
        enabled: newValue
    )
}
```

---

### Приоритет 2: Высокий

**2. Проверить trackEvent() и logger.business()**

**Проблема:**
- `trackEvent()` и `logger.business()` могут создавать Dictionary

**Решение:**
- Проверить, не создают ли они Dictionary
- Убедиться, что все операции выполняются на main thread
- Добавить защиту от рекурсии, если нужно

---

### Приоритет 3: Средний

**3. Добавить защиту от рекурсии**

**Проблема:**
- Нет защиты от повторного вызова аналитики

**Решение:**
- Добавить флаг для предотвращения повторного вызова
- Использовать `NSLock` для thread-safety
- Пропускать повторные вызовы, если аналитика уже выполняется

---

## 🎯 ВЫВОДЫ

### Критические проблемы:

1. 🔴 **`parameters ?? [:]` создает Dictionary literal в background thread** - в `trackEvent()` строка 50 создает Dictionary если parameters == nil
2. 🔴 **`parameters?.description` может создавать Dictionary для форматирования строки** - в `trackEvent()` строка 48 может создавать Dictionary
3. 🔴 **Task { await MainActor.run } может не гарантировать создание Dictionary на main thread** - Dictionary literal может создаваться синхронно при вызове функции
4. 🔴 **Несоответствие вызовов аналитики** - в production mode вызов происходит БЕЗ `await MainActor.run`, в demo mode - С `await MainActor.run`

### Причина краша:

- Dictionary создается в background thread в нескольких местах:
  1. `parameters ?? [:]` в `trackEvent()` создает Dictionary literal если parameters == nil
  2. `parameters?.description` может создавать Dictionary для форматирования строки
  3. Dictionary literal в `trackComponentToggle()` может создаваться синхронно при вызове функции
  4. В production mode вызов происходит БЕЗ `await MainActor.run`, что может вызывать проблемы
- При рекурсии Dictionary пытается изменить размер многократно в background thread
- **РЕКУРСИЯ!**

### Решение:

1. **Исправить trackEvent()** - убрать `parameters ?? [:]` и использовать условную проверку
2. **Исправить trackComponentToggle()** - использовать `DispatchQueue.main.async` вместо `Task { await MainActor.run }`
3. **Исправить NetworkProtectionViewModel** - добавить `await MainActor.run` для production mode
4. **Проверить logger.business()** - убедиться, что он не создает Dictionary в background thread

---

**Статус:** 🔴 **КРАШ ПРОДОЛЖАЕТСЯ - НУЖНЫ ДОПОЛНИТЕЛЬНЫЕ ИСПРАВЛЕНИЯ**  
**Рекомендация:** Использовать `DispatchQueue.main.async` вместо `Task { await MainActor.run }` и проверить все места создания Dictionary
