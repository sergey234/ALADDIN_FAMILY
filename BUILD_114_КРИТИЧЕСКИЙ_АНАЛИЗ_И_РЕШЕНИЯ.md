# 🔴 BUILD 114: КРИТИЧЕСКИЙ АНАЛИЗ ДВУХ ПРОБЛЕМ

**Дата:** 2026-03-12  
**Build:** 114  
**Incident Identifier:** C9359DF8-59D7-441E-A4D8-E3D2EEAC952D  
**Статус:** 🔴 **ДВЕ КРИТИЧЕСКИЕ ПРОБЛЕМЫ**

---

## 🔴 ПРОБЛЕМА #1: ОНБОРДИНГ ПРОПУСКАЕТСЯ

### 📊 **Что происходит:**

- При запуске приложения онбординг пропускается
- Приложение сразу переходит на главную страницу
- Раньше переход был через онбординг

---

### 🔍 **ИСТИННАЯ ПРИЧИНА:**

**Файл:** `ALADDINApp.swift`  
**Строки:** 145-146, 315-320, 684-687

**Проблемный код:**
```swift
// Статические флаги (остаются true между запусками приложения!)
private static var hasInitialized = false
private static var hasInitializedNavigation = false

// В onAppear:
guard !Self.hasInitialized else {
    return  // ❌ Возвращается БЕЗ установки экрана!
}

// В initializeNavigation:
if ALADDINApp.hasInitializedNavigation {
    return  // ❌ Возвращается БЕЗ установки экрана!
}
```

**Проблема:**
- После BUILD 113, статические флаги `hasInitialized` и `hasInitializedNavigation` остаются `true` между запусками приложения
- При следующем запуске приложения, `onAppear` и `initializeNavigation` возвращаются сразу
- `navigationManager.currentScreen` остается в дефолтном состоянии (вероятно, `.main`)
- Онбординг никогда не показывается!

---

### ✅ **РЕШЕНИЕ:**

**Вариант 1: Сбрасывать флаги при каждом запуске приложения**

```swift
// ✅ BUILD 114: Сбрасываем флаги при каждом запуске приложения
// Используем @State для отслеживания состояния приложения
@State private var hasInitialized = false

// ИЛИ использовать scenePhase для отслеживания запуска
.onChange(of: scenePhase) { newPhase in
    if newPhase == .inactive {
        // Приложение закрывается - сбрасываем флаги
        Self.hasInitialized = false
        Self.hasInitializedNavigation = false
    }
}
```

**Вариант 2: Проверять состояние онбординга ДО проверки флага (РЕКОМЕНДУЮ!)**

```swift
.onAppear {
    // ✅ BUILD 114: Сначала проверяем состояние онбординга
    // Если онбординг не пройден, устанавливаем экран онбординга
    if !hasCompletedOnboarding {
        navigationManager.currentScreen = .onboarding
        // НЕ возвращаемся - продолжаем инициализацию
    }
    
    // Только потом проверяем флаг инициализации
    guard !Self.hasInitialized else {
        return
    }
    Self.hasInitialized = true
    
    // Продолжаем инициализацию...
}
```

**Вариант 3: Использовать @State вместо static (ЛУЧШЕ!)**

```swift
// ✅ BUILD 114: Используем @State вместо static
// @State сбрасывается при каждом создании View
@State private var hasInitialized = false

// НО! Проблема: @State не работает в static методах
// Нужно использовать instance property
```

---

## 🔴 ПРОБЛЕМА #2: КРАШ EXC_BREAKPOINT (SIGTRAP)

### 📊 **Детали краша:**

- **Exception Type:** `EXC_BREAKPOINT (SIGTRAP)`
- **Exception Codes:** `0x0000000000000001`
- **Thread:** Thread 0 (Main Thread)
- **Ключевой стек:**
  ```
  0   libswiftCore.dylib    _assertionFailure(_:_:file:line:flags:)
  1   libswift_Concurrency.dylib    CheckedContinuation.resume(throwing:)
  2   ALADDIN    0x10493bda4  (наш код)
  3   ALADDIN    0x104430ff9  (наш код - повторяется!)
  4   ALADDIN    0x10472259d  (наш код)
  5   ALADDIN    0x104430ff9  (повторяется!)
  6   libswift_Concurrency.dylib    completeTaskWithClosure
  ```

**Вывод:** Краш происходит из-за двойного вызова `CheckedContinuation.resume()` или вызова после завершения!

---

### 🔍 **ИСТИННАЯ ПРИЧИНА:**

**Проблема:** `CheckedContinuation.resume()` вызывается дважды или после завершения задачи.

**Найдено использование CheckedContinuation:**
1. `StoreManager.validateReceipt()` - строки 536-546
2. `SubscriptionManager.registerDeviceAnonymously()` - строки 671-717
3. `NetworkProtectionScreen` - строки 965-1005
4. `APIService` - множественные места

**Типичные причины:**
1. `continuation.resume()` вызывается дважды в разных местах (например, в success и error handlers)
2. `continuation.resume()` вызывается после того, как continuation уже был завершен
3. Нет защиты от повторных вызовов в async/await коде

---

### ✅ **РЕШЕНИЕ:**

**Нужно добавить защиту от повторных вызовов во все места где используется CheckedContinuation:**

```swift
// ❌ ПЛОХО:
let continuation = CheckedContinuation<Result, Error> { ... }
continuation.resume(returning: result)  // Может быть вызван дважды!

// ✅ ХОРОШО:
var hasResumed = false
let continuation = CheckedContinuation<Result, Error> { ... }
if !hasResumed {
    hasResumed = true
    continuation.resume(returning: result)
}
```

---

## 🎯 ПЛАН ИСПРАВЛЕНИЙ

### 🔴 **КРИТИЧНО:**

1. ✅ **Исправить логику онбординга**
   - Проверять состояние онбординга ДО проверки флага `hasInitialized`
   - Устанавливать экран онбординга если он не пройден

2. ✅ **Найти и исправить CheckedContinuation**
   - Проверить все места где используется `CheckedContinuation`
   - Добавить защиту от повторных вызовов `resume()`

---

## 🎯 ЗАКЛЮЧЕНИЕ

### 🔴 **ДВЕ ПРОБЛЕМЫ:**

1. ✅ **Онбординг пропускается** - из-за статических флагов, которые остаются `true` между запусками
2. ✅ **Краш EXC_BREAKPOINT** - из-за двойного вызова `CheckedContinuation.resume()`

### ✅ **РЕШЕНИЕ:**

1. ✅ Проверять состояние онбординга ДО проверки флага `hasInitialized`
2. ✅ Найти и исправить все места где используется `CheckedContinuation`

---

**ГОТОВ К ИСПРАВЛЕНИЮ!** 🚀
