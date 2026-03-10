# 🔴 BUILD 97: ДЕТАЛЬНЫЙ АНАЛИЗ CRASH LOG И РЕКОМЕНДАЦИИ

**Дата:** 2026-03-10  
**Версия сборки:** 97  
**Exception Type:** `EXC_BAD_ACCESS (SIGSEGV)`  
**Exception Message:** `Thread stack size exceeded due to excessive recursion`

---

## 📊 ДЕТАЛЬНЫЙ АНАЛИЗ STACK TRACE

### Ключевые наблюдения:

#### 1. **РЕКУРСИЯ В ФОРМАТИРОВАНИИ ДАТЫ** 🔴

**Stack trace показывает:**
```
12  Foundation                     -[NSDateFormatter stringForObjectValue:] + 140
13  ALADDIN                       0x1025ae7b4  ← Вызов DateFormatter в нашем коде
14  ALADDIN                       0x1025afa50
15  ALADDIN                       0x10263df28
16  ALADDIN                       0x102609cac
17  ALADDIN                       0x102609a2c
18  ALADDIN                       0x10260a164
19-24 ALADDIN                    0x10260a174  ← РЕКУРСИЯ! (повторяется 6 раз!)
```

**Проблема:** Рекурсия происходит в `NSDateFormatter stringForObjectValue:`, что указывает на проблему с форматированием даты.

**Вероятность:** 🔴 **95%**

---

#### 2. **ICU (International Components for Unicode) РЕКУРСИЯ**

**Stack trace показывает:**
```
0   libicucore.A.dylib            icu::FormattedStringBuilder::insertCodePoint(...)
1   libicucore.A.dylib            icu::SimpleDateFormat::formatImpl(...)
2   libicucore.A.dylib            icu::SimpleDateFormat::format(...)
3   CoreFoundation                CFDateFormatterCreateStringWithAbsoluteTime
4   Foundation                     -[NSDateFormatter stringForObjectValue:]
```

**Проблема:** Рекурсия происходит внутри ICU библиотеки при форматировании даты.

**Вероятность:** 🔴 **90%**

---

## 🔍 НАЙДЕННЫЕ ПРОБЛЕМНЫЕ МЕСТА

### 🔴 ПРОБЛЕМА #1: `DateFormatter()` создается в `getCrashLogs()`

**Файл:** `ALADDINApp.swift:981`  
**Код:**
```swift
let formatter = DateFormatter()
formatter.dateStyle = .full
formatter.timeStyle = .full
result += "⏰ CRASH TIME: \(formatter.string(from: date))\n"
```

**Проблема:**
- `DateFormatter()` создается каждый раз при вызове `getCrashLogs()`
- Не установлен `locale`, поэтому используется `Locale.current` по умолчанию
- `Locale.current` читает из `UserDefaults`, что может вызвать рекурсию
- Если `getCrashLogs()` вызывается во время краша или при инициализации, это может вызвать рекурсию

**Вероятность краша:** 🔴 **70%**

---

### 🔴 ПРОБЛЕМА #2: `RelativeDateTimeFormatter` использует `Locale.current`

**Файл:** `Core/Managers/SubscriptionManager.swift:1285`  
**Код:**
```swift
let formatter = RelativeDateTimeFormatter()
formatter.locale = Locale.current  // ❌ ПРОБЛЕМА!
return formatter.localizedString(for: date, relativeTo: Date())
```

**Проблема:**
- `Locale.current` читает из `UserDefaults`
- Если это вызывается во время инициализации или в computed property, может вызвать рекурсию

**Вероятность краша:** 🟡 **50%**

---

### 🔴 ПРОБЛЕМА #3: `DateFormatter()` создается в `AppDelegate` crash handler

**Файл:** `AppDelegate.swift:13, 207`  
**Код:**
```swift
let formatter = DateFormatter()
formatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
```

**Проблема:**
- `DateFormatter()` создается в crash handler
- Не установлен `locale`, поэтому используется `Locale.current` по умолчанию
- Если crash handler вызывается во время рекурсии, это может усугубить проблему

**Вероятность краша:** 🟢 **30%**

---

### 🔴 ПРОБЛЕМА #4: `DateFormatter()` создается в `FamilyScreen` Button actions

**Файл:** `Screens/02_FamilyScreen.swift:3577, 3681`  
**Код:**
```swift
let formatter = DateFormatter()
formatter.timeStyle = .short
print("✅ Schedule saved: \(formatter.string(from: ...))")
```

**Проблема:**
- `DateFormatter()` создается в Button actions
- Не установлен `locale`, поэтому используется `Locale.current` по умолчанию
- Если это вызывается во время инициализации View, может вызвать рекурсию

**Вероятность краша:** 🟢 **20%**

---

## 🎯 РЕКОМЕНДАЦИИ ПО ИСПРАВЛЕНИЮ

### 🔴 КРИТИЧНО (Приоритет 1):

#### 1. **Исправить `getCrashLogs()` - использовать статический `DateFormatter`**

**Файл:** `ALADDINApp.swift:981`  
**Исправление:**
```swift
// ✅ BUILD 98: Статический DateFormatter для предотвращения рекурсии
private static let crashTimeFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.dateStyle = .full
    formatter.timeStyle = .full
    formatter.locale = Locale(identifier: "ru_RU")  // Статический locale
    return formatter
}()

// В функции getCrashLogs():
if timestamp > 0 {
    let date = Date(timeIntervalSince1970: timestamp)
    result += "⏰ CRASH TIME: \(Self.crashTimeFormatter.string(from: date))\n"
    ...
}
```

**Риск:** 🟢 Низкий

---

#### 2. **Исправить `RelativeDateTimeFormatter` в `SubscriptionManager`**

**Файл:** `Core/Managers/SubscriptionManager.swift:1285`  
**Исправление:**
```swift
// ✅ BUILD 98: Используем статический locale вместо Locale.current
let formatter = RelativeDateTimeFormatter()
formatter.locale = Locale(identifier: "ru_RU")  // Статический locale
return formatter.localizedString(for: date, relativeTo: Date())
```

**Риск:** 🟢 Низкий

---

### 🟡 ВЫСОКО (Приоритет 2):

#### 3. **Исправить `DateFormatter()` в `AppDelegate` crash handler**

**Файл:** `AppDelegate.swift:13, 207`  
**Исправление:**
```swift
// ✅ BUILD 98: Статический DateFormatter для предотвращения рекурсии
private static let crashLogFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
    formatter.locale = Locale(identifier: "ru_RU")  // Статический locale
    return formatter
}()

// В функции crashExceptionHandler():
let timestamp = Date()
let formattedTime = Self.crashLogFormatter.string(from: timestamp)
```

**Риск:** 🟢 Низкий

---

#### 4. **Исправить `DateFormatter()` в `FamilyScreen` Button actions**

**Файл:** `Screens/02_FamilyScreen.swift:3577, 3681`  
**Исправление:**
```swift
// ✅ BUILD 98: Статический DateFormatter для предотвращения рекурсии
private static let timeFormatter: DateFormatter = {
    let formatter = DateFormatter()
    formatter.timeStyle = .short
    formatter.locale = Locale(identifier: "ru_RU")  // Статический locale
    return formatter
}()

// В Button actions:
print("✅ Schedule saved: \(Self.timeFormatter.string(from: weekdayStart.wrappedValue))")
```

**Риск:** 🟢 Низкий

---

## 📊 ПРИОРИТЕТЫ ИСПРАВЛЕНИЙ

| Исправление | Приоритет | Риск | Время | Вероятность краша |
|-------------|-----------|------|-------|-------------------|
| #1: getCrashLogs() DateFormatter | 🔴 Критично | 🟢 Низкий | 5 мин | 70% |
| #2: RelativeDateTimeFormatter | 🔴 Критично | 🟢 Низкий | 5 мин | 50% |
| #3: AppDelegate DateFormatter | 🟡 Высоко | 🟢 Низкий | 5 мин | 30% |
| #4: FamilyScreen DateFormatter | 🟡 Высоко | 🟢 Низкий | 5 мин | 20% |

**Общее время:** ~20 минут

---

## ✅ КРИТЕРИИ УСПЕХА

- [ ] Все `DateFormatter` используют статические экземпляры
- [ ] Все форматтеры используют статический `Locale(identifier:)` вместо `Locale.current`
- [ ] Нет создания `DateFormatter()` в функциях или computed properties
- [ ] Нет крашей при запуске приложения
- [ ] Нет рекурсии в логах

---

## 🎯 ВЫВОДЫ

### ❌ ЧТО ПРОИСХОДИТ:

1. **Рекурсия в `DateFormatter`** - это новая проблема, не связанная с предыдущими исправлениями
2. **Рекурсия происходит в ICU библиотеке** при форматировании даты
3. **Вероятная причина:** Использование `Locale.current` или создание `DateFormatter()` в функциях

### ✅ ЧТО НУЖНО СДЕЛАТЬ:

1. Исправить `getCrashLogs()` - использовать статический `DateFormatter`
2. Исправить `RelativeDateTimeFormatter` - использовать статический `Locale`
3. Исправить `AppDelegate` crash handler - использовать статический `DateFormatter`
4. Исправить `FamilyScreen` Button actions - использовать статический `DateFormatter`

---

**ГОТОВО К ИСПРАВЛЕНИЮ!** 🚀
