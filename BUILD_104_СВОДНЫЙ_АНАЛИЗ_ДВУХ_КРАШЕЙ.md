# 🔍 BUILD 104: СВОДНЫЙ АНАЛИЗ ДВУХ КРАШЕЙ

**Дата:** 2026-03-11  
**Build:** 104  
**Статус:** 🔴 **КРИТИЧЕСКАЯ ПРОБЛЕМА - ДВА РАЗНЫХ КРАША!**

---

## 📊 СРАВНЕНИЕ ДВУХ КРАШЕЙ

### КРАШ 1: При переходе на страницу

**Дата:** 2026-03-11 12:12:08  
**Thread:** Thread 0 - `com.apple.main-thread` (**MAIN THREAD!**)  
**Адрес рекурсии:** `0x10314dfbc` (повторяется много раз)

**Stack trace:**
```
Thread 0 (Crashed - MAIN THREAD):
0   libswiftCore.dylib             swift::swift_slowAllocTyped(...)
1   libswiftCore.dylib             swift_allocObject
2   libswiftCore.dylib             static _DictionaryStorage.allocate(...)
3   libswiftCore.dylib             static _DictionaryStorage.resize(...)
4   ALADDIN                        0x103047f8c  // Dictionary создается здесь
5   ALADDIN                        0x103044060  // Dictionary operation
6   ALADDIN                        0x1030439c4  // Рекурсия начинается здесь
7   ALADDIN                        0x10314d864  // Рекурсивный вызов
8   ALADDIN                        0x10314dfac  // Рекурсивный вызов
9-14 ALADDIN                       0x10314dfbc  // РЕКУРСИЯ! (повторяется 6 раз)
15  ALADDIN                        0x10300ecb0  // SwiftUI View update
16  ALADDIN                        0x102d68f35  // SwiftUI body
17  ALADDIN                        0x1030432dd  // View recreation
18  ALADDIN                        0x102d68f35  // SwiftUI body
```

**Вывод:**
- Краш в **main thread** при переходе на страницу
- Рекурсия связана с SwiftUI View обновлением (строки 15-18)
- Dictionary создается в main thread и вызывает рекурсию

---

### КРАШ 2: При переключении тумблеров

**Дата:** 2026-03-11 12:19:46  
**Thread:** Thread 2 - `com.apple.root.user-initiated-qos.cooperative` (**BACKGROUND THREAD!**)  
**Адрес рекурсии:** `0x1008e5b60` (повторяется много раз)

**Stack trace:**
```
Thread 2 (Crashed - BACKGROUND THREAD):
0   libsystem_malloc.dylib         _xzm_xzone_malloc_from_freelist_chunk
1   libsystem_malloc.dylib         _xzm_xzone_malloc_freelist_outlined
2   libswiftCore.dylib             swift::swift_slowAllocTyped(...)
3   libswiftCore.dylib             swift_allocObject
4   libswiftCore.dylib             static _DictionaryStorage.allocate(...)
5   libswiftCore.dylib             static _DictionaryStorage.resize(...)
6   ALADDIN                        0x1007dff8c  // Dictionary создается здесь
7   ALADDIN                        0x1007dc060  // Dictionary operation
8   ALADDIN                        0x1007db9c4  // Рекурсия начинается здесь
9   ALADDIN                        0x1008e5864  // Рекурсивный вызов
10  ALADDIN                        0x1008e5b54  // Рекурсивный вызов
11-16 ALADDIN                      0x1008e5b60  // РЕКУРСИЯ! (повторяется 6 раз)
17  ALADDIN                        0x100716ebc  // Возможно: toggleComponent
18  ALADDIN                        0x1007e4aed  // Возможно: Task или async функция
19  ALADDIN                        0x100500f35  // Возможно: SwiftUI body
20  ALADDIN                        0x1007db2dd  // Возможно: View recreation
21  ALADDIN                        0x100500f35  // Возможно: SwiftUI body
```

**Вывод:**
- Краш в **background thread** при переключении тумблеров
- Рекурсия связана с `toggleComponent` (строка 17)
- Dictionary создается в background thread и вызывает рекурсию
- **Это та же проблема, что была в BUILD 101-103!**

---

## 🔍 КЛЮЧЕВЫЕ ОТЛИЧИЯ

| Параметр | Краш 1 (переход на страницу) | Краш 2 (переключение тумблеров) |
|----------|------------------------------|----------------------------------|
| **Thread** | Thread 0 (main thread) | Thread 2 (background thread) |
| **Когда происходит** | При первом переходе на страницу | При переключении тумблеров |
| **Адрес рекурсии** | `0x10314dfbc` | `0x1008e5b60` |
| **Связано с** | SwiftUI View обновление | `toggleComponent` |
| **Причина** | `Task {}` в `init()` | Dictionary в background thread |

---

## 🎯 ВЫВОД: У НАС ДВЕ РАЗНЫЕ ПРОБЛЕМЫ!

### Проблема 1: Краш при переходе на страницу (main thread)

**Причина:**
- `Task {}` в `NetworkProtectionViewModel.init()` вызывает пересоздание View
- SwiftUI обновляет View → `init()` вызывается снова → рекурсия

**Решение:**
- Убрать `Task {}` из `init()`
- Загружать статусы в `.onAppear` с защитой от повторного вызова

---

### Проблема 2: Краш при переключении тумблеров (background thread)

**Причина:**
- Dictionary создается в background thread при переключении тумблеров
- Это та же проблема, что была в BUILD 101-103
- Исправления BUILD 103-104 **НЕ ПОМОГЛИ** для тумблеров!

**Возможные причины:**
1. `Task { @MainActor in }` в `onToggle` не гарантирует создание Dictionary на main thread
2. Dictionary создается **ДО** перехода на main thread
3. `toggleComponent` в ViewModel может вызываться из background thread

**Решение:**
- Проверить, действительно ли `Task { @MainActor in }` гарантирует создание Dictionary на main thread
- Возможно, нужно использовать другой подход

---

## 🔍 ДЕТАЛЬНЫЙ АНАЛИЗ КРАША 2 (ПЕРЕКЛЮЧЕНИЕ ТУМБЛЕРОВ)

### Почему исправления BUILD 103-104 не помогли?

**Что мы исправили в BUILD 103-104:**
```swift
// ❌ Было:
onToggle: { newValue in Task { await viewModel.toggleCrashDetection(newValue) } }

// ✅ Стало:
onToggle: { newValue in Task { @MainActor in await viewModel.toggleCrashDetection(newValue) } }
```

**Проблема:**
- `Task { @MainActor in }` гарантирует, что **блок кода** выполняется на main thread
- НО: Dictionary может создаваться **ДО** входа в блок `@MainActor`
- Если `onToggle` вызывается из background thread, Dictionary literal может создаваться в background thread

**Пример:**
```swift
onToggle: { newValue in
    // ❌ Этот Dictionary может создаваться в background thread!
    let someDict = ["key": "value"]
    
    Task { @MainActor in
        // ✅ Этот код выполняется на main thread
        await viewModel.toggleCrashDetection(newValue)
    }
}
```

---

### Возможные причины краша при переключении тумблеров:

#### 1. Dictionary создается в `toggleComponent` до перехода на main thread

**Файл:** `ViewModels/NetworkProtectionViewModel.swift`

**Проблема:**
- `toggleComponent` может создавать Dictionary для аналитики
- Если метод вызывается из background thread, Dictionary создается в background thread

**Нужно проверить:**
- Где именно создается Dictionary в `toggleComponent`
- Создается ли он до или после перехода на main thread

---

#### 2. `ComponentAnalytics.trackComponentToggle()` создает Dictionary в background thread

**Файл:** `Core/Analytics/ComponentAnalytics.swift`

**Проблема:**
- Хотя класс имеет `@MainActor`, вызов из `async` функции может выполняться в background thread
- Dictionary literal создается **ДО** вызова метода

**Нужно проверить:**
- Вызывается ли `trackComponentToggle()` из `toggleComponent`
- Создается ли Dictionary на main thread

---

#### 3. `Task { @MainActor in }` не гарантирует создание Dictionary на main thread

**Проблема:**
- `Task { @MainActor in }` гарантирует выполнение блока на main thread
- НО: Dictionary literal может создаваться синхронно при вызове функции
- Если функция вызывается из background thread, Dictionary создается в background thread

**Пример:**
```swift
// В NetworkProtectionScreen:
onToggle: { newValue in
    // ❌ Этот вызов может быть в background thread
    Task { @MainActor in
        // ✅ Этот блок выполняется на main thread
        // НО: Dictionary уже может быть создан в background thread!
        await viewModel.toggleCrashDetection(newValue)
    }
}
```

---

## ✅ РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ

### Приоритет 1: Критический (исправить немедленно)

#### 1. Исправить краш при переходе на страницу

**Проблема:** `Task {}` в `init()` вызывает рекурсию

**Решение:**
- Убрать `Task {}` из `NetworkProtectionViewModel.init()`
- Загружать статусы в `.onAppear` с защитой от повторного вызова
- Убрать `Task { @MainActor in }` из `updateStatusForComponent()`
- Убрать `await MainActor.run {}` из методов загрузки

---

#### 2. Исправить краш при переключении тумблеров

**Проблема:** Dictionary создается в background thread

**Решение 1: Использовать `DispatchQueue.main.async` для гарантии main thread**

```swift
onToggle: { newValue in
    // ✅ Всегда выполняем на main thread используя DispatchQueue.main.async
    DispatchQueue.main.async {
        Task {
            await viewModel.toggleCrashDetection(newValue)
        }
    }
}
```

**Решение 2: Создавать Dictionary внутри `Task { @MainActor in }`**

```swift
onToggle: { newValue in
    Task { @MainActor in
        // ✅ Dictionary создается на main thread
        let parameters: [String: Any] = [
            "component_id": "crash_detection_agent",
            "enabled": newValue
        ]
        // Теперь вызываем метод
        await viewModel.toggleCrashDetection(newValue)
    }
}
```

**Решение 3: Использовать `Task { @MainActor in }` для всего блока, включая создание Dictionary**

```swift
onToggle: { newValue in
    Task { @MainActor in
        // ✅ Весь блок выполняется на main thread
        // Dictionary создается на main thread автоматически
        await viewModel.toggleCrashDetection(newValue)
    }
}
```

**НО:** Если `viewModel.toggleCrashDetection()` создает Dictionary внутри, это может быть проблемой!

---

#### 3. Проверить `toggleComponent` в ViewModel

**Нужно проверить:**
- Создается ли Dictionary в `toggleComponent`
- Создается ли он на main thread
- Используется ли `Task { @MainActor in }` правильно

---

## 📋 ПЛАН ДЕЙСТВИЙ

### Этап 1: Исправить краш при переходе на страницу (15 минут)

1. ✅ Убрать `Task {}` из `NetworkProtectionViewModel.init()`
2. ✅ Убрать `Task { @MainActor in }` из `updateStatusForComponent()`
3. ✅ Убрать `await MainActor.run {}` из методов загрузки
4. ✅ Добавить флаг `hasLoadedStatuses`
5. ✅ Переместить загрузку статусов в `.onAppear`

### Этап 2: Исправить краш при переключении тумблеров (20 минут)

6. ✅ Проверить, где создается Dictionary в `toggleComponent`
7. ✅ Убедиться, что Dictionary создается на main thread
8. ✅ Использовать `DispatchQueue.main.async` или другой подход
9. ✅ Добавить защиту от повторного переключения (уже есть `isToggling`)

### Этап 3: Тестирование (30 минут)

10. ✅ Протестировать переход на страницу
11. ✅ Протестировать переключение тумблеров
12. ✅ Проверить отсутствие крашей

---

## 🎯 ИТОГОВЫЙ ВЫВОД

**У нас ДВЕ разные проблемы:**

1. **Краш при переходе на страницу** (main thread) - из-за `Task {}` в `init()`
2. **Краш при переключении тумблеров** (background thread) - Dictionary создается в background thread

**Решение:**
- Исправить обе проблемы
- Использовать правильный подход для каждой проблемы
- Тестировать оба сценария

---

**Статус:** 🔴 **КРИТИЧЕСКАЯ ПРОБЛЕМА - ДВЕ РАЗНЫЕ ПРИЧИНЫ КРАША**  
**Рекомендация:** Исправить обе проблемы немедленно
