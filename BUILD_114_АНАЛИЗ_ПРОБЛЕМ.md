# 🔴 BUILD 114: АНАЛИЗ ДВУХ ПРОБЛЕМ

**Дата:** 2026-03-12  
**Build:** 114  
**Статус:** 🔴 **ДВЕ КРИТИЧЕСКИЕ ПРОБЛЕМЫ**

---

## 🔴 ПРОБЛЕМА #1: ОНБОРДИНГ ПРОПУСКАЕТСЯ

### 📊 **Что происходит:**

- При запуске приложения онбординг пропускается
- Приложение сразу переходит на главную страницу
- Раньше переход был через онбординг

---

### 🔍 **Причина:**

**Файл:** `ALADDINApp.swift`  
**Строки:** 684-687, 315-320

**Проблемный код:**
```swift
// В initializeNavigation:
if ALADDINApp.hasInitializedNavigation {
    print("🛠️ [ALADDINApp.initializeNavigation] Уже инициализировано, пропускаем")
    return  // ❌ ПРОБЛЕМА! Возвращается без установки экрана!
}

// В onAppear:
guard !Self.hasInitialized else {
    print("⚠️ ALADDINApp.onAppear уже вызван, пропускаем повторную инициализацию")
    return  // ❌ ПРОБЛЕМА! Возвращается без установки экрана!
}
```

**Проблема:**
- После добавления защиты от повторных вызовов (BUILD 113), `hasInitialized` и `hasInitializedNavigation` остаются `true` между запусками приложения
- При следующем запуске приложения, `initializeNavigation` возвращается сразу, не устанавливая экран
- `navigationManager.currentScreen` остается в дефолтном состоянии (вероятно, `.main`)

---

### ✅ **Решение:**

**Нужно сбрасывать флаги при каждом запуске приложения:**

```swift
// ✅ BUILD 114: Сбрасываем флаги при каждом запуске приложения
// Статические флаги должны быть сброшены при каждом новом запуске
private static var hasInitialized = false
private static var hasInitializedNavigation = false

// ИЛИ использовать @State для отслеживания состояния приложения
```

**ИЛИ:**

**Нужно проверять состояние онбординга ДО проверки флага:**

```swift
.onAppear {
    // ✅ BUILD 114: Сначала проверяем состояние онбординга
    // Если онбординг не пройден, устанавливаем экран онбординга
    if !hasCompletedOnboarding {
        navigationManager.currentScreen = .onboarding
        return
    }
    
    // Только потом проверяем флаг инициализации
    guard !Self.hasInitialized else {
        return
    }
    // ...
}
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
  3   ALADDIN    0x104430ff9  (наш код)
  4   ALADDIN    0x10472259d  (наш код)
  5   ALADDIN    0x104430ff9  (повторяется!)
  6   libswift_Concurrency.dylib    completeTaskWithClosure
  ```

**Вывод:** Краш происходит из-за двойного вызова `CheckedContinuation.resume()` или вызова после завершения!

---

### 🔍 **Причина:**

**Проблема:** `CheckedContinuation.resume()` вызывается дважды или после завершения задачи.

**Типичные причины:**
1. `continuation.resume()` вызывается дважды в разных местах
2. `continuation.resume()` вызывается после того, как continuation уже был завершен
3. Нет защиты от повторных вызовов в async/await коде

---

### ✅ **Решение:**

**Нужно найти все места где используется `CheckedContinuation` и добавить защиту:**

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
   - Сбрасывать `hasInitialized` и `hasInitializedNavigation` при каждом запуске
   - ИЛИ проверять состояние онбординга ДО проверки флага

2. ✅ **Найти и исправить CheckedContinuation**
   - Найти все места где используется `CheckedContinuation`
   - Добавить защиту от повторных вызовов `resume()`

---

## 🎯 ЗАКЛЮЧЕНИЕ

### 🔴 **ДВЕ ПРОБЛЕМЫ:**

1. ✅ **Онбординг пропускается** - из-за статических флагов, которые остаются `true` между запусками
2. ✅ **Краш EXC_BREAKPOINT** - из-за двойного вызова `CheckedContinuation.resume()`

### ✅ **РЕШЕНИЕ:**

1. ✅ Сбрасывать статические флаги при каждом запуске приложения
2. ✅ Найти и исправить все места где используется `CheckedContinuation`

---

**ГОТОВ К ИСПРАВЛЕНИЮ!** 🚀
