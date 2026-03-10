# 🚨 BUILD 100: КРИТИЧЕСКИЙ АНАЛИЗ НОВОГО КРАША

**Дата краша:** 2026-03-10 22:27:38  
**Build:** 100  
**Статус:** 🔴 **КРИТИЧЕСКАЯ ПРОБЛЕМА - РЕКУРСИЯ ВЕРНУЛАСЬ!**

---

## 📊 АНАЛИЗ КРАША

### Основная информация:

**Exception Type:** `EXC_BAD_ACCESS (SIGBUS)`  
**Exception Message:** `Thread stack size exceeded due to excessive recursion`  
**Thread:** Thread 7 - `Dispatch queue: com.apple.root.user-initiated-qos.cooperative` (BACKGROUND THREAD!)

**Ключевое отличие от BUILD 99:**
- BUILD 99: Рекурсия в **main thread** (Thread 0)
- BUILD 100: Рекурсия в **background thread** (Thread 7)

---

## 🔍 СРАВНЕНИЕ С BUILD 99

### BUILD 99 (предыдущий краш):
- **Thread:** Thread 0 (main thread)
- **Место:** `MainScreen.task {}` - синхронный вызов
- **Причина:** `DateFormatter.string()` вызывался синхронно в main thread
- **Исправление:** Добавлен `await MainActor.run` для форматирования

### BUILD 100 (новый краш):
- **Thread:** Thread 7 (background thread - `user-initiated-qos.cooperative`)
- **Место:** Похоже на тот же код, но в background thread
- **Причина:** Возможно, `DateFormatterService` вызывается из background thread без `MainActor`

---

## 🔍 АНАЛИЗ STACK TRACE

### Thread 7 (Crashed):

```
13  ALADDIN  0x104d2eb1c  // Возможно: DateFormatter.string() или DateFormatterService
14  ALADDIN  0x104d2fdb8  // Возможно: updateExpirationTextCache()
15  ALADDIN  0x104dbe47c  // Рекурсия начинается здесь
16  ALADDIN  0x104d8a014  // Рекурсивный вызов
17  ALADDIN  0x104d89d94  // Рекурсивный вызов
18  ALADDIN  0x104d8a074  // Рекурсивный вызов
19  ALADDIN  0x104d8a080  // Рекурсивный вызов
20  ALADDIN  0x104d8a080  // РЕКУРСИЯ! (повторяется много раз)
21  ALADDIN  0x104d8a080  // РЕКУРСИЯ!
22  ALADDIN  0x104d8a080  // РЕКУРСИЯ!
23  ALADDIN  0x104d8a080  // РЕКУРСИЯ!
24  ALADDIN  0x104d8a080  // РЕКУРСИЯ!
```

**Вывод:**
- Рекурсия происходит в коде ALADDIN (не в системных библиотеках)
- Адрес `0x104d8a080` повторяется много раз - это рекурсивный вызов
- Рекурсия связана с DateFormatter (ICU library в stack trace)

---

## 🔍 ПРИЧИНЫ ВОЗНИКНОВЕНИЯ

### Возможная причина 1: DateFormatterService вызывается из background thread

**Проблема:**
- Мы создали `DateFormatterService` с `@MainActor`
- Но если он вызывается из background thread без `await`, может возникнуть проблема
- `DateFormatter` требует main thread для работы с `Locale` и `Calendar`

**Проверка:**
```swift
// В DateFormatterService:
@MainActor
class DateFormatterService {
    func formatExpirationDate(from isoString: String) -> String? {
        // Если вызывается из background thread без await, может быть проблема
    }
}
```

---

### Возможная причина 2: Изменения в JWTCircuitBreaker вызвали проблему

**Проблема:**
- Мы только что изменили `JWTCircuitBreaker` - добавили `isMainInstance` параметр
- Но это не должно вызывать рекурсию в DateFormatter

**Вероятность:** Низкая

---

### Возможная причина 3: updateExpirationTextCache вызывается из background thread

**Проблема:**
- `updateExpirationTextCache` может вызываться из background thread
- Если внутри используется `DateFormatterService` без правильного `await MainActor.run`
- Может возникнуть рекурсия

**Проверка:**
```swift
// В MainScreen:
private func updateExpirationTextCache(from isoString: String) async {
    // Если вызывается из background thread
    // И DateFormatterService требует MainActor
    // Может быть проблема
}
```

---

### Возможная причина 4: Calendar.current все еще используется где-то

**Проблема:**
- Мы исправили `Calendar.current` в `DateFormatterService`
- Но возможно, где-то еще используется `Calendar.current`
- Это может вызвать рекурсию через `UserDefaults`

**Вероятность:** Средняя

---

## ⚠️ КРИТИЧЕСКИЕ ВОПРОСЫ

### 1. Почему краш в background thread?

**Вопрос:**
- BUILD 99 крашился в main thread
- BUILD 100 крашится в background thread
- Что изменилось?

**Возможные причины:**
- `updateExpirationTextCache` теперь вызывается из background thread
- `DateFormatterService` вызывается из background thread без правильного `await`
- Где-то используется `Task` без `@MainActor`

---

### 2. Откуда взялась рекурсия?

**Вопрос:**
- Мы исправили рекурсию в BUILD 100
- Но она вернулась в другом месте
- Что мы упустили?

**Возможные причины:**
- `DateFormatterService` не правильно используется
- Где-то все еще используется `Calendar.current`
- Где-то все еще используется `Locale.current` напрямую

---

### 3. Что изменилось с BUILD 99?

**Вопрос:**
- BUILD 99 работал после исправлений
- BUILD 100 крашится
- Что мы изменили?

**Изменения:**
- ✅ Добавлен `DateFormatterService`
- ✅ Изменен `JWTCircuitBreaker` (добавлен `isMainInstance`)
- ✅ Оптимизирован `testLogger` в SettingsScreen

**Возможная проблема:**
- `DateFormatterService` может вызываться неправильно
- Или где-то все еще используется старый код

---

## 🔍 ЧТО НУЖНО ПРОВЕРИТЬ

### 1. Проверить использование DateFormatterService

**Проверка:**
- Где вызывается `DateFormatterService.shared.formatExpirationDate()`?
- Вызывается ли он из background thread?
- Используется ли правильный `await MainActor.run`?

---

### 2. Проверить updateExpirationTextCache

**Проверка:**
- Где вызывается `updateExpirationTextCache()`?
- Вызывается ли он из background thread?
- Используется ли правильный `await MainActor.run` для форматирования?

---

### 3. Проверить использование Calendar.current

**Проверка:**
- Где еще используется `Calendar.current`?
- Используется ли он в `DateFormatter` или других местах?
- Может ли это вызвать рекурсию?

---

## 📋 ПЛАН ДЕЙСТВИЙ

### Этап 1: Немедленно (15 минут)

**Задача:** Найти источник рекурсии

**Действия:**
1. Проверить использование `DateFormatterService` в коде
2. Проверить, вызывается ли он из background thread
3. Проверить использование `Calendar.current` в коде
4. Найти место, где происходит рекурсия (адрес `0x104d8a080`)

---

### Этап 2: Исправить (20 минут)

**Задача:** Исправить рекурсию

**Действия:**
1. Убедиться, что `DateFormatterService` всегда вызывается с `await MainActor.run`
2. Убедиться, что все использования `Calendar.current` заменены на статический `Calendar`
3. Добавить защиту от рекурсии в `DateFormatterService`

---

## 🎯 НАЙДЕНА ПРИЧИНА КРАША!

### 🔴 КРИТИЧЕСКАЯ ПРОБЛЕМА: Старый код все еще используется!

**Проблема:**
- Мы создали `DateFormatterService` для предотвращения рекурсии
- НО в `updateExpirationTextCache` все еще используется **старый код** с `Self.displayFormatter`!
- Старый код может вызывать рекурсию, особенно при вызове из background thread

**Код проблемы (строки 1014-1029):**
```swift
// ❌ ПРОБЛЕМА: Используется старый код вместо DateFormatterService!
var parsedDate = Self.isoFormatter.date(from: isoString)  // Старый код
if parsedDate == nil {
    parsedDate = Self.isoFormatterFallback.date(from: isoString)  // Старый код
}
// ...
let formattedText = await MainActor.run {
    Self.displayFormatter.string(from: date)  // ❌ Старый код!
}
```

**Почему это вызывает рекурсию:**
1. `updateExpirationTextCache` вызывается из background thread (Thread 7)
2. Старый код использует `Self.displayFormatter` который может вызывать проблемы
3. Даже с `await MainActor.run` может быть проблема, если форматтер создан неправильно

---

## ✅ РЕШЕНИЕ

### Исправить updateExpirationTextCache - использовать DateFormatterService

**Нужно заменить:**
```swift
// БЫЛО (строки 1014-1029):
var parsedDate = Self.isoFormatter.date(from: isoString)
if parsedDate == nil {
    parsedDate = Self.isoFormatterFallback.date(from: isoString)
}
guard let date = parsedDate else { ... }
let formattedText = await MainActor.run {
    Self.displayFormatter.string(from: date)
}

// СТАЛО:
let formattedText = await MainActor.run {
    DateFormatterService.shared.formatExpirationDate(from: isoString)
}
```

---

## 🎯 ВЫВОДЫ

### Критические проблемы:

1. 🔴 **Старый код все еще используется** - `updateExpirationTextCache` не использует `DateFormatterService`
2. 🔴 **Рекурсия вернулась** - из-за использования старого кода
3. 🔴 **Краш в background thread** - `updateExpirationTextCache` вызывается из background thread

### Причина:

- Мы создали `DateFormatterService`, но забыли заменить старый код в `updateExpirationTextCache`
- Старый код может вызывать рекурсию при вызове из background thread

---

**Статус:** 🔴 **КРИТИЧЕСКАЯ ПРОБЛЕМА - НАЙДЕНА ПРИЧИНА**  
**Рекомендация:** Немедленно заменить старый код на `DateFormatterService` в `updateExpirationTextCache`
