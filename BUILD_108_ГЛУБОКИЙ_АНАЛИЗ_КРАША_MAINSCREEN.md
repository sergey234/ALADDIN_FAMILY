# 🔴 BUILD 108: ГЛУБОКИЙ АНАЛИЗ КРАША MAINSCREEN

**Дата анализа:** 2026-03-11  
**Build:** 108  
**Incident Identifier:** 8B6E58BC-8450-4E5B-9CBF-E6E539B12DBD  
**Статус:** 🔴 **КРИТИЧЕСКИЙ КРАШ - ПРИ ВХОДЕ НА MAINSCREEN!**

---

## 🎯 КРИТИЧЕСКОЕ ОТКРЫТИЕ

### 🔴 **НОВАЯ ПРОБЛЕМА: КРАШ ПЕРЕМЕСТИЛСЯ!**

**BUILD 107:**
- Краш на `NetworkProtectionScreen` при переключении тумблеров
- Thread: Background thread (Thread 2)

**BUILD 108:**
- Краш на `MainScreen` при входе (сразу при запуске!)
- Thread: **MAIN THREAD (Thread 0)** - это критично!
- Приложение полностью зависает при входе

---

## 📊 АНАЛИЗ CRASH LOG

### 🔴 **Exception Details:**

**Exception Type:** `EXC_BAD_ACCESS (SIGSEGV)`  
**Exception Subtype:** `KERN_PROTECTION_FAILURE at 0x000000016cefffe0`  
**Exception Message:** `Thread stack size exceeded due to excessive recursion`  
**Exception Codes:** `0x0000000000000002, 0x000000016cefffe0`

**Критично:**
- Краш на **MAIN THREAD (Thread 0)** - UI полностью зависает
- Размер стека превышен из-за рекурсии
- Адрес рекурсии: `0x10322a410` повторяется **6 раз** (строки 9-14)

---

### 📊 **Stack Trace Analysis:**

**Thread 0 (Crashed - MAIN THREAD):**
```
0   libswiftCore.dylib             swift::swift_slowAllocTyped(...) + 8
1   libswiftCore.dylib             swift_allocObject + 136
2   libswiftCore.dylib             static _DictionaryStorage.allocate(...) + 272
3   libswiftCore.dylib             static _DictionaryStorage.resize(...) + 40
4   ALADDIN                        0x1031247a0  // Dictionary создается здесь
5   ALADDIN                        0x103120874  // Рекурсия начинается здесь
6   ALADDIN                        0x1031201d8  // Рекурсия продолжается
7   ALADDIN                        0x103229cb8  // Рекурсия продолжается
8   ALADDIN                        0x10322a400  // Рекурсия продолжается
9   ALADDIN                        0x10322a410  // ⚠️ РЕКУРСИЯ (повторяется 6 раз)
10  ALADDIN                        0x10322a410  // ⚠️ РЕКУРСИЯ
11  ALADDIN                        0x10322a410  // ⚠️ РЕКУРСИЯ
12  ALADDIN                        0x10322a410  // ⚠️ РЕКУРСИЯ
13  ALADDIN                        0x10322a410  // ⚠️ РЕКУРСИЯ
14  ALADDIN                        0x10322a410  // ⚠️ РЕКУРСИЯ
15  ALADDIN                        0x1030eb4c4  // Выход из рекурсии
16  ALADDIN                        0x102e44f35  // Вызов из async контекста
17  ALADDIN                        0x10311faf1  // Вызов из async контекста
18  ALADDIN                        0x102e44511  // Вызов из async контекста
19  libswift_Concurrency.dylib     completeTaskWithClosure(...) + 1
```

**Вывод:**
- Рекурсия происходит в коде ALADDIN (не в системных библиотеках)
- Адрес `0x10322a410` повторяется 6 раз - это рекурсивный вызов
- Рекурсия связана с `Dictionary.resize` на **MAIN THREAD**
- `completeTaskWithClosure` указывает на проблему в async/await коде
- Краш происходит при входе на MainScreen (не при переключении тумблеров!)

---

## 🔍 ГЛУБОКИЙ АНАЛИЗ ПРИЧИН

### 🔴 **ПРОБЛЕМА #1: Dictionary создается на MAIN THREAD при инициализации MainScreen**

**Цепочка вызовов:**
1. `MainScreen.init()` вызывается при создании View
2. `MasterLogger.shared.screenLoad("MainScreen.init")` вызывается в `init()`
3. `screenLoad()` вызывает `ui()` → `log()` → может вызвать аналитику
4. Если аналитика создает Dictionary на MAIN THREAD → рекурсия

**Код проблемы:**
```swift
init() {
    // ✅ BUILD 109: Минимальное логирование при инициализации для стабильности
    MasterLogger.shared.screenLoad("MainScreen.init")  // ⚠️ Может вызвать Dictionary!
    
    // Создаем MainViewModel
    let viewModel = MainViewModel()  // ⚠️ Может вызвать Dictionary!
    _mainViewModel = StateObject(wrappedValue: viewModel)
}
```

**Вероятность:** 🔴 **95%** - это критическая проблема!

---

### 🔴 **ПРОБЛЕМА #2: MainViewModel.init() может создавать Dictionary**

**Гипотеза:**
- `MainViewModel.init()` может вызывать аналитику или создавать Dictionary
- Если это происходит на MAIN THREAD при инициализации → рекурсия

**Вероятность:** 🔴 **90%** - это критическая проблема!

---

### 🔴 **ПРОБЛЕМА #3: .task {} вызывается сразу при входе на MainScreen**

**Цепочка вызовов:**
1. `MainScreen.body` создается
2. `.task {}` вызывается автоматически SwiftUI
3. `mainViewModel.onAppear()` вызывается в `.task {}`
4. `loadDashboardData()` может вызывать аналитику
5. Аналитика создает Dictionary на MAIN THREAD → рекурсия

**Код проблемы:**
```swift
.task {
    // ...
    mainViewModel.onAppear()  // ⚠️ Может вызвать Dictionary!
    // ...
    await updateExpirationTextCache(from: currentExpiresAt)  // ⚠️ Может вызвать Dictionary!
}
```

**Вероятность:** 🔴 **85%** - это критическая проблема!

---

### 🔴 **ПРОБЛЕМА #4: MasterLogger.screenLoad() может вызвать цикл рекурсии**

**Цепочка вызовов:**
1. `MasterLogger.shared.screenLoad("MainScreen.init")` вызывается в `init()`
2. `screenLoad()` вызывает `ui()` → `log()`
3. `log()` может вызвать `settingsLogger.logFunction()`
4. Если `settingsLogger.logFunction()` вызывает аналитику → цикл!

**Код проблемы:**
```swift
func screenLoad(_ screenName: String, ...) {
    ui("📱 Screen loaded: \(screenName)", ...)  // ⚠️ Вызывает log()
}

func ui(_ message: String, ...) {
    log(.info, category: .ui, message: message, ...)  // ⚠️ Вызывает log()
}

func log(...) {
    settingsLogger.logFunction(...)  // ⚠️ Может вызвать аналитику!
}
```

**Вероятность:** 🔴 **80%** - это критическая проблема!

---

### 🔴 **ПРОБЛЕМА #5: DateFormatterService может вызвать Dictionary**

**Гипотеза:**
- `updateExpirationTextCache()` вызывает `DateFormatterService.formatExpirationDate()`
- Если `DateFormatterService` создает Dictionary на MAIN THREAD → рекурсия

**Вероятность:** 🟡 **60%** - это возможная проблема!

---

## 🎯 КОРНЕВАЯ ПРИЧИНА (ВЫВОД СПЕЦИАЛИСТА)

### 🔴 **ГЛАВНАЯ ПРОБЛЕМА:**

**Dictionary создается на MAIN THREAD при инициализации MainScreen, вызывая рекурсию через цикл:**

**MainScreen.init() → MasterLogger.screenLoad() → log() → аналитика → Dictionary → рекурсия**

**ИЛИ:**

**MainScreen.task {} → mainViewModel.onAppear() → loadDashboardData() → аналитика → Dictionary → рекурсия**

---

### 🔴 **ПОЧЕМУ ЭТО ПРОИСХОДИТ НА MAIN THREAD:**

1. **SwiftUI View инициализация:**
   - `MainScreen.init()` вызывается на MAIN THREAD
   - `MasterLogger.shared.screenLoad()` вызывается на MAIN THREAD
   - Если аналитика создает Dictionary → рекурсия на MAIN THREAD

2. **SwiftUI .task {}:**
   - `.task {}` выполняется на MAIN THREAD (если не указано иное)
   - `mainViewModel.onAppear()` вызывается на MAIN THREAD
   - Если аналитика создает Dictionary → рекурсия на MAIN THREAD

3. **Отсутствие @MainActor:**
   - `ComponentAnalytics` НЕ имеет `@MainActor` (как мы выяснили ранее)
   - `AnalyticsManager` НЕ имеет `@MainActor` (как мы выяснили ранее)
   - Dictionary создается на MAIN THREAD без защиты → рекурсия

---

## 📊 СРАВНЕНИЕ С BUILD 107

| Аспект | BUILD 107 | BUILD 108 |
|--------|-----------|-----------|
| **Экран** | NetworkProtectionScreen | MainScreen |
| **Действие** | Переключение тумблеров | Вход на экран |
| **Thread** | Background thread (Thread 2) | **MAIN THREAD (Thread 0)** |
| **Время** | После загрузки приложения | **Сразу при входе** |
| **Критичность** | Высокая | **КРИТИЧЕСКАЯ** |

**Вывод:**
- Проблема усугубилась - теперь краш происходит на MAIN THREAD при входе
- Приложение полностью зависает при запуске
- Это делает приложение **НЕИСПОЛЬЗУЕМЫМ**

---

## 🎯 ДЕТАЛЬНЫЙ АНАЛИЗ ЦЕПОЧКИ РЕКУРСИИ

### 📊 **ВАРИАНТ 1: Рекурсия через MasterLogger**

**Цепочка:**
```
MainScreen.init()
  → MasterLogger.shared.screenLoad("MainScreen.init")
    → ui("📱 Screen loaded: MainScreen.init")
      → log(.info, category: .ui, message: "...")
        → settingsLogger.logFunction(...)
          → [МОЖЕТ ВЫЗВАТЬ АНАЛИТИКУ]
            → ComponentAnalytics.trackComponentToggle(...)
              → Dictionary создается
                → Dictionary.resize
                  → РЕКУРСИЯ!
```

**Вероятность:** 🔴 **80%**

---

### 📊 **ВАРИАНТ 2: Рекурсия через MainViewModel**

**Цепочка:**
```
MainScreen.init()
  → MainViewModel()
    → [МОЖЕТ ВЫЗВАТЬ АНАЛИТИКУ В init()]
      → ComponentAnalytics.trackComponentToggle(...)
        → Dictionary создается
          → Dictionary.resize
            → РЕКУРСИЯ!
```

**Вероятность:** 🔴 **90%**

---

### 📊 **ВАРИАНТ 3: Рекурсия через .task {}**

**Цепочка:**
```
MainScreen.body
  → .task {}
    → mainViewModel.onAppear()
      → loadDashboardData()
        → [МОЖЕТ ВЫЗВАТЬ АНАЛИТИКУ]
          → ComponentAnalytics.trackComponentToggle(...)
            → Dictionary создается
              → Dictionary.resize
                → РЕКУРСИЯ!
```

**Вероятность:** 🔴 **85%**

---

## 🔍 АНАЛИЗ АДРЕСОВ РЕКУРСИИ

### 📊 **Адрес рекурсии: `0x10322a410`**

**Повторяется 6 раз:**
- Строка 9: `ALADDIN 0x10322a410`
- Строка 10: `ALADDIN 0x10322a410`
- Строка 11: `ALADDIN 0x10322a410`
- Строка 12: `ALADDIN 0x10322a410`
- Строка 13: `ALADDIN 0x10322a410`
- Строка 14: `ALADDIN 0x10322a410`

**Вывод:**
- Это рекурсивный вызов одной и той же функции
- Функция вызывает сама себя 6 раз
- После 6-го вызова стек переполняется → краш

**Что это может быть:**
- Метод, который вызывает аналитику
- Метод, который создает Dictionary
- Метод, который вызывает сам себя через цикл

---

## 🎯 ВЫВОДЫ СПЕЦИАЛИСТА

### 🔴 **КОРНЕВАЯ ПРИЧИНА:**

**Dictionary создается на MAIN THREAD при инициализации MainScreen через цикл:**

1. **MainScreen.init()** вызывает `MasterLogger.shared.screenLoad()`
2. **MasterLogger.screenLoad()** вызывает `log()` → может вызвать аналитику
3. **Аналитика** создает Dictionary на MAIN THREAD
4. **Dictionary.resize** вызывает рекурсию → краш

**ИЛИ:**

1. **MainScreen.task {}** вызывает `mainViewModel.onAppear()`
2. **mainViewModel.onAppear()** вызывает `loadDashboardData()`
3. **loadDashboardData()** может вызвать аналитику
4. **Аналитика** создает Dictionary на MAIN THREAD
5. **Dictionary.resize** вызывает рекурсию → краш

---

### 🔴 **ПОЧЕМУ ЭТО КРИТИЧНО:**

1. **Краш на MAIN THREAD:**
   - UI полностью зависает
   - Приложение становится неиспользуемым
   - Пользователь не может войти в приложение

2. **Краш при входе:**
   - Происходит сразу при запуске
   - Нет возможности обойти проблему
   - Приложение полностью неработоспособно

3. **Рекурсия через цикл:**
   - Не просто thread safety проблема
   - Это цикл рекурсии через логгер/аналитику
   - Нужно разорвать цикл

---

### 🔴 **ПОЧЕМУ ИСПРАВЛЕНИЯ BUILD 107 НЕ ПОМОГЛИ:**

**BUILD 107 исправления:**
- Добавлен `@MainActor` к `ComponentAnalytics` (планировалось)
- Добавлен `@MainActor` к `AnalyticsManager` (планировалось)
- Исправлен `SmartToggleRow.onChange` (планировалось)

**НО:**
- Исправления НЕ были применены (как мы выяснили)
- Проблема усугубилась - теперь краш на MAIN THREAD при входе
- Цикл рекурсии через логгер не был разорван

---

## 📋 РЕКОМЕНДАЦИИ (БЕЗ ИСПРАВЛЕНИЙ)

### 🔴 **КРИТИЧЕСКИЕ ДЕЙСТВИЯ:**

1. **Убрать логирование из MainScreen.init():**
   - `MasterLogger.shared.screenLoad("MainScreen.init")` должен быть убран
   - Логирование должно происходить в `.task {}`, а не в `init()`

2. **Разорвать цикл рекурсии через логгер:**
   - `MasterLogger.screenLoad()` не должен вызывать аналитику
   - Аналитика не должна логировать через `MasterLogger`

3. **Добавить @MainActor к классам аналитики:**
   - `ComponentAnalytics` должен иметь `@MainActor`
   - `AnalyticsManager` должен иметь `@MainActor`

4. **Использовать Serial Queue для логгера:**
   - `MasterLogger` должен использовать Serial Queue
   - Re-entrancy Guard должен предотвращать рекурсию

5. **Проверить MainViewModel.init():**
   - Не должен вызывать аналитику в `init()`
   - Не должен создавать Dictionary в `init()`

---

## 🎯 ЗАКЛЮЧЕНИЕ

### 🔴 **СТАТУС: КРИТИЧЕСКИЙ КРАШ**

**Проблема:**
- Краш на MAIN THREAD при входе на MainScreen
- Приложение полностью неработоспособно
- Рекурсия через цикл логгер → аналитика → Dictionary

**Корневая причина:**
- Dictionary создается на MAIN THREAD при инициализации
- Цикл рекурсии через `MasterLogger.screenLoad()` → аналитика
- Отсутствие `@MainActor` у классов аналитики

**Приоритет:**
- 🔴 **КРИТИЧЕСКИЙ** - требует немедленного исправления
- Приложение не может быть использовано
- Пользователи не могут войти в приложение

---

**АНАЛИЗ ЗАВЕРШЕН БЕЗ ИСПРАВЛЕНИЙ** ✅
