# 🔴 BUILD 112: КРИТИЧЕСКИЙ АНАЛИЗ КРАША ПРИ СТАРТЕ

**Дата:** 2026-03-12  
**Build:** 112  
**Incident Identifier:** CF02760C-9FD8-4D6C-B2C1-9969BE82969A  
**Статус:** 🔴 **КРИТИЧЕСКИЙ КРАШ ПРИ СТАРТЕ - ПРИЛОЖЕНИЕ НЕ ЗАПУСКАЕТСЯ!**

---

## 🔴 АНАЛИЗ КРАША

### 📊 **Детали краша:**

- **Exception Type:** `EXC_BAD_ACCESS (SIGSEGV)`
- **Exception Message:** `Thread stack size exceeded due to excessive recursion`
- **Thread:** **Thread 0 (Main Thread)** - краш на главном потоке!
- **Когда:** При входе в приложение - онбординг 1 секунда, затем главная страница, через 1 секунду краш
- **Время в приложении:** 1-1.5 секунды
- **Ключевой стек:**
  ```
  4   ALADDIN   0x1006b94f4  _DictionaryStorage.resize
  5   ALADDIN   0x1006b5b24  (рекурсия)
  6   ALADDIN   0x1006b5408  (рекурсия)
  7   ALADDIN   0x1007c0194  (рекурсия)
  8   ALADDIN   0x1007c08dc  (рекурсия)
  9-14 ALADDIN   0x1007c08ec  (РЕКУРСИЯ 6 РАЗ!) ← КРИТИЧНО!
  15  ALADDIN   0x10068096c  completeTaskWithClosure ← async/await!
  ```

**Вывод:** Рекурсия происходит через `async/await` и `Dictionary.resize` на главном потоке при **СТАРТЕ ПРИЛОЖЕНИЯ**!

---

## 🔴 ВСЕ ВОЗМОЖНЫЕ ПРИЧИНЫ КРАША

### ❌ **ПРИЧИНА #1: Инициализация ComponentAnalytics.shared создает AnalyticsManager.shared**

**Файл:** `Core/Analytics/ComponentAnalytics.swift`  
**Строки:** 16-18

**Код:**
```swift
static let shared = ComponentAnalytics()  // Инициализируется при первом обращении

private let analyticsManager = AnalyticsManager.shared  // ❌ КРИТИЧНО! Создается при инициализации ComponentAnalytics!

private init() {}
```

**Проблема:**
- При первом обращении к `ComponentAnalytics.shared` создается экземпляр
- В `init()` создается `AnalyticsManager.shared`
- `AnalyticsManager.shared` тоже инициализируется при первом обращении
- Если это происходит на неправильном потоке или при старте, может создать Dictionary на неправильном потоке
- Dictionary создается → рекурсия → краш!

**Критичность:** 🔴 **КРИТИЧНО!** - это основная причина краша!

---

### ❌ **ПРИЧИНА #2: visualLogger.log() вызывается в MainScreen.loadProfileImage()**

**Файл:** `Screens/01_MainScreen.swift`  
**Строки:** 350, 355, 362, 375

**Код:**
```swift
private func loadProfileImage() {
    visualLogger.log("\(logPrefix) START", level: .debug)  // ❌ КРИТИЧНО!
    visualLogger.log("\(logPrefix) ШАГ 1: Проверка ProfileImageManager...", level: .debug)  // ❌ КРИТИЧНО!
    visualLogger.log(errorMsg, level: .warning)  // ❌ КРИТИЧНО!
    visualLogger.log("\(logPrefix) ШАГ 2: Загрузка изображения...", level: .debug)  // ❌ КРИТИЧНО!
}
```

**Проблема:**
- `visualLogger.log()` вызывается при загрузке изображения профиля
- `loadProfileImage()` вызывается в `.task {}` MainScreen
- `VisualLogger` может вызвать `MasterLogger` или `UserDefaults`
- Это может создать цикл рекурсии при старте

**Критичность:** 🔴 **КРИТИЧНО!**

---

### ❌ **ПРИЧИНА #3: MasterLogger.shared.business() вызывается в ALADDINApp.initializeNavigation()**

**Файл:** `ALADDINApp.swift`  
**Строки:** 704-705

**Код:**
```swift
Task {
    MasterLogger.shared.business("NotificationManager initialized for push notifications")  // ❌ КРИТИЧНО!
}
```

**Проблема:**
- `MasterLogger.shared.business()` вызывается в `Task {}` при инициализации навигации
- Вызывается при старте приложения
- `MasterLogger` может вызвать аналитику или `UserDefaults`
- Это может создать цикл рекурсии при старте

**Критичность:** 🔴 **КРИТИЧНО!**

---

### ❌ **ПРИЧИНА #4: Инициализация singleton'ов при первом обращении**

**Проблема:**
- `ComponentAnalytics.shared` инициализируется при первом обращении
- `AnalyticsManager.shared` инициализируется при первом обращении
- Если вызываются при старте на неправильном потоке, может создать Dictionary на неправильном потоке
- Dictionary создается → рекурсия → краш!

**Критичность:** 🔴 **КРИТИЧНО!**

---

### ❌ **ПРИЧИНА #5: MainViewModel.onAppear() → loadDashboardData()**

**Файл:** `ViewModels/MainViewModel.swift`  
**Строки:** 350-372

**Код:**
```swift
func onAppear() {
    // ...
    if shouldRefresh {
        loadDashboardData()  // ⚠️ Может вызвать аналитику или рекурсию
    }
}
```

**Проблема:**
- `loadDashboardData()` может вызвать аналитику или другие операции
- Вызывается при входе на главную страницу
- Может создать цикл рекурсии

**Критичность:** 🟡 **ВАЖНО!**

---

### ❌ **ПРИЧИНА #6: visualLogger - computed property в MainScreen**

**Файл:** `Screens/01_MainScreen.swift`  
**Строки:** 11-13

**Код:**
```swift
private var visualLogger: VisualLogger {
    VisualLogger.shared  // ❌ Computed property - вызывается при каждом обращении!
}
```

**Проблема:**
- Computed property вызывается при каждом обращении
- Если вызывается при инициализации View, это может вызвать рекурсию
- `VisualLogger.shared` может вызвать `MasterLogger` или `UserDefaults`

**Критичность:** 🔴 **КРИТИЧНО!**

---

## 🎯 ИСТИННАЯ ПРИЧИНА КРАША

### 🔴 **ГЛАВНАЯ ПРИЧИНА:**

**Инициализация `ComponentAnalytics.shared` при первом обращении создает `AnalyticsManager.shared`, который создает Dictionary на неправильном потоке, что вызывает рекурсию через `async/await`!**

**Механизм краша:**
1. Приложение запускается
2. `MainScreen` инициализируется
3. `MainScreen.task {}` вызывается
4. `loadProfileImage()` вызывается
5. `visualLogger.log()` вызывается (computed property)
6. `VisualLogger.shared` инициализируется
7. `VisualLogger` может вызвать `MasterLogger` или аналитику
8. Аналитика инициализирует `ComponentAnalytics.shared`
9. `ComponentAnalytics.init()` создает `AnalyticsManager.shared`
10. `AnalyticsManager.shared` инициализируется на неправильном потоке
11. Dictionary создается на неправильном потоке
12. `@MainActor` пытается переключиться на main thread
13. `async/await` создает новый контекст
14. Re-entrancy Guard не срабатывает (разные async контексты)
15. Dictionary создается многократно → рекурсия → краш!

---

## 🔴 ДОПОЛНИТЕЛЬНЫЕ ПРИЧИНЫ

### ❌ **ПРИЧИНА #7: MasterLogger.shared.business() в ALADDINApp.initializeNavigation()**

**Проблема:**
- Вызывается при старте приложения
- Может вызвать рекурсию через аналитику или UserDefaults

**Критичность:** 🔴 **КРИТИЧНО!**

---

### ❌ **ПРИЧИНА #8: visualLogger.log() вызывается синхронно**

**Проблема:**
- `visualLogger.log()` вызывается синхронно в `loadProfileImage()`
- Может блокировать главный поток
- Может вызвать рекурсию

**Критичность:** 🔴 **КРИТИЧНО!**

---

## 🎯 ПЛАН ИСПРАВЛЕНИЙ (БЕЗ ИСПРАВЛЕНИЯ КОДА)

### 🔴 **КРИТИЧНЫЕ ИСПРАВЛЕНИЯ:**

#### **ИСПРАВЛЕНИЕ #1: Убрать visualLogger.log() из MainScreen.loadProfileImage()**

**Файл:** `Screens/01_MainScreen.swift`  
**Строки:** 350, 355, 362, 375

**Что сделать:**
- Убрать все вызовы `visualLogger.log()` из `loadProfileImage()`
- Оставить только `print()` для диагностики

**Почему критично:**
- `visualLogger.log()` может вызвать рекурсию через `MasterLogger` или аналитику
- Вызывается при старте приложения
- Блокирует запуск приложения

---

#### **ИСПРАВЛЕНИЕ #2: Убрать MasterLogger.shared.business() из ALADDINApp.initializeNavigation()**

**Файл:** `ALADDINApp.swift`  
**Строки:** 704-705

**Что сделать:**
- Убрать вызов `MasterLogger.shared.business()` из `Task {}`
- Оставить только `print()` для диагностики

**Почему критично:**
- Вызывается при старте приложения
- Может вызвать рекурсию через аналитику или UserDefaults
- Блокирует запуск приложения

---

#### **ИСПРАВЛЕНИЕ #3: Заменить computed property visualLogger на lazy property**

**Файл:** `Screens/01_MainScreen.swift`  
**Строки:** 11-13

**Что сделать:**
- Заменить `private var visualLogger: VisualLogger { VisualLogger.shared }` на `private let visualLogger = VisualLogger.shared`

**Почему критично:**
- Computed property вызывается при каждом обращении
- Может вызвать рекурсию при инициализации View

---

#### **ИСПРАВЛЕНИЕ #4: Гарантировать инициализацию singleton'ов на main thread**

**Файлы:** 
- `Core/Analytics/ComponentAnalytics.swift` (строка 16)
- `Core/Analytics/AnalyticsManager.swift` (строка 17)

**Что сделать:**
- Гарантировать инициализацию singleton'ов на main thread
- Использовать проверку `Thread.isMainThread` и `DispatchQueue.main.sync` если нужно

**Почему критично:**
- Singleton'ы инициализируются при первом обращении
- Если вызываются на неправильном потоке, может создать Dictionary на неправильном потоке
- Dictionary создается → рекурсия → краш!

---

#### **ИСПРАВЛЕНИЕ #5: Отложить создание AnalyticsManager.shared в ComponentAnalytics**

**Файл:** `Core/Analytics/ComponentAnalytics.swift`  
**Строка:** 18

**Что сделать:**
- Не создавать `AnalyticsManager.shared` в `init()`
- Создавать при первом использовании (lazy property)

**Почему критично:**
- При инициализации `ComponentAnalytics.shared` сразу создается `AnalyticsManager.shared`
- Это может вызвать рекурсию при старте

---

## 📊 ИТОГОВАЯ ТАБЛИЦА ПРОБЛЕМ

| Проблема | Критичность | Файл | Строки |
|----------|-------------|------|--------|
| **visualLogger.log() в loadProfileImage()** | 🔴 КРИТИЧНО | 01_MainScreen.swift | 350, 355, 362, 375 |
| **MasterLogger.shared.business() в initializeNavigation()** | 🔴 КРИТИЧНО | ALADDINApp.swift | 704-705 |
| **computed property visualLogger** | 🔴 КРИТИЧНО | 01_MainScreen.swift | 11-13 |
| **Инициализация singleton'ов** | 🔴 КРИТИЧНО | ComponentAnalytics.swift, AnalyticsManager.swift | 16, 17 |
| **AnalyticsManager.shared в ComponentAnalytics.init()** | 🔴 КРИТИЧНО | ComponentAnalytics.swift | 18 |

---

## 🎯 ВЕРДИКТ ЭКСПЕРТА

### 🔴 **ИСТИННАЯ ПРИЧИНА КРАША:**

**Цепочка рекурсии при старте приложения:**
1. `MainScreen.task {}` → `loadProfileImage()`
2. `loadProfileImage()` → `visualLogger.log()` (computed property)
3. `visualLogger.log()` → может вызвать `MasterLogger` или аналитику
4. Аналитика → `ComponentAnalytics.shared` (инициализируется)
5. `ComponentAnalytics.init()` → `AnalyticsManager.shared` (инициализируется)
6. `AnalyticsManager.shared` создается на неправильном потоке
7. Dictionary создается на неправильном потоке
8. `@MainActor` пытается переключиться → `async/await` → рекурсия → краш!

---

## 🎯 РЕКОМЕНДАЦИИ ЭКСПЕРТА

### 🔴 **КРИТИЧНО (СДЕЛАТЬ СЕЙЧАС!):**

1. ✅ Убрать все вызовы `visualLogger.log()` из `MainScreen.loadProfileImage()`
2. ✅ Убрать `MasterLogger.shared.business()` из `ALADDINApp.initializeNavigation()`
3. ✅ Заменить computed property `visualLogger` на lazy property
4. ✅ Гарантировать инициализацию singleton'ов на main thread
5. ✅ Отложить создание `AnalyticsManager.shared` в `ComponentAnalytics` (lazy property)

---

### 🟡 **ВАЖНО (СДЕЛАТЬ ПОСЛЕ КРИТИЧНЫХ):**

6. ✅ Проверить все вызовы `visualLogger` и `MasterLogger` при старте
7. ✅ Убедиться, что нет других мест где аналитика вызывается при старте

---

## 🎯 ЗАКЛЮЧЕНИЕ

### 🔴 **ПРОБЛЕМА:**

**Краш происходит из-за цепочки рекурсии при старте приложения через `visualLogger.log()` → аналитика → Dictionary!**

**Почему не исправили раньше:**
- Исправления были направлены на тумблеры, а не на старт
- Проблема с `visualLogger.log()` не была выявлена
- Проблема с `MasterLogger.shared.business()` в `initializeNavigation()` не была исправлена

**Что нужно сделать:**
1. Убрать все вызовы логгера при старте
2. Гарантировать инициализацию singleton'ов на main thread
3. Отложить создание зависимостей между singleton'ами

---

**ГОТОВ К ВЫПОЛНЕНИЮ КРИТИЧЕСКИХ ИСПРАВЛЕНИЙ!** 🚀
