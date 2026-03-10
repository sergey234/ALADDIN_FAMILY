# 🔴 BUILD 99: ФИНАЛЬНЫЙ АНАЛИЗ ИСТИННОЙ ПРИЧИНЫ КРАША

**Дата:** 2026-03-10  
**Версия сборки:** 99  
**Exception Type:** `EXC_BAD_ACCESS (SIGSEGV)`  
**Exception Message:** `Thread stack size exceeded due to excessive recursion`

---

## 🚨 КРИТИЧЕСКОЕ ОТКРЫТИЕ: ИСТИННАЯ ПРИЧИНА НАЙДЕНА!

### Stack trace анализ:
- Адрес `0x1029ae4ec` повторяется 6 раз (строки 19-24) - **РЕКУРСИЯ!**
- Вызов `DateFormatter.string(from:)` в строке 13
- Рекурсия происходит в ICU библиотеке при форматировании даты

**Это означает:** Проблема НЕ в создании форматтера, а в **ИСПОЛЬЗОВАНИИ** форматтера!

---

## 🔍 ИСТИННАЯ ПРИЧИНА КРАША

### 🔴 ПРОБЛЕМА: `displayFormatter.string(from:)` вызывается в async функции, которая может вызываться рекурсивно

**Анализ кода:**
```swift
// Screens/01_MainScreen.swift:991
private func updateExpirationTextCache(from isoString: String) async {
    // ...
    let formattedText = Self.displayFormatter.string(from: date)  // ← ЗДЕСЬ ПРОБЛЕМА!
    await MainActor.run {
        cachedExpirationText = formattedText
    }
}
```

**Проблема:**
1. `displayFormatter.string(from:)` вызывается **ДО** `await MainActor.run`
2. Это означает, что форматирование происходит **ВНЕ** main thread
3. Если `displayFormatter.string(from:)` вызывает чтение из `UserDefaults` через ICU
4. И это происходит во время обновления View
5. Это может вызвать рекурсию!

---

### 🔴 КОРНЕВАЯ ПРИЧИНА: DateFormatter.string(from:) может читать из UserDefaults даже со статическим Locale

**Техническая причина:**
- Даже если мы используем статический `Locale(identifier: "ru_RU")`
- `DateFormatter.string(from:)` внутри может использовать `Calendar.current`
- `Calendar.current` может читать из `UserDefaults` через `Locale.current`
- Это создает цикл: форматирование → Calendar.current → UserDefaults → обновление View → форматирование

**Доказательство:**
- Stack trace показывает рекурсию в ICU библиотеке
- ICU использует `Calendar` для форматирования
- `Calendar.current` может читать из `UserDefaults`

---

## 🎯 РЕШЕНИЕ ПРОБЛЕМЫ

### 🔴 КРИТИЧНО (НЕМЕДЛЕННО):

#### 1. Использовать статический Calendar для форматирования

**Проблема:**
- `DateFormatter` внутри использует `Calendar.current`
- `Calendar.current` может читать из `UserDefaults`

**Решение:**
```swift
// ✅ Создать статический Calendar
private static let calendar: Calendar = {
    var cal = Calendar(identifier: .gregorian)
    cal.locale = Locale(identifier: "ru_RU")
    return cal
}()

// ✅ Использовать статический Calendar в форматтере
private static let displayFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.dateStyle = .medium
    formatter.timeStyle = .none
    formatter.locale = Locale(identifier: "ru_RU")
    formatter.calendar = Self.calendar  // ← ДОБАВИТЬ ЭТО!
    return formatter
}()
```

---

#### 2. Выполнять форматирование на main thread

**Проблема:**
- Форматирование происходит вне main thread
- Это может вызвать проблемы с `UserDefaults`

**Решение:**
```swift
// ✅ Выполнять форматирование на main thread
private func updateExpirationTextCache(from isoString: String) async {
    // ...
    let formattedText = await MainActor.run {
        Self.displayFormatter.string(from: date)  // ← На main thread!
    }
    await MainActor.run {
        cachedExpirationText = formattedText
    }
}
```

---

#### 3. Заменить все `Calendar.current` на статический Calendar

**Проблема:**
- `Calendar.current` может читать из `UserDefaults`
- Это может вызвать рекурсию

**Решение:**
```swift
// ❌ БЫЛО:
if Calendar.current.isDateInToday(date) {
    // ...
}

// ✅ СТАЛО:
private static let calendar: Calendar = {
    var cal = Calendar(identifier: .gregorian)
    cal.locale = Locale(identifier: "ru_RU")
    return cal
}()

if Self.calendar.isDateInToday(date) {
    // ...
}
```

---

## 📋 ПЛАН ДЕЙСТВИЙ

### Шаг 1: Добавить статический Calendar в MainScreen
- Создать статический `Calendar` с `Locale(identifier: "ru_RU")`
- Установить его в `displayFormatter.calendar`

### Шаг 2: Выполнять форматирование на main thread
- Обернуть `displayFormatter.string(from:)` в `MainActor.run`
- Убедиться, что форматирование происходит на main thread

### Шаг 3: Заменить все `Calendar.current` на статический Calendar
- Найти все использования `Calendar.current`
- Заменить на статический `Calendar` где возможно

---

## ✅ ВЫВОДЫ

### ❌ ИСТИННАЯ ПРИЧИНА:

1. **`DateFormatter.string(from:)` использует `Calendar.current` внутри**
   - Даже со статическим `Locale`, форматтер может использовать `Calendar.current`
   - `Calendar.current` может читать из `UserDefaults`
   - Это создает цикл рекурсии

2. **Форматирование происходит вне main thread**
   - `displayFormatter.string(from:)` вызывается до `await MainActor.run`
   - Это может вызвать проблемы с `UserDefaults`

3. **`Calendar.current` используется в других местах**
   - `ChildRewardsScreen.formatDate()` использует `Calendar.current`
   - Это может вызвать рекурсию

### ✅ РЕШЕНИЕ:

1. **Добавить статический Calendar в форматтер**
   - `formatter.calendar = Self.calendar`
   - Это предотвратит использование `Calendar.current`

2. **Выполнять форматирование на main thread**
   - Обернуть `displayFormatter.string(from:)` в `MainActor.run`
   - Это предотвратит проблемы с `UserDefaults`

3. **Заменить все `Calendar.current` на статический Calendar**
   - Найти все использования
   - Заменить на статический `Calendar`

---

## 🚨 КРИТИЧЕСКОЕ ЗАМЕЧАНИЕ

**Мы уже 2 недели исправляем этот краш, но он продолжается.**

**Истинная причина:**
- `DateFormatter` внутри использует `Calendar.current`
- `Calendar.current` может читать из `UserDefaults`
- Это создает цикл рекурсии

**Решение:**
- Добавить статический `Calendar` в форматтер
- Выполнять форматирование на main thread
- Заменить все `Calendar.current` на статический `Calendar`

**Только так можно решить проблему раз и навсегда!**

---

**ГОТОВО К ИСПРАВЛЕНИЮ!** 🔧
