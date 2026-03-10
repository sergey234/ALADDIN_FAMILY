# 🔴 BUILD 98: ДЕТАЛЬНЫЙ АНАЛИЗ И РЕКОМЕНДАЦИИ

**Дата:** 2026-03-10  
**Версия сборки:** 98  
**Exception Type:** `EXC_BAD_ACCESS (SIGSEGV)`  
**Exception Message:** `Thread stack size exceeded due to excessive recursion`

---

## 📊 КРИТИЧЕСКИЙ АНАЛИЗ

### 🔴 ГЛАВНАЯ ПРОБЛЕМА: РЕКУРСИЯ ПРОДОЛЖАЕТСЯ!

**Stack trace показывает:**
- Адрес `0x1009f636c` повторяется 6 раз (строки 19-24)
- Это означает рекурсивный вызов функции
- Рекурсия происходит в `DateFormatter.string(from:)`
- Проблема НЕ решена моими предыдущими исправлениями

---

## 🔍 НАЙДЕННАЯ ПРОБЛЕМА

### 🔴 ПРОБЛЕМА: `updateExpirationTextCache()` вызывается в `onAppear`

**Код:**
```swift
// Screens/01_MainScreen.swift:445
.onAppear {
    let currentExpiresAt = subscriptionExpiresAtIso
    updateExpirationTextCache(from: currentExpiresAt)
    // ...
}

// Screens/01_MainScreen.swift:967
private func updateExpirationTextCache(from isoString: String) {
    // ...
    cachedExpirationText = Self.displayFormatter.string(from: date)
}
```

**Проблема:**
1. `onAppear` вызывается при появлении View
2. `updateExpirationTextCache()` вызывается в `onAppear`
3. `updateExpirationTextCache()` обновляет `cachedExpirationText` (это `@State`)
4. Обновление `@State` вызывает перерисовку View
5. Перерисовка View может вызвать `onAppear` снова
6. Это создает рекурсию!

---

## 🎯 РЕКОМЕНДАЦИИ

### 🔴 КРИТИЧНО (НЕМЕДЛЕННО):

#### 1. **УБРАТЬ ВЫЗОВ `updateExpirationTextCache()` ИЗ `onAppear`**

**Проблема:**
- `onAppear` вызывается при каждом обновлении View
- Если `updateExpirationTextCache()` обновляет `@State`, это вызывает обновление View
- Это создает рекурсию

**Решение:**
- Вызывать `updateExpirationTextCache()` только один раз при инициализации
- Использовать флаг для предотвращения повторных вызовов
- Или использовать `.task {}` вместо `.onAppear {}`

---

#### 2. **СДЕЛАТЬ `updateExpirationTextCache()` АСИНХРОННОЙ**

**Проблема:**
- Синхронное обновление `@State` в `onAppear` может вызвать рекурсию

**Решение:**
- Обернуть `updateExpirationTextCache()` в `Task { @MainActor in }`
- Это предотвратит блокировку main thread
- Это предотвратит рекурсию

---

#### 3. **ИСПОЛЬЗОВАТЬ `.task {}` ВМЕСТО `.onAppear {}`**

**Проблема:**
- `.onAppear {}` вызывается при каждом обновлении View
- `.task {}` вызывается только один раз при появлении View

**Решение:**
- Заменить `.onAppear {}` на `.task {}`
- Это предотвратит повторные вызовы

---

### 🟡 ВЫСОКО (В БЛИЖАЙШЕЕ ВРЕМЯ):

#### 4. **ДОБАВИТЬ ЗАЩИТУ ОТ РЕКУРСИИ**

**Решение:**
- Добавить флаг `isUpdatingExpirationText`
- Проверять флаг перед вызовом `updateExpirationTextCache()`
- Устанавливать флаг во время обновления
- Сбрасывать флаг после обновления

---

#### 5. **ИСПОЛЬЗОВАТЬ `@Published` ВМЕСТО `@State`**

**Решение:**
- Создать `@Published` свойство в ViewModel
- Обновлять его асинхронно
- Использовать его в View

---

## 📋 ПЛАН ДЕЙСТВИЙ

### Шаг 1: Убрать вызов из `onAppear`
- Заменить `.onAppear {}` на `.task {}`
- Или добавить флаг для предотвращения повторных вызовов

### Шаг 2: Сделать функцию асинхронной
- Обернуть `updateExpirationTextCache()` в `Task { @MainActor in }`
- Это предотвратит блокировку main thread

### Шаг 3: Добавить защиту от рекурсии
- Добавить флаг `isUpdatingExpirationText`
- Проверять флаг перед вызовом функции

### Шаг 4: Протестировать
- Проверить на симуляторе
- Проверить на реальном устройстве
- Убедиться, что рекурсия не происходит

---

## ✅ ВЫВОДЫ

### ❌ ЧТО ПРОИСХОДИТ:

1. **Рекурсия в `updateExpirationTextCache()`** - функция вызывается в `onAppear`
2. **Обновление `@State` вызывает перерисовку View** - это вызывает `onAppear` снова
3. **Это создает бесконечную рекурсию** - пока не произойдет краш

### ✅ ЧТО НУЖНО СДЕЛАТЬ:

1. **Убрать вызов из `onAppear`** - использовать `.task {}` или флаг
2. **Сделать функцию асинхронной** - обернуть в `Task { @MainActor in }`
3. **Добавить защиту от рекурсии** - использовать флаг

---

**ГОТОВО К ИСПРАВЛЕНИЮ!** 🚀
