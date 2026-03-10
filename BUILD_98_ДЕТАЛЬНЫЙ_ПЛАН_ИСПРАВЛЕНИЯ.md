# 🔧 BUILD 98: ДЕТАЛЬНЫЙ ПЛАН ИСПРАВЛЕНИЯ РЕКУРСИИ

**Дата:** 2026-03-10  
**Версия сборки:** 98 → 99  
**Цель:** Исправить рекурсию в `MainScreen.updateExpirationTextCache()`

---

## 📋 ПЛАН ИСПРАВЛЕНИЯ (3 этапа)

### 🔴 ЭТАП 1: Добавить защиту от рекурсии

**Цель:** Предотвратить повторные вызовы функции

**Действия:**
1. Добавить флаг `@State private var isUpdatingExpirationText: Bool = false`
2. Проверять флаг перед вызовом `updateExpirationTextCache()`
3. Устанавливать флаг во время обновления
4. Сбрасывать флаг после обновления

**Код:**
```swift
// Добавить флаг
@State private var isUpdatingExpirationText: Bool = false

// Модифицировать функцию
private func updateExpirationTextCache(from isoString: String) {
    // ✅ BUILD 99: Защита от рекурсии
    guard !isUpdatingExpirationText else {
        print("⚠️ [MainScreen] updateExpirationTextCache уже выполняется, пропускаем")
        return
    }
    
    isUpdatingExpirationText = true
    defer { isUpdatingExpirationText = false }
    
    guard !isoString.isEmpty else {
        cachedExpirationText = nil
        return
    }
    
    // ... остальной код ...
}
```

**Риск:** 🟢 Низкий  
**Время:** 5 минут

---

### 🔴 ЭТАП 2: Сделать функцию асинхронной

**Цель:** Предотвратить блокировку main thread

**Действия:**
1. Обернуть `updateExpirationTextCache()` в `Task { @MainActor in }`
2. Обновлять `@State` на main thread
3. Использовать `async/await` для асинхронности

**Код:**
```swift
// Модифицировать вызов в .onAppear
.onAppear {
    // ... другой код ...
    
    // ✅ BUILD 99: Асинхронное обновление кеша для предотвращения рекурсии
    Task { @MainActor in
        let currentExpiresAt = subscriptionExpiresAtIso
        await updateExpirationTextCache(from: currentExpiresAt)
    }
}

// Модифицировать функцию
private func updateExpirationTextCache(from isoString: String) async {
    // ✅ BUILD 99: Защита от рекурсии
    guard !isUpdatingExpirationText else {
        print("⚠️ [MainScreen] updateExpirationTextCache уже выполняется, пропускаем")
        return
    }
    
    isUpdatingExpirationText = true
    defer { isUpdatingExpirationText = false }
    
    guard !isoString.isEmpty else {
        cachedExpirationText = nil
        return
    }
    
    // ✅ Используем статический formatter вместо создания нового каждый раз
    var parsedDate = Self.isoFormatter.date(from: isoString)
    if parsedDate == nil {
        parsedDate = Self.isoFormatterFallback.date(from: isoString)
    }
    guard let date = parsedDate else {
        cachedExpirationText = nil
        return
    }
    
    // ✅ Используем статический displayFormatter
    cachedExpirationText = Self.displayFormatter.string(from: date)
}
```

**Риск:** 🟡 Средний (нужно проверить async/await)  
**Время:** 10 минут

---

### 🔴 ЭТАП 3: Заменить `.onAppear {}` на `.task {}`

**Цель:** Предотвратить повторные вызовы при обновлении View

**Действия:**
1. Заменить `.onAppear {}` на `.task {}`
2. `.task {}` вызывается только один раз при появлении View
3. Это предотвратит повторные вызовы при обновлении View

**Код:**
```swift
// Заменить .onAppear на .task
.task {
    // ✅ КРИТИЧНО: Логирование для TestFlight (работает в RELEASE)
    let startTime = Date()
    let logPrefix = "🔍 MainScreen.task"
    
    // ... другой код ...
    
    // ✅ BUILD 99: Асинхронное обновление кеша для предотвращения рекурсии
    let currentExpiresAt = subscriptionExpiresAtIso
    await updateExpirationTextCache(from: currentExpiresAt)
    debugLog.append("✅ cachedExpirationText инициализирован")
    
    // ... остальной код ...
}
```

**Риск:** 🟡 Средний (нужно проверить, что `.task {}` работает правильно)  
**Время:** 5 минут

---

## 📊 ПРИОРИТЕТЫ ИСПРАВЛЕНИЙ

| Этап | Приоритет | Риск | Время | Зависимости |
|------|-----------|------|------|-------------|
| #1: Защита от рекурсии | 🔴 Критично | 🟢 Низкий | 5 мин | Нет |
| #2: Асинхронность | 🔴 Критично | 🟡 Средний | 10 мин | Этап #1 |
| #3: Замена .onAppear | 🟡 Высоко | 🟡 Средний | 5 мин | Этап #2 |

**Общее время:** ~20 минут

---

## ✅ КРИТЕРИИ УСПЕХА

- [ ] Функция `updateExpirationTextCache()` не вызывается рекурсивно
- [ ] Нет крашей при запуске приложения
- [ ] Нет рекурсии в логах
- [ ] Все функции работают корректно
- [ ] Производительность не ухудшилась

---

## 🔍 ДЕТАЛЬНЫЙ ПЛАН ДЕЙСТВИЙ

### Шаг 1: Добавить флаг защиты от рекурсии

**Файл:** `Screens/01_MainScreen.swift`  
**Строка:** ~32 (после `@State private var cachedExpirationText`)

**Действия:**
1. Добавить `@State private var isUpdatingExpirationText: Bool = false`
2. Модифицировать `updateExpirationTextCache()` для проверки флага
3. Устанавливать флаг перед обновлением
4. Сбрасывать флаг после обновления

**Код:**
```swift
// После строки 32
@State private var isUpdatingExpirationText: Bool = false

// Модифицировать функцию updateExpirationTextCache (строка ~950)
private func updateExpirationTextCache(from isoString: String) {
    // ✅ BUILD 99: Защита от рекурсии
    guard !isUpdatingExpirationText else {
        print("⚠️ [MainScreen] updateExpirationTextCache уже выполняется, пропускаем")
        return
    }
    
    isUpdatingExpirationText = true
    defer { isUpdatingExpirationText = false }
    
    // ... остальной код без изменений ...
}
```

---

### Шаг 2: Сделать функцию асинхронной

**Файл:** `Screens/01_MainScreen.swift`  
**Строка:** ~950 (функция `updateExpirationTextCache`)

**Действия:**
1. Добавить `async` к функции `updateExpirationTextCache()`
2. Обернуть вызов в `.onAppear {}` в `Task { @MainActor in }`
3. Использовать `await` при вызове функции

**Код:**
```swift
// Модифицировать функцию (строка ~950)
private func updateExpirationTextCache(from isoString: String) async {
    // ... код из Шага 1 ...
}

// Модифицировать вызов в .onAppear (строка ~445)
Task { @MainActor in
    let currentExpiresAt = subscriptionExpiresAtIso
    await updateExpirationTextCache(from: currentExpiresAt)
}
```

---

### Шаг 3: Заменить `.onAppear {}` на `.task {}`

**Файл:** `Screens/01_MainScreen.swift`  
**Строка:** ~387 (`.onAppear {}`)

**Действия:**
1. Заменить `.onAppear {` на `.task {`
2. Убедиться, что все вызовы внутри используют `await`
3. Проверить, что логирование работает правильно

**Код:**
```swift
// Заменить .onAppear на .task (строка ~387)
.task {
    // ✅ КРИТИЧНО: Логирование для TestFlight (работает в RELEASE)
    let startTime = Date()
    let logPrefix = "🔍 MainScreen.task"
    
    // ... весь код из .onAppear ...
    
    // ✅ BUILD 99: Асинхронное обновление кеша для предотвращения рекурсии
    let currentExpiresAt = subscriptionExpiresAtIso
    await updateExpirationTextCache(from: currentExpiresAt)
    debugLog.append("✅ cachedExpirationText инициализирован")
    
    // ... остальной код ...
}
```

---

## ⚠️ РИСКИ И МИТИГАЦИЯ

### 🟢 РИСК #1: Флаг не сбрасывается при ошибке

**Митигация:**
- Использовать `defer { isUpdatingExpirationText = false }`
- Это гарантирует сброс флага даже при ошибке

---

### 🟡 РИСК #2: `.task {}` может не вызываться при обновлении View

**Митигация:**
- `.task {}` вызывается только один раз при появлении View
- Это именно то, что нам нужно
- Если нужно обновление при изменении `subscriptionExpiresAtIso`, добавить `.onChange()`

---

### 🟡 РИСК #3: Асинхронность может вызвать race condition

**Митигация:**
- Использовать `@MainActor` для гарантии выполнения на main thread
- Использовать флаг для предотвращения параллельных вызовов
- Использовать `await` для последовательного выполнения

---

## 📋 ЧЕКЛИСТ ПЕРЕД ИСПРАВЛЕНИЕМ

- [ ] Прочитан весь код `MainScreen.updateExpirationTextCache()`
- [ ] Понятна причина рекурсии
- [ ] Составлен план исправления
- [ ] Проверены все зависимости
- [ ] Подготовлен код для исправления

---

## 📋 ЧЕКЛИСТ ПОСЛЕ ИСПРАВЛЕНИЯ

- [ ] Код скомпилирован без ошибок
- [ ] Нет предупреждений компилятора
- [ ] Протестировано на симуляторе
- [ ] Протестировано на реальном устройстве
- [ ] Нет крашей при запуске
- [ ] Нет рекурсии в логах
- [ ] Все функции работают корректно

---

## ✅ ВЫВОДЫ

### ❌ ЧТО БУДЕТ ИСПРАВЛЕНО:

1. **Рекурсия в `updateExpirationTextCache()`** - добавлена защита от рекурсии
2. **Блокировка main thread** - функция сделана асинхронной
3. **Повторные вызовы** - `.onAppear {}` заменен на `.task {}`

### ✅ РЕЗУЛЬТАТ:

- Нет рекурсии при запуске приложения
- Нет крашей на главной странице
- Все функции работают корректно

---

**ГОТОВО К ИСПРАВЛЕНИЮ!** 🚀
